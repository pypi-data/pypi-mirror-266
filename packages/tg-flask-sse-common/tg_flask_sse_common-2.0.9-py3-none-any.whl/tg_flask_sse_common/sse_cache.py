#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from datetime import datetime


class SseOpenSwitchCache(object):
    """
    sse开关缓存
    """
    def __init__(self, redis_client, key_prefix):
        self.redis = redis_client
        self.prefix = key_prefix + ':sse:'

    def key(self):
        return self.prefix + 'open_switch'

    def set(self, status):
        self.redis.set(self.key(), status)

    def get(self):
        status = self.redis.get(self.key())
        if status is None:
            return 'open'

        if isinstance(status, bytes):
            status = status.decode('utf-8')

        return status


class SseConnectLockCache(object):
    """
    sse连接锁缓存
    """
    def __init__(self, redis_client, key_prefix):
        self.redis = redis_client
        self.prefix = key_prefix + ':sse:'

    def key(self, channel):
        return self.prefix + 'connect_lock:' + channel

    def try_lock(self, channel):
        res = self.redis.get(self.key(channel))
        if res is not None:
            return False

        ok = self.redis.setnx(self.key(channel), "1")
        self.redis.expire(self.key(channel), 5)
        return ok

    def release_lock(self, channel):
        self.redis.delete(self.key(channel))


class SseConnectStatsCache(object):
    """
    节点sse连接状态信息统计缓存
    用于统计每个节点下的所有channel-sse连接状态信息，用于查看节点下所有用户的连接状态
    info : {
        'channel': '122121',
        'connect_time': '2024-01-29 12:00:00',
        'extra': {},
    }
    """
    def __init__(self, redis_client, key_prefix):
        self.redis = redis_client
        self.prefix = key_prefix + ':sse:'
        self.expire = 60 * 60 * 48

    def key(self):
        tail = datetime.now().strftime('%Y%m%d')
        return self.prefix + 'connect_stats_info:' + tail

    def add(self, channel, info):
        info = json.dumps(info)
        self.redis.hset(self.key(), channel, info)
        self.redis.expire(self.key(), self.expire)

    def get(self, channel):
        data = self.redis.hget(self.key(), channel)
        if data is None:
            return {}

        if isinstance(data, bytes):
            data = data.decode('utf-8')

        return json.loads(data)

    def get_all_by_day(self, day):
        day_key = self.prefix + 'connect_stats_info:' + day
        datas = self.redis.hgetall(day_key)
        print({
            'title': 'sse-log',
            'msg': '获取连接情况统计数据',
            'key': day_key
        })
        result = {}
        if datas is None:
            return {}

        for channel, info in datas.items():
            if isinstance(channel, bytes):
                channel = channel.decode('utf-8')
            if isinstance(info, bytes):
                result[channel] = json.loads(info.decode('utf-8'))

        return result

    def delete(self, channel):
        self.redis.hdel(self.key(), channel)


class SseEventMessageCache(object):
    """
    sse消息缓存
    """
    def __init__(self, redis_client, key_prefix):
        self.redis = redis_client
        self.prefix = key_prefix + ':sse:'
        self.expire = 60 * 60 * 48

    def pub_key(self):
        tail = datetime.now().strftime('%Y%m%d')
        return self.prefix + 'pub_event_message:' + tail

    def sub_key(self):
        tail = datetime.now().strftime('%Y%m%d')
        return self.prefix + 'sub_event_message:' + tail

    def add_pub_message(self, message):
        message = json.dumps(message)
        self.redis.lpush(self.pub_key(), message)
        self.redis.expire(self.pub_key(), self.expire)

    def add_sub_message(self, message):
        message = json.dumps(message)
        self.redis.lpush(self.sub_key(), message)
        self.redis.expire(self.sub_key(), self.expire)

    def get_pub_all_by_day(self, day, start=0, end=100):
        day_key = self.prefix + 'pub_event_message:' + day
        print({
            'title': 'sse-log',
            'msg': '获取推送消息统计数据',
            'key': day_key,
            'start': start,
            'end': end
        })
        message = self.redis.lrange(day_key, start, end)
        result = list()
        if message is None:
            return []

        for i in range(len(message)):
            if isinstance(message[i], bytes):
                result.append(
                    json.loads(message[i].decode('utf-8'))
                )

        return result

    def get_sub_all_by_day(self, day, start=0, end=100):
        day_key = self.prefix + 'sub_event_message:' + day
        print({
            'title': 'sse-log',
            'msg': '获取接收消息统计数据',
            'key': day_key,
            'start': start,
            'end': end
        })
        result = list()
        message = self.redis.lrange(day_key, start, end)
        if message is None:
            return []

        for i in range(len(message)):
            if isinstance(message[i], bytes):
                result.append(
                    json.loads(message[i].decode('utf-8'))
                )

        return result
