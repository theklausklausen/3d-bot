up:
	docker-compose -f docker-compose.yml up

down:
	docker-compose -f docker-compose.yml down

up-build:
	docker-compose -f docker-compose.yml up -d --build

dec_env:
	sops -d workspace.env.encrypted > workspace.env

# run unittests from docker container
test:
	docker exec 3d-bot_3d-bot_1 ls -lah /app/tests
	docker exec 3d-bot_3d-bot_1 python -m unittest /app/