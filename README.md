# Blockbuster Premiere Rush - Observabilidade B3 (Cenario 2)



Sistema de Autorizacao de Streaming de Alta Performance desenvolvido em Python (FastAPI), instrumentado com OpenTelemetry e integrado a stack completa de observabilidade LGTM (Loki, Grafana, Tempo, Prometheus).



---



## Arquitetura e Componentes da Solucao



1. Backend FastAPI (/stream/authorize): Gateway de autorizacao com engine de decisao dinamica de qualidade (4K, 1080p, 720p) baseada em nivel de carga e resiliencia sob picos de tráfego.

2. Instrumentacao OpenTelemetry & RED: Coleta nativa de métricas de Rate (RPS), Errors (Taxa de Erros) e Duration (Latencia p95), com expostas via endpoint /metrics no formato Prometheus.

3. Centralizacao de Logs e Tracing: Emissão de logs estruturados em formato JSON com injecao automatica de trace_id e span_id para rastreabilidade ponta a ponta no Loki e no Tempo.

4. Simulador Frontend SRE & Chaos Engineering: Interface web construida para inspecao de metadados, controle de tráfego simulado e injecao de falhas controladas (HTTP 500) para testes de resiliencia.

5. Containerizacao e Orquestracao: Ambiente totalmente containerizado via Docker Compose utilizando a imagem oficial grafana/otel-lgtm e gerador de carga grafana/k6.



---



## Requisitos de Ambiente



- Git

- Docker (versao 20.10+)

- Docker Compose (versao 2.0+)

- Make (opcional, para uso dos comandos facilitados)



---



## Passo a Passo de Execucao (Do GitHub a Aplicacao Rodando)



### Passo 1: Obter o Codigo Fonte



Abra o terminal e execute os comandos abaixo para clonar o seu fork do repositorio e acessar o diretorio raiz da aplicacao:



git clone https://github.com/seu-usuario/blockbuster-premiere-rush.git

cd blockbuster-premiere-rush



### Passo 2: Executar a Aplicacao



A aplicacao pode ser iniciada via Docker Compose padrao ou via Makefile.



Opcao A: Via Docker Compose (Padrao Oficial do Desafio)



Na raiz do projeto, execute o comando de orquestracao:



docker compose up --build -d



Este comando vai construir a imagem da API FastAPI, baixar a imagem oficial grafana/otel-lgtm, subir a suite de testes de carga do k6 e integrar os coletores.



Para checar o status de execucao dos containers:



docker compose ps



Para acompanhar os logs do sistema em tempo real:



docker compose logs -f api



Opcao B: Via Makefile



Se optar pelo uso de atalhos automatizados:



make up          # Constroi as imagens e sobe os servicos em background

make ps          # Inspeciona o estado dos containers

make logs        # Acompanha a saida dos logs da aplicacao

make down        # Encerra e remove os containers do ambiente



---



## Como Validar e Testar o Sistema



### 1. Teste de Endpoint via Terminal (Backend Isolado)



Para realizar uma requisicao direta de autorizacao de streaming via curl:



curl -i "http://localhost:8080/stream/authorize?user_id=usr_99823&movie_id=mov_escape_earth"



Resposta de Sucesso Esperada (HTTP 200 OK):



{

  "user_id": "usr_99823",

  "movie_id": "mov_escape_earth",

  "authorized": true,

  "resolution": "4K",

  "drm_token": "eyJhbGciOiJIUzI1NiIsInR5c...",

  "server_region": "sa-east-1",

  "status": "ok",

  "load_level": "low",

  "concurrent_requests": 1,

  "requests_per_second": 2.0,

  "rush_active": false,

  "error_mode": false

}



### 2. Inspeção de Metricas Prometheus



Para verificar a exposicao oficial das metricas no modelo RED:



curl -s http://localhost:8080/metrics



### 3. Validação pelo Dashboard do Grafana (Stack LGTM)



1. Acesse a interface do Grafana em: http://localhost:3000

2. As credenciais padrao sao: admin / admin (com acesso anonimo configurado para visualizacao).

3. Navegue ate o painel pre-provisionado "Blockbuster Premiere Rush - Metricas RED" (carregado via dashboard.json na raiz do projeto).

4. O painel apresenta em tempo real:

   - RPS (Requisições por Segundo): Calculado via irate para evitar atrasos na amostragem.

   - Taxa de Erros: Monitoramento instantaneo de falhas HTTP 500.

   - Totalizador Absoluto de Erros: Utilizando increase e formatado como numero inteiro (0 casas decimais).

   - Latencia p95: Percentil 95 da duracao das requisicoes.



### 4. Validacao de Logs (Loki) e Traces (Tempo) no Grafana



1. No menu lateral do Grafana (http://localhost:3000), clique em "Explore".

2. No seletor de fonte de dados no topo da pagina:

   - Selecione "Loki" para consultar os logs em formato JSON da aplicacao e filtrar pelo trace_id.

   - Selecione "Tempo" para consultar os spans distribuídos das requisicoes HTTP recebidas pelo OpenTelemetry Collector (porta 4317).



### 5. Validacao via Interface SRE e Simulador de Caos



Acesse a interface web no seu navegador:

http://localhost:8080



Recursos disponiveis na interface:

- Botao Play: Dispara autorizacoes unitarias com medicao de latencia no cliente.

- Rush Limpo: Simula o pico de acessos do lancamento sem injecao de erros.

- Rush c/ Erros (Chaos Mode): Ativa o gerador de erros controlados (HTTP 500) para avaliar o comportamento do painel de observabilidade sob instabilidade.

- Telemetria de Tela: Exibe os contadores de requisições enviadas, totalizador de erros 500 e a distribuicao de qualidade por resolucao (4K, 1080p, 720p).



---



## Procedimento para Encerramento do Ambiente



Para interromper os containers e limpar a rede virtual criada pelo Docker:

Via Docker Compose:

docker compose down -v

Via Makefile:

make down