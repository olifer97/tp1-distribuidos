SHELL := /bin/bash
PWD := $(shell pwd)


default: build

all:

miner:
	docker build -f ./miner/Dockerfile -t "miner:latest" .
.PHONY: miner
