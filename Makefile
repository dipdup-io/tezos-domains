.ONESHELL:

up:
	docker-compose -f docker-compose.local.yml up -d --build

down:
	docker-compose -f docker-compose.local.yml down -v