.ONESHELL:
.DEFAULT_GOAL: all

DEV=1
TAG=latest

all: install lint test cover
lint: isort black flake mypy

install:
	poetry install `if [ "${DEV}" = "0" ]; then echo "--no-dev"; fi`

isort:
	poetry run isort tezos_domains

black:
	poetry run black tezos_domains

flake:
	poetry run flakehell lint tezos_domains

mypy:
	poetry run mypy tezos_domains

cover:

build:
	poetry build

image:
	docker build . -t tezos-domains:${TAG}

up:
	docker-compose -f docker-compose.local.yml up -d db hasura

down:
	docker-compose -f docker-compose.local.yml down

clear:
	docker-compose -f docker-compose.local.yml down -v

run:
	poetry run dipdup -c dipdup.yml -c dipdup.local.yml run