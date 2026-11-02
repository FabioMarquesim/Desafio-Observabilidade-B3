.PHONY: help build up down restart logs ps rush-start rush-stop test-k6 clean

# Variáveis
DC = docker-compose

help: ## Exibe os comandos disponíveis
	@echo "Uso: make [comando]"
	@echo ""
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Compila/recompila a imagem do backend e serviços
	$(DC) build

up: ## Sobe todo o ambiente em segundo plano (detached)
	$(DC) up -d --remove-orphans

down: ## Para e remove todos os contêineres e redes
	$(DC) down

restart: ## Reinicia o ambiente recompilando as alterações (down + build + up)
	$(DC) down
	$(DC) build
	$(DC) up -d --remove-orphans

logs: ## Exibe os logs em tempo real da API
	$(DC) logs -f api

ps: ## Lista o status dos contêineres
	$(DC) ps

test-k6: ## Dispara o teste de carga do k6 via Docker
	$(DC) run --rm k6 run /scripts/load.js

rush-start: ## Dispara a chamada para iniciar o Rush no backend
	curl -X POST http://localhost:8080/rush/start

rush-stop: ## Dispara a chamada para parar o Rush no backend
	curl -X POST http://localhost:8080/rush/stop

clean: ## Limpa contêineres e volumes parados
	$(DC) down -v --remove-orphans