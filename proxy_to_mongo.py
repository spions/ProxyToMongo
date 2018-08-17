#!/usr/bin/env python3.6

# https://github.com/constverum/ProxyBroker

import asyncio
import requests
import os
import signal
from proxybroker import Broker, ProxyPool
from pymongo import MongoClient
from datetime import datetime
from var_dump import var_dump
from dotenv import load_dotenv, find_dotenv



def handler(signum, frame):
    print ("Exit (ctr+c)")
    exit(1)

def fetch2(url, server):
    proxyDict = {"https": server}
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5 (.NET CLR 3.5.30729)'}
    try:
        r = requests.get(url, headers=headers, proxies=proxyDict)
        status = r.status_code
        if status is 200:
            return status
        else:
            return False
    except Exception:
        return False


async def show(proxies):
    while True:
        proxy = await proxies.get()
        if proxy is None: break
        print('Found proxy: %s' % proxy)


async def save(proxies, collection):
    while True:

        signal.signal(signal.SIGINT, handler)

        proxy = await proxies.get()
        if proxy is None:
            break
        # Found proxy: <Proxy FR 0.27s [HTTP: High] 163.172.28.22:80>
        print('Found proxy: %s' % proxy)
        # var_dump(proxy)
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
        # print(data)
        if fetch2('https://httpbin.org/get?show_env', HostPort) == 200:
            collection.update_one(key, data, upsert=True)
        else:
            print('Proxy: %s not support https' % HostPort)


def main():
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    load_dotenv(find_dotenv())

    MONGODB_ADDRESS = os.getenv("MONGODB_ADDRESS")
    DB = os.getenv("DB")
    COLLECTION = os.getenv("COLLECTION")
    LIMIT_PROXY = os.getenv("LIMIT_PROXY")

    print("%s: Start search proxy servers..." % start_time)
    client = MongoClient(MONGODB_ADDRESS)
    db = client[DB]
    collection = db[COLLECTION]

    #  Отключаем прокси у которых только отказы
    query = {
        'bad': {'$gte': 5},
        '$or': [{'good': 0}, {'good': {'$exists': False}}]
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
        broker.find(types=[('HTTP', ('Anonymous', 'High'))], limit=LIMIT_PROXY),
        save(proxies, collection)
    )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(tasks)
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("%s: End search proxy servers." % end_time)
    print('Duration: {}'.format(end_time - start_time))

if __name__ == '__main__':
    main()
