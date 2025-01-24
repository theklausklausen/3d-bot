up:
	docker-compose -f docker-compose.yml up

down:
	docker-compose -f docker-compose.yml down

up-build:
	docker-compose -f docker-compose.yml up -d --build

dec_env:
	sops -d workspace.env.encrypted > workspace.env

encrypt:
	@echo "Encrypting ${f} to $$(echo ${f} | sed 's/\.yml/\.enc.yml/g' | sed 's/\.yaml/\.enc.yaml/g')"
	sops --encrypt --encrypted-suffix='secretTemplates' ${f} > $$(echo '${f}' | sed 's/\.yml/\.enc.yml/g' | sed 's/\.yaml/\.enc.yaml/g')

decrypt:
	@echo "Decrypting ${f} to $$(echo ${f} | sed 's/\.enc.yml/\.yml/g' | sed 's/\.enc.yaml/\.yaml/g')"
	sops --decrypt --unencrypted-suffix='secretTemplates' ${f} > $$(echo ${f} | sed 's/\.enc.yml/\.yml/g' | sed 's/\.enc.yaml/\.yaml/g')