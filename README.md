# Blockbuster Premiere Rush - Observabilidade B3 (Cenário 2)



Sistema de Autorização de Streaming de Alta Performance desenvolvido em Python (FastAPI), instrumentado com OpenTelemetry e integrado à stack completa de observabilidade LGTM (Loki, Grafana, Tempo, Prometheus).



---



## 1. Arquitetura e Componentes da Solução



1. **Backend FastAPI (`/stream/authorize`):** Gateway de autorização com engine de decisão dinâmica de qualidade (4K, 1080p, 720p) baseada em nível de carga e resiliência sob picos de tráfego.

2. **Instrumentação OpenTelemetry & RED:** Coleta nativa de métricas de Rate (RPS), Errors (Taxa de Erros) e Duration (Latência p95), expostas via endpoint `/metrics` no formato Prometheus.

3. **Centralização de Logs e Tracing:** Emissão de logs estruturados em formato JSON com injeção automática de `trace_id` e `span_id` para rastreabilidade ponta a ponta no Loki e no Tempo.

4. **Simulador Frontend SRE & Chaos Engineering:** Interface web construída para inspeção de metadados, controle de tráfego simulado e injeção de falhas controladas (HTTP 500) para testes de resiliência.

5. **Containerização e Orquestração:** Ambiente totalmente containerizado via Docker Compose utilizando a imagem oficial `grafana/otel-lgtm` e gerador de carga `grafana/k6`.



---



## 2. Entendendo os Dashboards de Observabilidade (Stack LGTM)



### 2.1 Acesso ao Grafana e Credenciais

Para aceder ao explorador e aos dashboards do Grafana (`http://localhost:3000`), utilize as credenciais padrão de autenticação:

- **Usuário:** `admin`

- **Senha:** `admin`



### 2.2 Métrica RED & Painéis do Grafana

O dashboard pré-provisionado (**"Blockbuster Premiere Rush - Métricas RED"**) permite analisar a saúde da aplicação em tempo real:



- **RPS - Requisições por Segundo (Rate):** Mede o volume de tráfego que chega ao gateway `/stream/authorize`. Utiliza `irate` para garantir leitura instantânea e sem atrasos no gráfico.

- **Taxa de Erros (Errors):** Exibe a proporção instantânea de respostas HTTP 500 geradas no sistema.

- **Total de Erros Absoluto (Stat Panel):** Contador quantitativo de erros acumulados no período selecionado. Utiliza a função `increase` calibrada com a variável `$__range` e arredondamento estrito de inteiros (0 casas decimais) para bater exatamente com a contagem real do backend.

- **Latência p95 (Duration):** Exibe o tempo de resposta em milissegundos para 95% das requisições autorizadas, mostrando como a degradação graciosa de qualidade (4K → 1080p → 720p) previne lentidões excessivas.



> ⚠️ **Nota de Propagação de Dados:** Os dados e gráficos de volumetria nos dashboards do Grafana podem demorar alguns segundos (ou um breve ciclo de atualização) para refletir as métricas após o início do tráfego ou dos testes de carga.



### 2.3 Ajustes de Visualização no Grafana

- **Seletor de Tempo (Time Range):** No canto superior direito da tela do Grafana, clique no ícone de relógio para definir a janela de visualização (ex: `Last 5 minutes` ou `Last 15 minutes`).

- **Auto-Refresh:** Selecione a atualização automática para `5s` para acompanhar picos de tráfego e injeção de falhas ao vivo.



### 2.4 Guia Prático de Consultas no Loki e no Tempo



Para realizar investigações avançadas e correlacionar eventos no menu **Explore** do Grafana, utilize os seguintes exemplos de queries:



#### A. Consultas no Loki (LogQL)

Para inspecionar logs estruturados em JSON, filtrar por nível de erro ou rastrear um identificador único de rastreio (`trace_id`):



- **Puxar todos os logs estruturados da aplicação:**

  ```logql

  {container="blockbuster-api"} | json | logger="blockbuster-premiere-rush"

  ```



- **Filtrar apenas logs que registraram erros HTTP 500:**

  ```logql

  {container="blockbuster-api"} | json | level="ERROR"

  ```



- **Investigar um `trace_id` específico capturado nos logs:**

  ```logql

  {container="blockbuster-api"} |= "0585d4ca7d8adedb457fe18dc4a8b776"

  ```



#### B. Consultas no Tempo (TraceQL)

Para rastrear o fluxo distribuído e a latência das requisições:



- **Filtrar todos os rastreios do serviço da aplicação:**

  ```traceql

  { resource.service.name = "blockbuster-premiere-rush" }

  ```



