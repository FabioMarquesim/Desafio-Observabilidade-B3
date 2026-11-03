Blockbuster Premiere Rush - Observabilidade B3 (Cenário 2)

Sistema de Autorização de Streaming de Alta Performance desenvolvido em Python (FastAPI), instrumentado com OpenTelemetry e integrado à stack completa de observabilidade LGTM (Loki, Grafana, Tempo, Prometheus).

1. Arquitetura e Componentes da Solução

Backend FastAPI (/stream/authorize): Gateway de autorização com engine de decisão dinâmica de qualidade (4K, 1080p, 720p) baseada em nível de carga e resiliência sob picos de tráfego.

Instrumentação OpenTelemetry & RED: Coleta nativa de métricas de Rate (RPS), Errors (Taxa de Erros) e Duration (Latência p95), expostas via endpoint /metrics no formato Prometheus.

Centralização de Logs e Tracing: Emissão de logs estruturados em formato JSON com injeção automática de trace_id e span_id para rastreabilidade ponta a ponta no Loki e no Tempo.

Simulador Frontend SRE & Chaos Engineering: Interface web construída para inspeção de metadados, controle de tráfego simulado e injeção de falhas controladas (HTTP 500) para testes de resiliência.

Containerização e Orquestração: Ambiente totalmente containerizado via Docker Compose utilizando a imagem oficial grafana/otel-lgtm e gerador de carga grafana/k6.

2. Entendendo os Dashboards de Observabilidade (Stack LGTM)

2.1 Métrica RED & Painéis do Grafana

O dashboard pré-provisionado ("Blockbuster Premiere Rush - Métricas RED") permite analisar a saúde da aplicação em tempo real:

RPS - Requisições por Segundo (Rate): Mede o volume de tráfego que chega ao gateway /stream/authorize. Utiliza irate para garantir leitura instantânea e sem atrasos no gráfico.

Taxa de Erros (Errors): Exibe a proporção instantânea de respostas HTTP 500 geradas no sistema.

Total de Erros Absoluto (Stat Panel): Contador quantitativo de erros acumulados no período selecionado. Utiliza a função increase calibrada com a variável $__range e arredondamento estrito de inteiros (0 casas decimais) para bater exatamente com a contagem real do backend.

Latência p95 (Duration): Exibe o tempo de resposta em milissegundos para 95% das requisições autorizadas, mostrando como a degradação graciosa de qualidade (4K → 1080p → 720p) previne lentidões excessivas.

2.2 Ajustes de Visualização no Grafana

