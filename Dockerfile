FROM python:3.6-slim

RUN mkdir /usr/src/app
WORKDIR /usr/src/app
ADD ./requirements.txt .
ADD ./proxy_to_mongo.py .
ADD ./.env .

RUN pip install -r requirements.txt
ADD . /usr/src/app
CMD [ "python", "./proxy_to_mongo.py" ]
