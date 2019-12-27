#!/usr/bin/env python
# coding=utf-8
import nsq


def test():
    result = dict()
    result.update({'status': 1, 'message': 'success', 'data': ['1', '2', '3']})
    print(result)
    return True


if __name__ == '__main__':
    r = nsq.Reader(message_handler=test,
                   nsqd_tcp_addresses=['127.0.0.1:4150'],
                   topic='test_topic',
                   channel='test',
                   lookupd_poll_interval=15)
    nsq.run()