Seletor de Tempo (Time Range): No canto superior direito da tela do Grafana (http://localhost:3000), clique no ícone de relógio para definir a janela de visualização (ex: Last 5 minutes ou Last 15 minutes).

Auto-Refresh: Selecione a atualização automática para 5s para acompanhar picos de tráfego e injeção de falhas ao vivo.

2.3 Logs (Loki) e Traces (Tempo)

Loki: Acesse o menu Explore no Grafana e selecione a fonte Loki para consultar os logs JSON da aplicação e filtrar eventos por trace_id.

Query LogQL para puxar todos os logs com erro (HTTP 500):

{job="blockbuster-api"} |= "500"


Tempo: Na fonte Tempo, inspecione os spans de tempo distribuídos de cada requisição capturada pelo OpenTelemetry Collector.

2.4 Validação Direta no Prometheus

Acesse http://localhost:9090 e vá em Status > Targets para confirmar se o Prometheus está raspando ativamente o target da API (blockbuster-api).

PromQL Principal (Taxa de Requisições por Endpoint/Método):

sum(irate(http_requests_total[5s])) by (endpoint, method)


3. Cenários de Teste da Aplicação

3.1 Teste Unitário

Valida o comportamento individual do gateway /stream/authorize respondendo com HTTP 200 OK, metadados de carga, token DRM e definição da qualidade inicial.

3.2 Cenário de Carga Sem Erro (Rush Limpo)

Simula o pico de acessos durante o lançamento de uma grande estreia. O gateway recebe alta demanda e ativa a degradação dinâmica de resoluções de mídia para manter o sistema estável sem gerar falhas 500.

3.3 Cenário de Carga Com Erro (Modo Caos / Chaos Engineering)

Simula instabilidade na infraestrutura ou dependências externas através da injeção controlada de falhas HTTP 500. Atenção: É obrigatório ativar o modo de erro no backend (/rush/error-start) antes de disparar a carga com o k6 para que os erros sejam injetados corretamente. Permite validar os alertas do Grafana, a contagem absoluta de erros e o rastreamento de exceções nos logs do Loki.

4. Requisitos de Ambiente

Git

Docker (versão 20.10+)

Docker Compose (versão 2.0+)

Make (opcional)

5. Passo a Passo de Execução: Opção A - Docker (Padrão Oficial)

1. Clonar o Repositório

git clone https://github.com/seu-usuario/blockbuster-premiere-rush.git
cd blockbuster-premiere-rush


2. Iniciar a Aplicação e a Stack LGTM

(Dica: Utilize a flag --remove-orphans para evitar conflitos de containers antigos ou órfãos de execuções anteriores)

docker compose up --build -d --remove-orphans


3. Verificar Status dos Containers

docker compose ps


4. Acompanhar Logs da API em Tempo Real

docker compose logs -f api


5. Executar os Cenários de Teste via Terminal

A. Teste Unitário (Requisição Pontual)

curl -i "http://localhost:8080/stream/authorize?user_id=usr_99823&movie_id=mov_escape_earth"


B. Cenário de Carga Sem Erros (Rush Limpo + k6)

# Ativa o modo Rush Limpo
curl -X POST http://localhost:8080/rush/start

# Dispara o teste de carga concorrente do k6
docker compose run --rm k6-load-test run /load.js


C. Cenário de Carga Com Erros (Modo Caos + k6)

(Importante: O modo de erro deve estar ativo antes do k6 iniciar os disparos)

# Ativa a injeção de falhas 500
curl -X POST http://localhost:8080/rush/error-start

# Dispara o teste de carga sob falhas
docker compose run --rm -e ERROR_MODE=true k6-load-test


D. Parar Simulações de Rush/Caos

curl -X POST http://localhost:8080/rush/stop


6. Encerrar e Limpar o Ambiente

docker compose down -v


6. Passo a Passo de Execução: Opção B - Makefile (Atalhos Automatizados)

1. Clonar o Repositório

git clone https://github.com/seu-usuario/blockbuster-premiere-rush.git
cd blockbuster-premiere-rush


2. Iniciar o Ambiente

make up


3. Verificar Status dos Containers

make ps


4. Acompanhar Logs da API

make logs


5. Executar os Cenários de Teste via Terminal

A. Teste Unitário

make test-unit


B. Cenário de Carga Sem Erros (Rush Limpo + k6)

make test-rush


C. Cenário de Carga Com Erros (Modo Caos + k6)

make test-chaos


D. Parar Simulações de Rush/Caos

make test-stop


6. Encerrar e Limpar o Ambiente

make down


7. Passo a Passo de Execução: Opção C - Interface Web (Simulador SRE)

1. Subir a Aplicação

Certifique-se de que o ambiente está rodando:

docker compose up -d 


2. Acessar o Simulador Frontend

Abra o navegador e acesse a interface SRE em:

http://localhost:8080


3. Executar os Cenários pela Interface Web

Painel de Controle de Tráfego: Utilize os botões interativos disponíveis na página principal para iniciar simulações de fluxo de usuários, disparar o modo Rush e acionar o Chaos Engineering visualmente.

Inspeção em Tempo Real: Acompanhe o comportamento do sistema diretamente na tela da aplicação, observando a resposta dinâmica do gateway de streaming e o comportamento das métricas no Grafana concomitante (http://localhost:3000).

Normalização: Utilize o botão de parada/reset na interface web para encerrar o cenário ativo e retornar a API ao estado normal.

8. Links de Acesso Rápido com o Ambiente Ativo

Simulador Frontend SRE: http://localhost:8080

Dashboard Grafana (Métricas RED): http://localhost:3000

Métricas Prometheus Expostas: http://localhost:8080/metrics

Prometheus UI: http://localhost:9090
