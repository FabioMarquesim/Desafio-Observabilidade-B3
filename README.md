# 🏆 Desafio Técnico - Observabilidade B3

Um desafio prático desenvolvido para avaliar os fundamentos de Observabilidade e Engenharia de Confiabilidade aplicados a um serviço de backend simulado. 

> *"Um sistema às cegas é um incidente esperando para acontecer. Sua missão é trazer a luz."*

---

## 🎯 Objetivo do Desafio
Construir um serviço HTTP com um endpoint integrado a uma API pública (ou utilizando dados simulados). O foco principal do desafio é **instrumentar essa aplicação** para gerar telemetria útil (Logs, Métricas e Traces) de forma automatizada em um ambiente local.

---

## 🔍 O Que Será Avaliado
A sua entrega será avaliada com base nos seguintes pesos:
* **Instrumentação (Métricas/Logs/Traces):** 40%.
* **Criação de Dashboards:** 25%.
* **Funcionamento da API e Resiliência:** 20%.
* **Documentação e Infraestrutura como Código (Docker):** 15%.

---

## ⏱️ Prazo de Entrega
O candidato terá **5 dias corridos** a partir do recebimento deste desafio para enviar a solução.

---

## 🏗️ Requisitos de Infraestrutura e Stack
Para padronizar a avaliação, a sua entrega deve rodar localmente com um único comando de orquestração. 

| Componente | Requisito Esperado |
| :--- | :--- |
| **Linguagem/Framework** | Python utilizando Flask ou FastAPI. |
| **Ambiente de Execução** | Docker Compose ou Docker Swarm. |
| **Stack de Observabilidade** | OpenTelemetry para instrumentação. Utilizar a imagem oficial `grafana/otel-lgtm` que provisiona uma stack completa com OTEL Collector, Prometheus, Loki, Tempo e Grafana. É necessário utilizar também a imagem do `grafana/k6`, que será responsável por gerar o teste de carga na aplicação. |

---

## 🧭 Cenários Disponíveis (Escolha APENAS 1)

### 🎧 Cenário 1 — Mainstage Live Sync (Música & Festivais)
**📖 A História:**
Em festivais de grande porte, a experiência audiovisual é tudo. A equipe de engenharia de transmissão precisa de uma API ultra-rápida que atue como ponte entre os palcos principais e a internet. O sistema deve capturar instantaneamente os metadados das faixas que estão sendo tocadas nos CDJs e softwares de mixagem dos artistas, processar a "energia" da música e enviar essas informações para sincronizar os painéis de LED, a pirotecnia e atualizar os aplicativos do público em tempo real.

O desafio é que a rede em festivais oscila muito e a integração com bases de dados musicais pode apresentar latência. Se a API falhar ou ficar lenta, os visuais do palco perdem o sincronismo com as batidas, arruinando a experiência do show.

**🎯 Missão Técnica:**
Construir um endpoint que receba a faixa atual, consulte dados enriquecidos simulando uma API externa de streaming e devolva as instruções de palco.

`GET /live-sync/track?artist={artist}&title={title}`  

**Resposta Esperada:**
```json
{  
  "track": "Everlong",  
  "artist": "Foo Fighters",  
  "bpm": 158,  
  "energy_level": "High",  
  "visual_preset": "strobes_and_lasers",  
  "sync_delay_ms": 12  
}
```

##

### 🍿 Cenário 2 — Blockbuster Premiere Rush (Filmes & Streaming)  
**📖 A História:**
Uma grande plataforma de streaming está prestes a lançar a continuação de um épico de ficção científica simultaneamente para o mundo todo. Exatamente às 20h00, milhões de usuários famintos por entretenimento apertarão o botão de play no exato mesmo segundo.   O serviço responsável por verificar as credenciais do usuário, analisar a qualidade da banda de internet do cliente e autorizar a resolução da transmissão (4K, 1080p, 720p) precisa aguentar o "Premiere Rush", ou seja, o pico absurdo de acessos. Se o serviço principal de validação ficar sobrecarregado, ele precisa degradar graciosamente para não derrubar a plataforma inteira, entregando resoluções menores em vez de telas de erro.   

**🎯 Missão Técnica:**  
Construir o serviço de autorização de streaming que decide a qualidade que o usuário vai receber baseado em fatores simulados, como a carga do servidor ou conexão do cliente.   

`GET /stream/authorize?user_id={user_id}&movie_id={movie_id}`  

