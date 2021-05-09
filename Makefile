SHELL := /bin/bash
PWD := $(shell pwd)


default: build

all:

api:
	docker build -f ./api/Dockerfile -t "api:latest" .
.PHONY: api

blockchain:
	docker build -f ./blockchain/Dockerfile -t "blockchain:latest" .
.PHONY: blockchain

docker-image:
	docker build -f ./blockchain/Dockerfile -t "blockchain:latest" .
	docker build -f ./api/Dockerfile -t "api:latest" .
.PHONY: docker-image

docker-compose-up: docker-image
	docker-compose up -d --build
.PHONY: docker-compose-up

docker-compose-down:
	docker-compose stop -t 1
	docker-compose down
.PHONY: docker-compose-down

docker-compose-logs:
	docker-compose logs -f
.PHONY: docker-compose-logs
