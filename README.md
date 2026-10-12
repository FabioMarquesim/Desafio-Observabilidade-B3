# Stream Authorization Service: Observabilidade

Serviço HTTP em Python (FastAPI) que simula a autorização de streaming de uma plataforma de vídeo (**Cenário 2: Blockbuster Premiere Rush**), totalmente instrumentado com OpenTelemetry (traces, métricas e logs) e visualizado no Grafana.

## O que o serviço faz

`GET /stream/authorize?user_id={user_id}&movie_id={movie_id}`

- Consulta uma "API externa" simulada (latência de 50 a 500 ms e ~10% de falha).
- **Degradação graciosa:** quanto maior a latência, menor a resolução autorizada (`4K` < 150 ms, `1080p` < 300 ms, `720p` acima disso).
- Se a API externa falhar, a aplicação não cai: responde **HTTP 503** com um JSON de erro.

## Pré-requisitos

- Docker e Docker Compose

## Como rodar

```bash
docker compose up --build
```

Na primeira execução, o download da imagem `grafana/otel-lgtm` é grande e pode levar alguns minutos. Quando tudo estiver de pé, o k6 começa a gerar carga automaticamente (50 usuários virtuais por 5 minutos).

Para repetir a carga depois que ela terminar:

```bash
docker compose up k6-load-test
```

Para parar tudo: `docker compose down`.

## Como acessar

| O quê | URL |
|---|---|
| API (Swagger) | http://localhost:8080/docs |
| Métricas Prometheus da API | http://localhost:8080/metrics |
| Grafana | http://localhost:3000 (login `admin` / `admin`) |

## Dashboard

O arquivo `dashboard.json` (raiz do repositório) contém o dashboard **Stream API - RED** com três painéis:

- **RPS:** requisições por segundo
- **Taxa de Erros (%):** proporção de respostas 5xx
- **Latência p95:** em milissegundos

Para importar: Grafana → **Dashboards → New → Import → Upload JSON file** → selecione `dashboard.json`. Use o intervalo **Last 15 minutes** com o k6 rodando.

## O que está instrumentado

- **Traces:** OpenTelemetry (OTLP/HTTP) → Tempo. Um span por requisição.
- **Métricas:** OpenTelemetry (OTLP/HTTP) → Prometheus. Além disso, a API expõe `/metrics` em formato Prometheus com as métricas RED próprias (`stream_api_http_requests_total` e `stream_api_http_request_duration_seconds`).
- **Logs:** JSON estruturado no stdout, com `trace_id` e `span_id` em cada linha.

### Demonstração: do log ao trace

1. Pegue um `trace_id`:
```bash
   docker compose logs api | grep trace_id
```
2. No Grafana: **Explore → Tempo → TraceQL**, cole o `trace_id` e execute.
3. O trace abre com a duração da mesma requisição (compare com `latency_ms` do log).

## Decisões de design

- **Falha simulada com exceção própria** (`ExternalServiceError`): só a falha esperada vira 503; bugs reais continuam aparecendo como 500 nas métricas.
- **Endpoint assíncrono** com `asyncio.sleep`, para suportar 50 usuários simultâneos sem bloquear o event loop.
- **Label `route` com o template da rota** (não a URL crua), evitando cardinalidade alta nas métricas.
- **Dockerfile otimizado:** imagem `slim`, cache de dependências por camada, usuário não-root.

## Estrutura

```
.
├── app/
│   ├── main.py            # rota e regras de negócio
│   ├── telemetry.py       # setup OpenTelemetry (traces e métricas)
│   ├── logging_config.py  # logs JSON com trace_id
│   ├── metrics.py         # /metrics (prometheus-client)
│   └── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── load.js                # teste de carga k6
└── dashboard.json         # dashboard Grafana
```