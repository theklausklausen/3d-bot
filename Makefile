up:
	docker-compose -f docker-compose.yml up

down:
	docker-compose -f docker-compose.yml down

up-build:
	docker-compose -f docker-compose.yml up -d --build

dec_env:
	sops -d workspace.env.encrypted > workspace.env