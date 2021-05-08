SHELL := /bin/bash
PWD := $(shell pwd)


default: build

all:

miners_handler:
	docker build -f ./miners_handler/Dockerfile -t "miners_handler:latest" .
.PHONY: miners_handler

blockchain:
	docker build -f ./blockchain/Dockerfile -t "blockchain:latest" .
.PHONY: miners_handler

docker-image:
	docker build -f ./blockchain/Dockerfile -t "blockchain:latest" .
	docker build -f ./miners_handler/Dockerfile -t "miners_handler:latest" .
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
