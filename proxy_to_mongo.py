#!/usr/bin/env python3.6

# https://github.com/constverum/ProxyBroker

import asyncio
from proxybroker import Broker, ProxyPool
from pymongo import MongoClient
from datetime import datetime
from var_dump import var_dump


async def show(proxies):
    while True:
        proxy = await proxies.get()
        if proxy is None: break
        print('Found proxy: %s' % proxy)


async def save(proxies, collection):
    while True:
        proxy = await proxies.get()
        if proxy is None:
            break
        # Found proxy: <Proxy FR 0.27s [HTTP: High] 163.172.28.22:80>
        print('Found proxy: %s' % proxy)
        #var_dump(proxy)
        # proto = 'https' if 'HTTPS' in proxy.types else 'http'
        # row = '%s://%s:%d\n' % (proto, proxy.host, proxy.port)
        HostPort = '%s:%d' % (proxy.host, proxy.port)

        now = datetime.utcnow()

        key = {'HostPort': HostPort}
        data = {
            "$setOnInsert": {
                'HostPort': HostPort,
                'lvl': proxy.types,
                'countries': proxy.geo.code,
                'avg_resp_time': proxy.avg_resp_time,
                'insertion_date': now,
            },
            "$set": {
                'last_update_date': now
            }
        }
        #print(data)
        collection.update_one(key, data, upsert=True)


def main():
    client = MongoClient('mongodb://test1:passwd@192.168.1.7:27017/')
    db = client['tvh5']
    collection = db['proxy']

    #  Отключаем прокси у которых только отказы
    query = {
        'bad': {'$gte': 5},
        '$or': [{'good': 0},{'good':{'$exists':False}}]
    }
    update = {'$set': {'status': 0}}

    result = collection.update_many(query, update)
    proxy_count = result.matched_count
    proxy_mod = result.modified_count
    print('Update status to "0" proxy: %s in %s' % (proxy_mod, proxy_count))


    index_name = 'HostPort'
    if index_name not in collection.index_information():
        collection.create_index(index_name, unique=True)

    loop = asyncio.get_event_loop()

    proxies = asyncio.Queue(loop=loop)
    proxy_pool = ProxyPool(proxies)
    codes = [200, 301, 302]

    judges = ['http://httpbin.org/get?show_env',
              'https://httpbin.org/get?show_env'
              ]

    broker = Broker(
        proxies, timeout=8, max_conn=200, max_tries=3, verify_ssl=True, judges=judges, loop=loop,

    )



    tasks = asyncio.gather(
        #broker.find(types=['HTTP', 'HTTPS','SOCKS5'], limit=100),
        broker.find(types=[('HTTP', ('Anonymous', 'High'))], limit=400),
        save(proxies, collection)
    )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(tasks)


if __name__ == '__main__':
    main()

