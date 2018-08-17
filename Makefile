help:
	@echo "Please use make <target> where <target> is one of the following:"
	@echo "  start       Runs Docker instance"
	@echo "  stop        Stop Docker instance"
	@echo "  status      Status Docker instance"
	@echo "  build       Build  Docker instance"

build:
	docker build -t python-proxy-to-mongo .

start:
	#docker run python-proxy-to-mongo
	docker-compose up -d

stop:
	#docker stop python-proxy-to-mongo
	docker-compose stop

status:
	docker-compose ps

