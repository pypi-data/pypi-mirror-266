#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from datetime import datetime
import traceback
import time

import redis

from .sse_cache import SseConnectStatsCache, SseEventMessageCache, SseOpenSwitchCache, SseConnectLockCache
from .sse_constant import RedisPubSubField, SseSystemEventType
from .sse_message import SseMessage, SseMessageField
from .sse_constant import RedisPubSubConfig, SseClientConfig


class SseRedisPubSub(object):
    """
    全局redis-pub-sub对象
    """
    def __init__(
            self, key_prefix, host, port, password, db,
            sse_clients, sse_clients_config, redis_pub_sub_config
    ):
        # 初始化redis连接
        new_redis_client = redis.StrictRedis(
            host=host,
            port=port,
            password=password,
            db=db,
        )

        self.redis_client = new_redis_client
        self.redis_pubsub_client = new_redis_client.pubsub(
            ignore_subscribe_messages=True
        )
        self.sse_connect_stats_cache = SseConnectStatsCache(
            redis_client=new_redis_client, key_prefix=key_prefix
        )
        self.sse_event_message_cache = SseEventMessageCache(
            redis_client=new_redis_client, key_prefix=key_prefix
        )
        self.sse_open_switch_cache = SseOpenSwitchCache(
            redis_client=new_redis_client, key_prefix=key_prefix
        )
        self.sse_connect_lock_cache = SseConnectLockCache(
            redis_client=new_redis_client, key_prefix=key_prefix
        )

        message_retry_time = sse_clients_config['message_retry_time'] or SseClientConfig.MESSAGE_RETRY_TIME

        listen_interval = redis_pub_sub_config['listen_interval'] or RedisPubSubConfig.LISTEN_INTERVAL
        heartbeat_interval = redis_pub_sub_config['heartbeat_interval'] or RedisPubSubConfig.HEARTBEAT_INTERVAL

        self.listen_interval = listen_interval
        self.heartbeat_interval = heartbeat_interval
        self.message_retry_time = message_retry_time
        self.previous_heartbeat_time = int(time.time())
        self.sse_clients = sse_clients

    def listen(self):
        """
        监听redis订阅频道，将收到的消息推送到全局sse连接对象
        """
        print({
            'title': 'sse-log',
            'msg': '开启监听redis频道',
            'channel_count': self.sse_clients.count()
        })

        while True:
            if not self.sse_clients.is_running:
                print({
                    'title': 'sse-log',
                    'msg': '监听redis频道线程停止',
                    'channel_count': self.sse_clients.count()
                })
                break

            try:
                # 所有连接推送心跳包
                cur_time = int(time.time())
                if cur_time - self.previous_heartbeat_time > self.heartbeat_interval:
                    self.sse_clients.add_heartbeat()
                    self.previous_heartbeat_time = cur_time

                    # 如果关闭开关时，停止线程
                    if not self.is_open_sse_switch():
                        self.disconnect_all()
                        print({
                            'title': 'sse-log',
                            'msg': '监听redis频道线程停止-开关关闭',
                            'channel_count': self.sse_clients.count()
                        })
                        break

                sub_message = self.redis_pubsub_client.get_message()
                if not sub_message:
                    time.sleep(self.listen_interval)
                    continue

                channel, message = self.redis_pub_sub_event_message_handler(sub_message)
                if not message:
                    time.sleep(self.listen_interval)
                    continue

                if self.is_message_need_cache(message):
                    # 缓存消息
                    self.sse_event_message_cache.add_sub_message({
                        'channel': channel,
                        'message': message.to_dict(),
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    })

                if self.is_message_need_push(message):
                    # 消息推送到全局sse连接对象
                    self.sse_clients.add_message(channel, message)

                time.sleep(self.listen_interval)

            except:
                print({
                    'title': 'sse-log',
                    'msg': '监听redis频道异常',
                    'exp': traceback.format_exc(),
                    'channel_count': self.sse_clients.count()
                })
                time.sleep(self.listen_interval)

    def subscribe_channel(self, channel, extra=None):
        """
        订阅sse频道消息
        :param channel: 频道
        :param extra: 额外信息
        """
        try:
            # 加锁限制同一个频道并发连接
            if not self.sse_connect_lock_cache.try_lock(channel):
                return False, "connect lock, please retry", ""

            self.redis_pubsub_client.subscribe(channel)

            ok, msg, client_id = self.sse_clients.connect(channel)
            if not ok:
                print({
                    'title': 'sse-log',
                    'msg': '订阅失败-连接失败',
                    'channel': channel,
                    'msg1': msg,
                    'client_id': client_id,
                    'channel_count': self.sse_clients.count(),
                    'ln_id': self.sse_clients.get_local_node_id(),
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                })
                self.redis_pubsub_client.unsubscribe(channel)
                return ok, msg, ""

            # 连接成功，记录连接信息
            self.sse_connect_stats_cache.add(channel, {
                'connect_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ln_id': self.sse_clients.get_local_node_id(),
                'client_id': client_id,
                'extra': extra,
            })

            # 推送连接消息到当前节点
            self.sse_clients.add_message(
                channel, SseMessage(
                    channel=channel,
                    data={
                        'msg': 'try connect',
                        'client_id': client_id,
                        'ln_id': self.sse_clients.get_local_node_id()
                    },
                    event=SseSystemEventType.TRY_CONNECT,
                    _id=str(int(datetime.now().timestamp() * 1000000)),
                    retry=self.message_retry_time,
                )
            )

            # 推送连接消息到其他节点
            push_count = self.publish_message(
                channel=channel,
                data={
                    'msg': 'connect success',
                    'client_id': client_id,
                    'ln_id': self.sse_clients.get_local_node_id()
                },
                event=SseSystemEventType.CONNECT,
                _id=str(int(datetime.now().timestamp() * 1000000)),
                retry=self.message_retry_time,
                client_id=client_id
            )

            print({
                'title': 'sse-log',
                'msg': '订阅成功' if push_count > 0 else '订阅失败-频道不存在',
                'channel': channel,
                'channel_count': self.sse_clients.count(),
                'ln_id': self.sse_clients.get_local_node_id(),
                'client_id': client_id,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })

            return ok, msg, client_id
        except:
            print({
                'title': 'sse-log',
                'msg': '订阅异常',
                'exp': traceback.format_exc(),
                'channel': channel,
                'channel_count': self.sse_clients.count(),
                'ln_id': self.sse_clients.get_local_node_id(),
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })
            return False, "subscribe error, please retry", ""

    def publish_message(self, channel, data, event=None, _id=None, retry=None, client_id=None):
        """
        推送sse消息, 添加信息到redis发布队列记录
        :param channel: 频道
        :param data: 数据
        :param event: 事件
        :param _id: 消息id
        :param retry: 重试时间
        :param client_id: 客户端id
        """
        try:
            message = SseMessage(
                channel=channel, data=data, event=event, _id=_id, retry=retry
            ).to_dict()

            push_count = self.redis_client.publish(channel=channel, message=json.dumps(message))

            self.sse_event_message_cache.add_pub_message({
                'channel': channel,
                'message': message,
                'push_count': push_count,
                'ln_id': self.sse_clients.get_local_node_id(),
                'client_id': client_id,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })

            if push_count > 0:
                print({
                    'title': 'sse-log',
                    'msg': '消息推送成功',
                    'channel': channel,
                    'event': event,
                    'push_count': push_count,
                    'channel_count': self.sse_clients.count(),
                    'ln_id': self.sse_clients.get_local_node_id(),
                    'client_id': client_id,
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                })
            else:
                print({
                    'title': 'sse-log',
                    'msg': '消息推送失败-频道不存在',
                    'channel': channel,
                    'event': event,
                    'channel_count': self.sse_clients.count(),
                    'ln_id': self.sse_clients.get_local_node_id(),
                    'client_id': client_id,
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                })

            return push_count
        except:
            print({
                'title': 'sse-log',
                'msg': '消息推送异常',
                'exp': traceback.format_exc(),
                'channel': channel,
                'event': event,
                'channel_count': self.sse_clients.count(),
                'ln_id': self.sse_clients.get_local_node_id(),
                'client_id': client_id,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })
            return 0

    def unsubscribe_channel(self, channel):
        """
        取消订阅sse频道
        :param channel: 频道
        """
        print({
            'title': 'sse-log',
            'msg': '取消订阅',
            'channel': channel,
            'channel_count': self.sse_clients.count(),
            'ln_id': self.sse_clients.get_local_node_id(),
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        })
        self.redis_pubsub_client.unsubscribe(channel)

    def disconnect_all(self):
        """
        断开所有sse连接，关闭服务时调用
        """
        channel_list = self.sse_clients.sse_global_clients.keys()
        if channel_list:
            # 清理全局连接对象
            self.sse_clients.release_all()

    def get_pub_message_stat(self, day=datetime.now().strftime('%Y%m%d'), start=0, end=100):
        """
        获取指定日期推送消息统计
        :param day: 日期
        :param start: 开始
        :param end: 结束
        """
        return self.sse_event_message_cache.get_pub_all_by_day(day, start, end)

    def get_sub_message_stat(self, day=datetime.now().strftime('%Y%m%d'), start=0, end=100):
        """
        获取指定日期接收消息统计
        :param day: 日期
        :param start: 开始
        :param end: 结束
        """
        return self.sse_event_message_cache.get_sub_all_by_day(day, start, end)

    def get_connect_stat(self, day=datetime.now().strftime('%Y%m%d')):
        """
        某天连接统计
        :param day: 日期
        """
        return self.sse_connect_stats_cache.get_all_by_day(day)

    def is_open_sse_switch(self):
        """
        sse开关
        """
        status = self.sse_open_switch_cache.get()
        return status == 'open'

    def open_sse_switch(self):
        return self.sse_open_switch_cache.set("open")

    def close_sse_switch(self):
        return self.sse_open_switch_cache.set("close")

    @staticmethod
    def is_message_need_push(message):
        """
        该消息是否可以推送给用户
        """
        if not message:
            return False
        if not isinstance(message, SseMessage):
            return False
        event = message.to_dict().get(SseMessageField.EVENT, '')
        return event not in [
            SseSystemEventType.ERROR, SseSystemEventType.REDIS,
        ]

    @staticmethod
    def is_message_need_cache(message):
        """
        该消息是否需要缓存
        """
        if not message:
            return False
        if not isinstance(message, SseMessage):
            return False
        event = message.to_dict().get(SseMessageField.EVENT, '')
        return event not in [
            SseSystemEventType.ERROR, SseSystemEventType.REDIS, SseSystemEventType.HEARTBEAT
        ]

    @staticmethod
    def redis_pub_sub_event_message_handler(sub_message):
        """
        redis消息类型处理
        :param sub_message: redis订阅消息

        :return:
            message: sse消息
            brk: 是否中断结束
        """
        try:
            if not sub_message:
                return SseSystemEventType.ERROR, None

            # 需要先解码
            for key, value in sub_message.items():
                if isinstance(key, bytes):
                    key = key.decode('utf-8')
                if isinstance(value, bytes):
                    value = value.decode('utf-8')
                sub_message[key] = value

            channel = sub_message.get(SseMessageField.CHANNEL)
            if not channel:
                return SseSystemEventType.ERROR, None

            # 非message类型不处理
            if sub_message[RedisPubSubField.TYPE] != RedisPubSubField.Type.MESSAGE:
                return SseSystemEventType.REDIS, None

            sub_message_data = sub_message.get(RedisPubSubField.DATA, '')
            if not sub_message_data:
                return SseSystemEventType.ERROR, None

            # 消息
            sse_message = json.loads(sub_message_data)
            message = SseMessage(
                channel=sse_message.get(SseMessageField.CHANNEL),
                data=sse_message.get(SseMessageField.DATA),
                event=sse_message.get(SseMessageField.EVENT),
                _id=sse_message.get(SseMessageField.ID),
                retry=sse_message.get(SseMessageField.RETRY)
            )

            return channel, message
        except:
            return SseSystemEventType.ERROR, None