- **Investigar um Trace ID específico diretamente no Tempo:**

  Basta colar o identificador (ex: `0585d4ca7d8adedb457fe18dc4a8b776`) diretamente na aba de busca por **Trace ID** no painel do Tempo.



---



## 3. Cenários de Teste da Aplicação



### 3.1 Teste Unitário

Valida o comportamento individual do gateway `/stream/authorize` respondendo com HTTP 200 OK, metadados de carga, token DRM e definição da qualidade inicial.



### 3.2 Cenário de Carga Sem Erro (Rush Limpo)

Simula o pico de acessos durante o lançamento de uma grande estreia. O gateway recebe alta demanda e ativa a degradação dinâmica de resoluções de mídia para manter o sistema estável sem gerar falhas 500.



### 3.3 Cenário de Carga Com Erro (Modo Caos / Chaos Engineering)

Simula instabilidade na infraestrutura ou dependências externas através da injeção controlada de falhas HTTP 500. **Atenção:** É obrigatório garantir que o modo de erro esteja ativo no backend (`error-start`) antes de disparar a carga com o k6 para que os erros sejam injetados corretamente. Permite validar os alertas do Grafana, a contagem absoluta de erros e o rastreamento de exceções nos logs do Loki.



---



## 4. Requisitos de Ambiente



- Git

- Docker (versão 20.10+)

- Docker Compose (versão 2.0+)

- Make (opcional)



---



## 5. Passo a Passo de Execução: Opção A - Docker (Padrão Oficial)



### 1. Clonar o Repositório

```bash

git clone https://github.com/anahysales/desafio-observabilidade-b3.git

cd desafio-observabilidade-b3

```



### 2. Iniciar a Aplicação e a Stack LGTM

*(Dica: Utilize a flag `--remove-orphans` para evitar conflitos de containers antigos ou órfãos de execuções anteriores)*

```bash

docker compose up --build -d --remove-orphans

```



### 3. Verificar Status dos Containers

```bash

docker compose ps

```



### 4. Acompanhar Logs da API em Tempo Real

```bash

docker compose logs -f api

```



### 5. Executar os Cenários de Teste via Terminal



#### A. Teste Unitário (Requisição Pontual)

```bash

curl -i "http://localhost:8080/stream/authorize?user_id=usr_99823&movie_id=mov_escape_earth"

```



#### B. Cenário de Carga Sem Erros (Rush Limpo + k6)

```bash

# Ativa o modo Rush Limpo

curl -X POST http://localhost:8080/rush/start



# Dispara o teste de carga concorrente do k6

docker compose run --rm k6-load-test run /load.js

```



#### C. Cenário de Carga Com Erros (Modo Caos + k6)

*(Importante: O modo de erro deve estar ativo antes do k6 iniciar os disparos)*

```bash

# Ativa manualmente a injeção de falhas 500

curl -X POST http://localhost:8080/rush/error-start



# Dispara o teste de carga sob falhas

docker compose run --rm -e ERROR_MODE=true k6-load-test

```



#### D. Parar Simulações de Rush/Caos

```bash

curl -X POST http://localhost:8080/rush/stop

```



### 6. Encerrar e Limpar o Ambiente

```bash

docker compose down -v

```



---



## 6. Passo a Passo de Execução: Opção B - Makefile (Atalhos Automatizados)



### 1. Clonar o Repositório

```bash

git clone https://github.com/anahysales/desafio-observabilidade-b3.git

cd desafio-observabilidade-b3

```



### 2. Iniciar o Ambiente

```bash

make up

```



### 3. Verificar Status dos Containers

```bash

make ps

```



### 4. Acompanhar Logs da API

```bash

make logs

```



### 5. Executar os Cenários de Teste via Terminal



#### A. Teste Unitário

```bash

make test-unit

```



#### B. Cenário de Carga Sem Erros (Rush Limpo + k6)

```bash

make test-rush

```



#### C. Cenário de Carga Com Erros (Modo Caos + k6)

```bash

make test-chaos

```



#### D. Controlo Manual do Modo Caos (Erros)

```bash

# Ativa manualmente o modo caos/erros

make error-start



# Desativa manualmente o modo caos/erros

make error-stop

```



#### E. Parar Simulações de Rush/Caos

```bash

make test-stop

```



### 6. Encerrar e Limpar o Ambiente

```bash

make down

```



---



## 7. Links de Acesso Rápido com o Ambiente Ativo



- **Simulador Frontend SRE:** `http://localhost:8080`

- **Dashboard Grafana (Métricas RED):** `http://localhost:3000` *(Login: `admin` / `admin`)*

- **Métricas Prometheus Expostas:** `http://localhost:8080/metrics`

- **Prometheus UI:** `http://localhost:9090`