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

up: docker-image
	docker-compose up -d --build
.PHONY: up

down:
	docker-compose stop -t 1
	docker-compose down
.PHONY: down

logs:
	docker-compose logs -f
.PHONY: logs