**Resposta Esperada:**
```json
{  
  "user_id": "usr_99823",  
  "movie_id": "mov_dune_part2",  
  "authorized": true,  
  "resolution": "4K",  
  "drm_token": "eyJhbGciOiJIUzI1NiIsInR5c...",  
  "server_region": "sa-east-1"  
}
```  

---

## 📊 Sistema de Pontuação e Entregáveis (Total: 100 pts)  
### 📈 1. Observabilidade e Instrumentação (40 pontos)  
* Expor métricas padrão RED (Rate, Errors, Duration) no formato Prometheus (15 pts).   
* Estruturar logs em formato JSON (10 pts).   
* Injetar o trace_id nos logs para garantir a rastreabilidade ponta a ponta (15 pts).   

### 🖥️ 2. Dashboards e Visualização (25 pontos)  
* Fornecer um arquivo JSON exportado do Grafana contendo um dashboard previamente configurado (15 pts).  
* O dashboard deve conter no mínimo 3 painéis: RPS (Requisições por segundo), Taxa de Erros e Latência, utilizando p95 ou média (10 pts).  

### ⚙️ 3. Funcionamento da API e Resiliência (20 pontos)  
* O endpoint desenvolvido deve retornar as respostas esperadas no formato JSON (10 pts).  
* A aplicação não deve sofrer "crash" caso a API externa simulada falhe; ela deve tratar o erro e retornar um HTTP 500 ou 503 (10 pts).  

### 📦 4. Documentação e Infraestrutura (15 pontos)  
* Escrever um Dockerfile otimizado e um arquivo de orquestração (Compose/Swarm) que execute a API e a stack de observabilidade de forma conjunta (10 pts).  
* Criar um README com instruções claras explicando como rodar o projeto e como acessar o dashboard criado (5 pts).  

---

## 🛠️ Material de Apoio e Configuração  
Para ajudar na construção do setup, utilize as referências oficiais abaixo:  
* **Grafana LGTM Stack:** Documentação Oficial  [https://grafana.com/docs/opentelemetry/docker-lgtm/]
* **Instrumentação Python:** OpenTelemetry Docs  [https://opentelemetry.io/docs/]
* **Testes de Carga:** Grafana k6 Docs  [https://hub.docker.com/r/grafana/k6]

### Configuração do Gerador de Carga (k6)  
Para garantir que sua aplicação receba tráfego e popule os dashboards, crie o arquivo `load.js` na raiz do seu projeto:  
```JavaScript
import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  vus: 50, // 50 usuários virtuais simultâneos simulados
  duration: '5m', // Duração total do teste
};

export default function () {
  // ATENÇÃO: Ajuste a URL abaixo para refletir o cenário que você escolheu
  http.get('http://api:8080/stream/authorize?user_id=123&movie_id=dune2');
  sleep(0.1); // Pausa de 100ms entre as requisições de cada usuário
}
```  

No seu arquivo de orquestração `docker-compose.yml`, adicione o bloco abaixo como referência para acionar o teste junto com a sua API:  
```YAML  
  k6-load-test:
    image: grafana/k6:latest
    volumes:
      - ./load.js:/load.js
    command: run /load.js
    depends_on:
      - api # Garante que a API inicie antes de receber o tráfego
```  

---

## 🚀 Processo de Submissão  
### Antes de enviar, valide sua entrega com este checklist:  
* [ ] Repositório público com código-fonte.  
* [ ] Arquivo de orquestração de containers funcional (subindo API, Prometheus, Grafana, Loki, Tempo e Otel Collector).  
* [ ] Aplicação instrumentada expondo rota /metrics.  
* [ ] Arquivo JSON do Dashboard do Grafana na raiz do projeto.  
* [ ] Documentação (README.md da solução) com instruções claras de execução.

### Como enviar:
* Faça um fork deste repositório (não clone diretamente!).  
* Desenvolva o seu projeto dentro deste fork.  
* Faça o commit e suba as alterações para o SEU fork.  
* Pela interface do GitHub, abra um Pull Request para este repositório original.  

### ⚠️ ATENÇÃO:  
* Mantenha o seu fork público para facilitar a inspeção do código pela equipe e não tente fazer PUSH diretamente para este repositório base.  

---

### 🎙️ O Que Esperar da Avaliação?  
A etapa final do processo seletivo incluirá um bate-papo técnico sobre a sua entrega. Esteja preparado para compartilhar sua tela rodando o projeto, navegar pelos dashboards que você construiu e realizar troubleshooting ao vivo caso simulemos uma falha nos seus containers. Entender como a sua telemetria se comporta sob pressão é tão importante quanto o código da API!
