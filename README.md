ProxyToMongo
=====================

ProxyToMongo is an open source tool that asynchronously 
finds public proxies (only https) from multiple sources, concurrently 
checks them and save to MongoDB. 

Based on https://github.com/constverum/ProxyBroker

## Installation

    cp .env-dist .env
    vi .env  
    make build

## Usage

Run containers  
  
    make run

Show status containers

    make status

Stop containers

    make stop
    
## Deploying to Heroku

```
$ heroku create
$ git push heroku master
$ heroku open
```
or

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)