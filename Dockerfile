FROM python:3.6-slim
ADD proxy_to_mongo.py /
RUN pip install proxybroker pymongo datetime var_dump
CMD [ "python", "./proxy_to_mongo.py" ]
