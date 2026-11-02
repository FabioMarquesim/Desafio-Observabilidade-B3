# Linha do Tempo e Diário de Bordo - Desafio Observabilidade B3

Este documento registra o passo a passo da concepção, arquitetura e desenvolvimento do projeto, servindo como guia para a apresentação técnica.

## 1. Planejamento e Especificação (Spec Kit)
- **Definição do Escopo:** Escolha do **Cenário 2 (Blockbuster Premiere Rush)** focado em resiliência, autorização de streaming e alta performance.
- **Criação do Spec (`spec.md`):** Estabelecidas as diretrizes técnicas, endpoints obrigatórios (`/stream/authorize` e `/metrics`), e os requisitos de observabilidade (métricas RED, logs estruturados em JSON e tracing distribuído).

## 2. Configuração do Repositório e Versionamento
- **Fork e Integração:** Realizado o fork seguro do repositório base para o GitHub pessoal e clonagem local via Cursor.
- **Padrão de Commits:** Adoção rigorosa de *Conventional Commits* em Português (pt-br) para assegurar histórico limpo e rastreável.
- **Primeiro Marco:** Commit da especificação técnica inicial (`docs: adiciona especificacao tecnica do cenario 2`).

## 3. Arquitetura Base (Backend & Clean Code)
- **Framework:** Implementação em **Python com FastAPI** devido à alta performance assíncrona e facilidade de instrumentação.
- **Estrutura Inicial:** Criação do arquivo `main.py` e do gerenciador de dependências (`requirements.txt`).
- **Endpoints Funcionais:** Subida bem-sucedida da rota de autorização simulada de streaming e do endpoint de métricas básicas.
- **Segundo Marco:** Commit da estrutura base do backend (`feat: implementa estrutura base do backend em fastapi com rotas de autorizacao e metricas`).

## 4. Containerização e Stack LGTM
- **Dockerfile & Docker Compose:** Criação dos arquivos de containerização para a API e orquestração da stack LGTM (`grafana/otel-lgtm`).
- **Integração de Métricas e Traces:** Exposição das portas do Grafana (3000), Prometheus (9090) e OTLP (4317/4318).
- **Terceiro Marco:** Commit da configuração do ambiente containerizado (`feat: adiciona dockerfile e docker-compose com stack lgtm`).

## 5. Containerização e Stack LGTM
- **Docker Compose:** Orquestração bem-sucedida da API FastAPI (`blockbuster-api`) integrada com a stack unificada de observabilidade `grafana/otel-lgtm`.
- **Portas Ativas:** Mapeamento concluído para o Grafana (`3000`), Prometheus (`9090`) e coletor OTLP (`4317/4318`).
- **Terceiro Marco:** Commit da configuração do ambiente containerizado (`feat: adiciona dockerfile e docker-compose com stack lgtm`).

## 6. Testes de Carga & Simulação de Falhas
- **Script de Carga (`load_test.py`):** Desenvolvido script concorrente simulando o tráfego de pico do cenário *Blockbuster Premiere Rush*.
- **Validação de Métricas RED:** Disparadas requisições em massa para testar o comportamento da API containerizada e a coleta de dados pelo OpenTelemetry/Prometheus.
- **Quarto Marco:** Commit da automação de testes de carga (`test: adiciona script de teste de carga para simulacao de pico`).

## 7. Desenvolvimento do Frontend e Simulador de SRE
- **Interface Web:** Criação do `frontend.html` em Tailwind CSS com design retrô minimalista inspirado na identidade visual da Blockbuster Premiere Rush.
- **Simulação Avançada (Rush):** Implementação dos modos de tráfego dinâmico (*Rush Limpo* via `/rush/start` e *Rush c/ Erros/Chaos* via `/rush/error-start`).
- **Contadores em Tempo Real:** Adicionados contadores granulares no painel do SRE para monitorar o total de requisições, erros 500 e a quebra de resoluções de transmissão (4K, 1080p e 720p).
- **Quinto Marco:** Commit da interface web e simulação avançada (`feat: adiciona interface web e simulação avançada de rush`).

## 8. Refinamento de Observabilidade & Sincronização RED
- **Correção de Telemetria:** Substituição das funções de taxa para eliminar rampas artificiais e atrasos visuais, adotando `irate` para a taxa de erros instantânea e `increase` com `$__range` acoplado à redução `lastNotNull` para o contador de total de erros.
- **Padronização do Backend:** Ajuste no middleware de métricas do FastAPI para evitar duplicações de incremento em status HTTP 500.
- **Ajustes de UI no Grafana:** Configuração de arredondamento estrito de números inteiros (0 decimais) nos painéis Stat para bater perfeitamente com os eventos reais do cliente.
- **Sexto Marco:** Commit da correção de métricas e sincronização final (`feat(observabilidade): corrige divergência de métricas RED e sincroniza simulador com o Grafana`).