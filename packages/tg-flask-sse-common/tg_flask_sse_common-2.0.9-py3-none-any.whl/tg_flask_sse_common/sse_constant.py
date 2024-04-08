#!/usr/bin/env python
# -*- coding: utf-8 -*-
class RedisPubSubField(object):
    """
    redis pubsub消息字段
    """
    TYPE = 'type'
    DATA = 'data'
    PATTERN = 'pattern'

    class Type(object):
        """
        redis pubsub消息类型
        """
        MESSAGE = 'message'
        P_MESSAGE = 'pmessage'
        SUBSCRIBE = 'subscribe'
        UNSUBSCRIBE = 'unsubscribe'
        P_SUBSCRIBE = 'psubscribe'
        P_UNSUBSCRIBE = 'punsubscribe'


class SseMessageField(object):
    """
    sse消息字段
    """
    ID = "id"
    DATA = "data"
    EVENT = "event"
    RETRY = "retry"
    CHANNEL = 'channel'
    CLIENT_ID = 'client_id'


class SseSystemEventType(object):
    """
    sse系统内置消息事件类型定义
    """
    # 结束连接消息事件
    END = "END"
    # 错误消息事件
    ERROR = "ERROR"
    # redis消息事件
    REDIS = "REDIS"
    # 连接消息事件
    CONNECT = "CONNECT"
    # 尝试连接
    TRY_CONNECT = "TRY_CONNECT"
    # 心跳
    HEARTBEAT = "HEARTBEAT"
    # 全部断开
    ALL_DISCONNECT = 'ALL_DISCONNECT'
    # 超时连接
    TIMEOUT_CONNECT = 'TIMEOUT_CONNECT'
    # 主动结束连接
    END_CONNECT = 'END_CONNECT'
    # 单个节点重复连接
    REPEAT_CONNECT = 'REPEAT_CONNECT'
    # 分布式其他节点重复连接
    D_REPEAT_CONNECT = 'D_REPEAT_CONNECT'


class SseListenRsp(object):
    # 全部断开
    ALL_DISCONNECT = 'ALL_DISCONNECT'
    # 超时连接
    TIMEOUT_CONNECT = 'TIMEOUT_CONNECT'
    # 消息主动结束连接
    END_CONNECT = 'END_CONNECT'
    # 客户端主动断开连接
    CLIENT_DISCONNECT = 'CLIENT_DISCONNECT'
    # 单个节点重复连接
    REPEAT_CONNECT = 'REPEAT_CONNECT'
    # 分布式其他节点重复连接
    D_REPEAT_CONNECT = 'D_REPEAT_CONNECT'


class RedisConfig(object):
    HOST = '127.0.0.1'
    PORT = 6379
    DB = 0
    PASSWORD = ''
    KEY_PREFIX = ''


class SseClientConfig(object):
    # 连接最大时长
    MAX_CONNECT_TIME = 600
    # 单进程最大连接数
    MAX_CONNECT_COUNT = 2000
    # 连接监听消息-轮训时间间隔
    LISTEN_INTERVAL = 1
    # 当前节点id
    LOCAL_NODE_ID = '127.0.0.1'
    # 消息retry时间
    MESSAGE_RETRY_TIME = 60 * 1000


class RedisPubSubConfig(object):
    # pub-sub监听-轮训时间间隔
    LISTEN_INTERVAL = 0.01
    # 心跳间隔
    HEARTBEAT_INTERVAL = 20
