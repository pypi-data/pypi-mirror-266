#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from datetime import datetime

from .sse_constant import RedisConfig, SseSystemEventType, SseClientConfig
from .sse_clients import SseClients
from .sse_redis_pub_sub import SseRedisPubSub


class Sse(object):
    def __init__(self, redis_config, sse_clients_config, redis_pub_sub_config):
        host = redis_config['host'] or RedisConfig.HOST
        port = redis_config['port'] or RedisConfig.PORT
        password = redis_config['password'] or RedisConfig.PASSWORD
        db = redis_config['db'] or RedisConfig.DB
        key_prefix = redis_config['key_prefix'] or RedisConfig.KEY_PREFIX

        # 初始化sse连接对象
        sse_clients = SseClients(
            sse_clients_config=sse_clients_config,
            redis_pub_sub_config=redis_pub_sub_config
        )
        self.sse_clients = sse_clients

        # 初始化redis-pub-sub对象
        self.sse_redis_pub_sub = SseRedisPubSub(
            host=host, port=port, password=password, db=db, key_prefix=key_prefix,
            sse_clients_config=sse_clients_config,
            sse_clients=sse_clients, redis_pub_sub_config=redis_pub_sub_config
        )

        self.message_retry_time = sse_clients_config['message_retry_time'] or SseClientConfig.MESSAGE_RETRY_TIME

    def connect(self, channel, extra=None):
        """
        添加连接对象, 并订阅sse消息, 添加信息到redis订阅频道
        订阅后，推送一条带节点ip地址的消息，通知非当前ip地址节点的连接进行断开
        :param channel: 频道id
        :param extra: 额外信息
        """
        is_open_switch = self.sse_redis_pub_sub.is_open_sse_switch()
        if not is_open_switch:
            return False, "sse switch is close", ""

        return self.sse_redis_pub_sub.subscribe_channel(channel=channel, extra=extra)

    def listen(self):
        """
        开启sse消息监听redis-频道，服务启动时调用
        """
        if not self.sse_clients.is_running:
            self.sse_clients.is_running = True
            self.sse_redis_pub_sub.listen()

    def default_generator(self, channel):
        """
        订阅消息，监听内存中的消息队列
        """
        try:
            for message, client_id in self.sse_clients.listen_message(channel):
                # 消息非法
                if not message:
                    continue

                # 其他节点重复连接消息，取消当前节点订阅
                if message.event == SseSystemEventType.D_REPEAT_CONNECT:
                    self.sse_redis_pub_sub.unsubscribe_channel(channel)

                try:
                    yield message.to_rsp_str()
                except:
                    self.sse_clients.disconnect_sse(channel=channel, client_id=client_id)
                    pass
        except:
            print({
                'title': 'sse-log',
                'msg': '客户端断开连接',
                'channel': channel
            })
            pass

    def publish_business_message(self, channel, event, data, _id=None, retry=None):
        """
        推送sse业务消息, 添加信息到redis频道
        """
        if event in [
            SseSystemEventType.END, SseSystemEventType.ERROR,
            SseSystemEventType.REDIS, SseSystemEventType.CONNECT
        ]:
            print("sse-log-business event type error, can not use system event type")
            return 0

        return self.sse_redis_pub_sub.publish_message(
            channel=channel,
            data=data,
            event=event,
            _id=_id,
            retry=retry
        )

    def publish_end_message(self, channel):
        """
        推送sse-end系统消息, 添加信息到redis频道
        """
        return self.sse_redis_pub_sub.publish_message(
            channel=channel,
            data=SseSystemEventType.END,
            event=SseSystemEventType.END,
            _id=str(int(datetime.now().timestamp() * 1000000)),
            retry=self.message_retry_time
        )

    def open_sse(self):
        """
        开启sse服务
        """
        self.sse_redis_pub_sub.open_sse_switch()

    def close_sse(self):
        """
        关闭sse服务
        """
        self.sse_redis_pub_sub.close_sse_switch()

    def sse_run(self):
        """
        开启后台线程监听sse消息，服务启动时调用
        """
        thread = threading.Thread(target=self.listen)
        thread.start()

    def sse_stop(self):
        """
        停止后台sse消息监听线程，服务停止时调用
        """
        self.sse_clients.is_running = False
        return self.sse_redis_pub_sub.disconnect_all()

    def get_stat(self, stat_type, day, start=0, end=100):
        """
        获取相对应的统计数据
        """
        if stat_type == 'connect':
            return self.sse_redis_pub_sub.get_connect_stat(day)
        elif stat_type == 'pub_message':
            return self.sse_redis_pub_sub.get_pub_message_stat(day, start, end)
        elif stat_type == 'sub_message':
            return self.sse_redis_pub_sub.get_sub_message_stat(day, start, end)
        else:
            return []

