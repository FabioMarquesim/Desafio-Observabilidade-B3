# Spec - Blockbuster Premiere Rush (Backend & Observabilidade)

## 1. Visão Geral
Serviço HTTP de autorização de streaming desenvolvido em Python (FastAPI) para o desafio técnico de Observabilidade B3 (Cenário 2). O sistema decide a resolução de transmissão (4K, 1080p ou 720p) com base na carga simulada em tempo real e expõe telemetria completa via Prometheus e Grafana, utilizando métricas RED (Rate, Errors, Duration).

## 2. Stack Tecnológica
- **Linguagem/Framework:** Python 3.10+ com FastAPI, Uvicorn e Prometheus Client (`prometheus_client`).
- **Instrumentação e Telemetria:** OpenTelemetry (Metrics, Logs, Traces) com exportação nativa Prometheus e logs estruturados em formato JSON com propagação de `trace_id` e `span_id`.
- **Resiliência e Chaos Engineering:** Tratamento dinâmico de falhas para simular picos de tráfego e erros controlados de servidor (HTTP 500) sem crashar a aplicação.
- **Visualização:** Grafana embutido com painéis em tempo real (RPS, Taxa de Erros com `irate`, Total de Erros absoluto com `increase`, e Latência p95).

## 3. Endpoints da Aplicação

### Principais Endpoints de Negócio
- `GET /stream/authorize?user_id={user_id}&movie_id={movie_id}`
  - **Resposta de Sucesso (200 OK):**
    ```json
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
      "rush_active": true,
      "error_mode": false
    }
    ```

### Endpoints de Controle de Simulação (Rush)
- `POST /rush/start` — Inicia o fluxo de tráfego limpo (sem erros de servidor).
- `POST /rush/error-start` — Inicia o fluxo de tráfego em modo caos/erros (injetando falhas controladas HTTP 500).
- `POST /rush/stop` — Interrompe a simulação de tráfego.

### Endpoint de Telemetria
- `GET /metrics` — Exposição oficial de métricas no formato Prometheus seguindo o modelo RED.

## 4. Requisitos de Observabilidade
- **Logs Estruturados em JSON:** Cada evento registra timestamp, nível, mensagem, serviço e os metadatos de rastreio (`trace_id` e `span_id`).
- **Métricas RED Otimizadas:**
  - **RPS & Taxa de Erros:** Utilização de `irate` com janelas curtas para refletir instantaneamente picos e zerar imediatamente ao parar o tráfego (evitando rampas e suavizações artificiais).
  - **Total de Erros (Stat):** Utilização de `increase` acoplado ao escopo temporal da janela (`$__range`) com formatação estrita para números inteiros (0 decimais).
- **Tracing Distribuído:** Monitoramento completo do ciclo de vida de cada requisição que passa pelo Gateway de Autorização.