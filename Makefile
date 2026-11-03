.PHONY: help build up down restart logs ps test-k6 rush-start rush-stop test-unit test-rush test-chaos test-stop clean error-start error-stop

# Variáveis (utilizando o docker-compose compatível com o seu sistema)
DC = docker-compose

help: ## Exibe os comandos disponíveis
	@echo "Uso: make [comando]"
	@echo ""
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Compila/recompila a imagem do backend e serviços
	$(DC) build

up: ## Sobe todo o ambiente em segundo plano (detached) limpando órfãos
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

test-k6: ## Dispara o teste de carga padrão do k6 via Docker
	$(DC) run --rm k6-load-test run /load.js

rush-start: ## Dispara a chamada para iniciar o Rush no backend
	curl -X POST http://localhost:8080/rush/start

rush-stop: ## Dispara a chamada para parar o Rush no backend
	curl -X POST http://localhost:8080/rush/stop

# ==============================================================================
# COMANDOS DE TESTE DOS CENÁRIOS (UNITÁRIO, CARGA E CAOS)
# ==============================================================================

test-unit: ## Executa o teste unitário da API com JSON formatado
	@echo "=== Executando Teste Unitário (API) ==="
	curl -s "http://localhost:8080/stream/authorize?user_id=usr_99823&movie_id=mov_escape_earth" | json_pp

test-rush: ## Executa o Cenário de Carga Sem Erro (Ativa Rush Limpo + k6)
	@echo "=== Ativando Modo Rush Limpo na API ==="
	curl -X POST http://localhost:8080/rush/start
	@echo "\n=== Disparando Teste de Carga (k6) ==="
	$(DC) run --rm k6-load-test run /load.js

test-chaos: ## Executa o Cenário de Carga com Erro (Ativa Modo Caos HTTP 500 + k6)
	@echo "=== Ativando Modo Caos / Injeção de Erros na API ==="
	curl -X POST http://localhost:8080/rush/error-start
	@echo "\n=== Disparando Teste de Carga sob Falha (k6) ==="
	$(DC) run --rm -e ERROR_MODE=true k6-load-test run /load.js

test-stop: ## Para qualquer simulação ativa de Rush/Caos e normaliza a API
	@echo "=== Parando Modo Rush e Retornando a API ao Normal ==="
	curl -X POST http://localhost:8080/rush/stop

clean: ## Limpa contêineres e volumes parados (incluindo órfãos)
	$(DC) down -v --remove-orphans

error-start: ## Ativa manualmente o modo caos/erros no backend
	curl -X POST http://localhost:8080/rush/error-start

error-stop: ## Desativa manualmente o modo caos/erros no backend
	curl -X POST http://localhost:8080/rush/stop