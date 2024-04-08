#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import time

from .sse_constant import SseClientConfig, SseSystemEventType, SseListenRsp
from .sse_message import SseMessageField, SseMessage


class SseClients(object):
    """
    用于全局保存sse连接对象
    背景 : 因为在每个sse长连接中，每次创建redis-pub-sub监听会耗cpu的操作，所以redis-pub-sub需要全局创建，
          如果全局创建redis-pub-sub，就无法区分不同的sse连接，也就无法对不同的sse连接进行操作，
          所以需要一个全局保存sse连接对象的地方
    原理 : 原理类似websocket的全局socket对象机制，每个连接都保存在了全局socket对象中，通过socket_id进行访问
          主要考虑连接建立时，连接断开时，连接异常时的处理，同时提供定时任务清理无效连接
    连接建立 : 保存连接对象
    连接断开 : 删除连接对象
    连接异常 : 删除连接对象
    """

    class Field(object):
        """
        sse全局连接对象字段
        """
        CLIENT_ID = 'client_id'
        MESSAGE_LIST = 'message_list'
        CONNECT_TIME = 'connect_time'
        LATER_RELEASE = 'later_release'
        RELEASE_REASON = 'release_reason'

    def __init__(self, sse_clients_config, redis_pub_sub_config):
        self.is_running = False
        self.sse_global_clients = {}

        # 控制连接最大时间，超过时间超过定时任务清理
        max_connect_time = sse_clients_config['max_connect_time'] or SseClientConfig.MAX_CONNECT_TIME
        max_connect_count = sse_clients_config['max_connect_count'] or SseClientConfig.MAX_CONNECT_COUNT
        listen_interval = sse_clients_config['listen_interval'] or SseClientConfig.LISTEN_INTERVAL
        local_node_id = sse_clients_config['local_node_id'] or SseClientConfig.LOCAL_NODE_ID
        message_retry_time = sse_clients_config['message_retry_time'] or SseClientConfig.MESSAGE_RETRY_TIME

        self.max_connect_time = max_connect_time
        self.max_connect_count = max_connect_count
        self.listen_interval = listen_interval
        self.local_node_id = local_node_id
        self.message_retry_time = message_retry_time

    def get_local_node_id(self):
        return self.local_node_id

    def get_channel_sse_count(self, channel):
        """
        获取指定频道下的连接数
        :param channel: 频道id
        """
        sse_connect_list = self.sse_global_clients.get(channel)
        if not sse_connect_list:
            return 0
        return len(sse_connect_list)

    def count(self):
        return len(self.sse_global_clients.keys())

    def connect(self, channel):
        """
        添加连接对象，请求建立sse连接时调用
        :param channel: 连接id
        """
        if not channel:
            return False, "channel is empty", ""

        if self.count() > self.max_connect_count:
            return False, "connect count is max", ""

        channel = str(channel)

        sse_connect_list = self.sse_global_clients.get(channel)
        if not sse_connect_list:
            sse_connect_list = list()

        # 将之前的连接全部设置稍后关闭, 关闭原因为 - 同一节点重复连接
        for sse_connect in sse_connect_list:
            sse_connect.update({
                self.Field.LATER_RELEASE: True,
                self.Field.RELEASE_REASON: SseListenRsp.REPEAT_CONNECT
            })

        # 添加新的连接
        client_id = channel + '_' + str(int(time.time() * 1000000))
        sse_connect_list.append({
            self.Field.CLIENT_ID: client_id,
            self.Field.MESSAGE_LIST: [],
            self.Field.CONNECT_TIME: datetime.now(),
            self.Field.LATER_RELEASE: False,
        })

        self.sse_global_clients[channel] = sse_connect_list

        return True, "ok", client_id

    def release_sse(self, channel):
        """
        移除待释放连接对象
        :param channel: 连接id
        """
        # 移除待释放连接对象
        release_connect_list = list()
        release_channel_list = list()

        sse_connect_list = self.sse_global_clients.get(channel)
        if not sse_connect_list:
            sse_connect_list = []

        for index, sse_connect in enumerate(sse_connect_list):
            if sse_connect.get(self.Field.LATER_RELEASE):
                release_connect_list.append(index)

        # 清理记录的待释放连接
        for index in release_connect_list:
            if index >= len(sse_connect_list):
                continue
            sse_connect_list.pop(index)

        # 清理记录的频道
        if len(sse_connect_list) == 0:
            self.sse_global_clients.pop(channel)
            release_channel_list.append(channel)

        if len(release_connect_list) > 0 or len(release_channel_list) > 0:
            print({
                'title': 'sse-log',
                'msg': '移除待释放连接/频道',
                'ln_id': self.local_node_id,
                'channel': channel,
                'release_connect_list': release_connect_list,
                'release_channel_list': release_channel_list,
                'channel_connect_count': len(sse_connect_list),
                'channel_count': self.count(),
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })

    def release_timeout_sse(self):
        """
        移除超时连接对象
        """
        release_channel_list = list()

        for channel in list(self.sse_global_clients.keys()):
            release_connect_list = list()

            sse_connect_list = self.sse_global_clients.get(channel)
            if not sse_connect_list:
                continue

            for index, sse_connect in enumerate(list(sse_connect_list)):
                if not sse_connect:
                    continue
                connect_time = sse_connect.get(self.Field.CONNECT_TIME, datetime.now())
                if (datetime.now() - connect_time).seconds > self.max_connect_time:
                    release_connect_list.append(index)

            # 清理记录的超时连接
            if len(release_connect_list) > 0:
                for index in release_connect_list:
                    if index >= len(sse_connect_list):
                        continue
                    sse_connect_list.pop(index)
                print({
                    'title': 'sse-log',
                    'msg': '移除超时连接',
                    'ln_id': self.local_node_id,
                    'channel': channel,
                    'release_connect_list': release_connect_list,
                    'channel_connect_count': len(sse_connect_list),
                    'channel_count': self.count(),
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                })

            if len(sse_connect_list) == 0:
                release_channel_list.append(channel)

        # 清理记录的频道
        if len(release_channel_list) > 0:
            for channel in release_channel_list:
                self.sse_global_clients.pop(channel)
            print({
                'title': 'sse-log',
                'msg': '移除超时频道',
                'ln_id': self.local_node_id,
                'release_channel_list': release_channel_list,
                'channel_count': self.count(),
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })

    def release_message_accumulate_sse(self):
        """
        移除消息堆积过多的连接对象
        """
        release_channel_list = list()

        for channel in list(self.sse_global_clients.keys()):
            release_connect_list = list()

            sse_connect_list = self.sse_global_clients.get(channel)
            if not sse_connect_list:
                continue

            for index, sse_connect in enumerate(list(sse_connect_list)):
                if not sse_connect:
                    continue

                message_list = sse_connect.get(self.Field.MESSAGE_LIST, [])
                if len(message_list) > 200:
                    release_connect_list.append(index)

            # 清理记录的消息堆积过多连接
            if len(release_connect_list) > 0:
                for index in release_connect_list:
                    if index >= len(sse_connect_list):
                        continue
                    sse_connect_list.pop(index)
                print({
                    'title': 'sse-log',
                    'msg': '移除消息堆积过多连接',
                    'ln_id': self.local_node_id,
                    'channel': channel,
                    'release_connect_list': release_connect_list,
                    'channel_connect_count': len(sse_connect_list),
                    'channel_count': self.count(),
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                })

            if len(sse_connect_list) == 0:
                release_channel_list.append(channel)

        # 清理记录的频道
        if len(release_channel_list) > 0:
            for channel in release_channel_list:
                self.sse_global_clients.pop(channel)
            print({
                'title': 'sse-log',
                'msg': '移除消息堆积过多频道',
                'ln_id': self.local_node_id,
                'release_channel_list': release_channel_list,
                'channel_count': self.count(),
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })

    def disconnect_sse(self, channel, client_id):
        """
        监听到推送消息异常后，可以判断客户端是断开连接
        需注意 :
            这个事件的触发是非实时，所以在执行清理的时候，sse_connect_list中可能存在多个连接对象
        :param channel: 连接id
        :param client_id: 客户端id
        """
        change_state_count = 0

        sse_connect_list = self.sse_global_clients.get(channel)
        if not sse_connect_list:
            return

        for sse_connect in sse_connect_list:
            if not sse_connect:
                continue

            if sse_connect.get(self.Field.CLIENT_ID) == client_id:
                sse_connect.update({
                    self.Field.LATER_RELEASE: True,
                    self.Field.RELEASE_REASON: SseListenRsp.CLIENT_DISCONNECT
                })
                change_state_count += 1

        self.release_sse(channel=channel)

        print({
            'title': 'sse-log',
            'msg': '客户端断开连接-设置标识位',
            'channel': channel,
            'client_id': client_id,
            'change_state_count': change_state_count,
            'channel_connect_count': len(sse_connect_list),
            'channel_count': self.count()
        })

    def release_all(self):
        """
        清理所有连接对象
        """
        self.sse_global_clients.clear()

    def add_message(self, channel, message):
        """
        添加消息到连接对象，监听到redis-pub-sub消息时调用
        :param channel: 连接id
        :param message: 消息
        """
        sse_connect_list = self.sse_global_clients.get(channel)
        if not sse_connect_list:
            sse_connect_list = []

        for sse_connect in sse_connect_list:
            if not sse_connect:
                continue

            message_list = sse_connect.get(self.Field.MESSAGE_LIST, [])
            message_list.append(message)
            sse_connect.update({
                self.Field.MESSAGE_LIST: message_list,
            })

        self.sse_global_clients[channel] = sse_connect_list

    def add_heartbeat(self):
        """
        添加心跳消息到连接对象
        """
        # 问题:
        # 因为flask是无法主动监听到连接是否关闭的(或者说客户端关闭事件，flask是不会向上抛出异常)，所以需要定时发送心跳包
        # 一旦客户端关闭连接，就会收不到心跳包（yield报错），这时候协程将断开连接，while将直接退出，设置LATER_RELEASE=true。
        #
        # 1. 每次心跳包时，将清理已经关闭的连接对象
        # 2. 每次心跳包时，将清理超时连接对象 (额外兜底)
        # 3. 每次心跳包时，将检测消息堆积过多的对象 (额外兜底)
        try:
            self.release_timeout_sse()

            for channel in list(self.sse_global_clients.keys()):
                self.release_sse(channel=channel)

            self.release_message_accumulate_sse()
        except:
            pass

        # 移除完失效连接后，往有效连接中添加心跳消息
        for channel in self.sse_global_clients.keys():
            self.add_message(
                channel=channel,
                message=SseMessage(
                    channel=channel,
                    data=SseSystemEventType.HEARTBEAT,
                    event=SseSystemEventType.HEARTBEAT,
                    _id=str(int(datetime.now().timestamp() * 1000000)),
                    retry=self.message_retry_time
                )
            )

    def listen_message(self, channel):
        """
        监听消息
        """
        latest_sse_connect = None

        sse_connect_list = self.sse_global_clients.get(channel)
        if not sse_connect_list:
            sse_connect_list = []

        for sse_connect in sse_connect_list:
            if not sse_connect:
                continue
            if sse_connect.get(self.Field.LATER_RELEASE):
                continue

            latest_sse_connect = sse_connect
            break

        if not latest_sse_connect:
            print({
                'title': 'sse-log',
                'msg': '当前连接全部等待关闭中，请重新连接',
                'channel': channel,
                'channel_connect_count': len(sse_connect_list),
                'ln_id': self.local_node_id,
                'channel_count': self.count(),
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })

            self.release_sse(channel=channel)
            yield SseMessage(
                channel=channel,
                data=SseSystemEventType.ALL_DISCONNECT,
                event=SseSystemEventType.ALL_DISCONNECT,
                _id=str(int(datetime.now().timestamp() * 1000000)),
                retry=self.message_retry_time,
            ), None
            return

        message_list = latest_sse_connect.get(self.Field.MESSAGE_LIST, [])
        connect_time = latest_sse_connect.get(self.Field.CONNECT_TIME, datetime.now())
        client_id = latest_sse_connect.get(self.Field.CLIENT_ID, '')

        # 退出原因
        run_rsp = SseListenRsp.TIMEOUT_CONNECT
        run_rsp_message = SseMessage(
            channel=channel,
            data=SseSystemEventType.TIMEOUT_CONNECT,
            event=SseSystemEventType.TIMEOUT_CONNECT,
            _id=str(int(datetime.now().timestamp() * 1000000)),
            retry=self.message_retry_time,
        )

        # 最大超时范围内，轮训消息
        while (datetime.now() - connect_time).seconds < self.max_connect_time:
            if latest_sse_connect.get(self.Field.LATER_RELEASE):
                run_rsp = latest_sse_connect.get(self.Field.RELEASE_REASON)
                break

            if not message_list:
                time.sleep(self.listen_interval)
                continue

            message = message_list.pop(0)
            if not message:
                time.sleep(self.listen_interval)
                continue

            message_dict = message.to_dict()
            event = message_dict.get(SseMessageField.EVENT, '')

            if event == SseSystemEventType.END:
                run_rsp = SseListenRsp.END_CONNECT
                break

            if event == SseSystemEventType.CONNECT:
                data = message_dict.get(SseMessageField.DATA, {})
                if data and isinstance(data, dict):
                    if data.get('ln_id', '') != self.local_node_id:
                        run_rsp = SseListenRsp.D_REPEAT_CONNECT
                        break

            yield message, client_id
            time.sleep(self.listen_interval)

        # 1. 其他节点重复连接 - 关闭全部连接，此情况需要当前节点调用unsubscribe取消频道订阅
        # 2. 主动结束连接 - 关闭全部连接
        # 3. 超时连接 - 关闭全部连接
        # 4. 同一节点重复连接 - 无需操作，因为在连接建立时设置了关闭标志位
        if run_rsp in [
            SseListenRsp.D_REPEAT_CONNECT, SseListenRsp.END_CONNECT, SseListenRsp.TIMEOUT_CONNECT
        ]:
            for sse_connect in sse_connect_list:
                sse_connect.update({
                    self.Field.LATER_RELEASE: True,
                    self.Field.RELEASE_REASON: run_rsp
                })

        if run_rsp == SseListenRsp.TIMEOUT_CONNECT:
            print({
                'title': 'sse-log',
                'msg': '连接超时-关闭轮训',
                'channel': channel,
                'connect_time': datetime.strftime(connect_time, '%Y-%m-%d %H:%M:%S'),
                'channel_connect_count': len(sse_connect_list),
                'ln_id': self.local_node_id,
                'client_id': client_id,
                'channel_count': self.count(),
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })
            run_rsp_message = SseMessage(
                channel=channel,
                data=SseSystemEventType.TIMEOUT_CONNECT,
                event=SseSystemEventType.TIMEOUT_CONNECT,
                _id=str(int(datetime.now().timestamp() * 1000000)),
                retry=self.message_retry_time
            )
        elif run_rsp == SseListenRsp.REPEAT_CONNECT:
            print({
                'title': 'sse-log',
                'msg': '收到同一节点重复channel连接-关闭轮训',
                'channel': channel,
                'connect_time': datetime.strftime(connect_time, '%Y-%m-%d %H:%M:%S'),
                'channel_connect_count': len(sse_connect_list),
                'ln_id': self.local_node_id,
                'client_id': client_id,
                'channel_count': self.count(),
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })
            run_rsp_message = SseMessage(
                channel=channel,
                data=SseSystemEventType.REPEAT_CONNECT,
                event=SseSystemEventType.REPEAT_CONNECT,
                _id=str(int(datetime.now().timestamp() * 1000000)),
                retry=self.message_retry_time
            )
        elif run_rsp == SseListenRsp.D_REPEAT_CONNECT:
            print({
                'title': 'sse-log',
                'msg': '收到其他节点重复channel连接-关闭轮训',
                'channel': channel,
                'connect_time': datetime.strftime(connect_time, '%Y-%m-%d %H:%M:%S'),
                'channel_connect_count': len(sse_connect_list),
                'ln_id': self.local_node_id,
                'client_id': client_id,
                'channel_count': self.count(),
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })
            run_rsp_message = SseMessage(
                channel=channel,
                data=SseSystemEventType.D_REPEAT_CONNECT,
                event=SseSystemEventType.D_REPEAT_CONNECT,
                _id=str(int(datetime.now().timestamp() * 1000000)),
                retry=self.message_retry_time
            )
        elif run_rsp == SseListenRsp.END_CONNECT:
            print({
                'title': 'sse-log',
                'msg': '收到结束消息-关闭轮训',
                'channel': channel,
                'connect_time': datetime.strftime(connect_time, '%Y-%m-%d %H:%M:%S'),
                'channel_connect_count': len(sse_connect_list),
                'channel_count': self.count(),
                'ln_id': self.local_node_id,
                'client_id': client_id,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })
            run_rsp_message = SseMessage(
                channel=channel,
                data=SseSystemEventType.END,
                event=SseSystemEventType.END,
                _id=str(int(datetime.now().timestamp() * 1000000)),
                retry=self.message_retry_time
            )

        # 释放连接
        self.release_sse(channel=channel)

        # 返回对应的结束消息
        yield run_rsp_message, client_id

        return

