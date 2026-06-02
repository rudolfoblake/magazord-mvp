# Enterprise BI Copilot: Business Intelligence via Model Context Protocol (MCP)

Desenvolvido por **Rudolfo Blake**

## Objetivo

Este projeto implementa um MVP de Business Intelligence para e-commerce utilizando o Model Context Protocol (MCP).

O objetivo é permitir que modelos de linguagem consultem indicadores de negócio através de ferramentas controladas e auditáveis, sem acesso direto ao banco de dados.

A solução combina PostgreSQL, Redis, Python, Node.js e Google Gemini para responder perguntas em linguagem natural sobre faturamento, GMV, ticket médio, produtos, categorias, cancelamentos e indicadores operacionais.

Toda a lógica de negócio e os cálculos são executados no servidor através de ferramentas MCP especializadas. Dessa forma, os dados retornados ao modelo já chegam processados e validados, reduzindo erros de interpretação e eliminando a necessidade de acesso direto ao banco.

Este projeto foi desenvolvido como resposta ao desafio técnico da Magazord.

---

## Documentação Complementar

* **instrucoes_desafio.md**: requisitos e escopo do desafio.
* **relatorio_de_melhorias.md**: melhorias futuras, observabilidade, escalabilidade e evolução da arquitetura.

---

## Arquitetura

A solução é composta por dois componentes principais.

### MCP Server (Python)

Responsável por:

* Conexão com PostgreSQL
* Execução das consultas
* Aplicação das regras de negócio
* Agregação dos indicadores
* Cache via Redis
* Exposição das ferramentas MCP

Toda a lógica crítica permanece no servidor para garantir consistência dos cálculos e uma única fonte da verdade.

### MCP Client (Node.js + TypeScript)

Responsável por:

* Interface de linha de comando (CLI)
* Integração com Google Gemini
* Interpretação das perguntas do usuário
* Seleção e execução das ferramentas MCP
* Tratamento de falhas através de Circuit Breaker

---

## Fluxo de Funcionamento

1. O usuário faz uma pergunta em linguagem natural.
2. O Gemini interpreta a intenção.
3. O cliente identifica quais ferramentas MCP devem ser executadas.
4. O servidor consulta PostgreSQL e Redis.
5. Os dados são processados no servidor.
6. O resultado é retornado para o modelo.
7. O modelo gera a resposta final utilizando apenas os dados recebidos.

---

## Exemplo de Uso

Pergunta:

> Qual foi o GMV do último mês e qual a variação em relação ao mês anterior?

Resposta:

* GMV Maio/2026: R$ 32.169.897,58
* GMV Abril/2026: R$ 37.251.930,66
* Variação: -13,64%

Todas as métricas são obtidas através das ferramentas MCP e calculadas no servidor.

---

## Tecnologias Utilizadas

### Backend

* Python 3.12
* SQLAlchemy
* Pydantic
* FastMCP

### Banco e Cache

* PostgreSQL 17
* Redis 7

### Cliente

* Node.js
* TypeScript
* Google Generative AI SDK

### Infraestrutura

* Docker
* Docker Compose

---

## Instalação e Execução

### Pré-requisitos

* Docker
* Docker Compose
* Chave de API do Google Gemini

### Configuração

Criar o arquivo de ambiente:

```bash
cp .env.example .env
```

Configurar:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

### Subir os serviços

```bash
docker compose up --build -d
```

### Executar o cliente

```bash
docker compose --profile client run --rm mcp-client
```

---

## Decisões de Arquitetura

### Ferramentas MCP Especializadas

Em vez de permitir que a LLM gere consultas SQL diretamente, o sistema expõe ferramentas específicas para cada tipo de análise.

Exemplos:

* GMV
* Ticket Médio
* Comparações de períodos
* Produtos mais vendidos
* Cancelamentos
* Indicadores executivos

Essa abordagem reduz riscos de alucinação e mantém as regras de negócio centralizadas.

### Regras de Faturamento

Para garantir consistência dos indicadores:

Status considerados válidos para receita:

* processing
* shipped
* delivered

Status excluídos do faturamento:

* cancelled
* pending

Toda a lógica permanece centralizada no servidor.

### Cache

O Redis é utilizado para armazenar resultados de consultas recorrentes e reduzir carga sobre o banco de dados.

---

## Engenharia de Software

O projeto utiliza decorators para desacoplar funcionalidades de infraestrutura da lógica de negócio.

### @mcp_cache

Responsável pelo cache de resultados no Redis.

Benefícios:

* Redução de latência
* Menor carga no banco
* Reutilização de consultas frequentes

### @tool_telemetry

Responsável pela observabilidade das ferramentas.

Registra:

* nome da ferramenta
* argumentos utilizados
* tempo de execução
* status de sucesso ou falha

### @mcp.tool()

Decorator responsável pelo registro automático das ferramentas no protocolo MCP.

---

## Observabilidade

Atualmente o projeto implementa logging estruturado para execução das ferramentas MCP.

Informações registradas:

* timestamp
* tool_name
* execution_time_ms
* success
* error_message
* cache_hit

Os logs são enviados para stdout e podem ser consumidos diretamente pelo Docker.

---

## Uso de Inteligência Artificial

A IA foi utilizada como ferramenta de apoio durante o desenvolvimento.

Foi utilizada para:

* geração inicial de código
* prototipação de componentes
* geração de consultas SQL
* aceleração da documentação

Toda a arquitetura, regras de negócio, validação dos indicadores, revisão do código e ajustes finais foram realizados manualmente.

---

## Roadmap de Evolução

### Curto Prazo (Q3 2026)
- **Suporte Multi-idioma:** Otimização dos prompts do sistema para suporte nativo a análises em Inglês e Espanhol.
- **Exportação de Relatórios:** Implementação de ferramentas para geração de PDFs e planilhas formatadas a partir dos insights da IA.
- **Observabilidade Avançada:** Implementação de correlação completa de requisições (`request_id` e `correlation_id`) para rastreamento end-to-end.
- **Expansão de Testes:** Ampliação da cobertura de testes para incluir cenários de carga e falhas de integração.

### Médio Prazo (Q4 2026 - Q1 2027)
- **Análise Preditiva:** Integração de modelos de Machine Learning para previsão de demanda (Forecasting) e detecção de anomalias em tempo real.
- **Orquestrador de LLM Dedicado:** Migração para uma arquitetura de microserviço dedicada para gestão de múltiplos provedores de IA e segurança avançada.
- **Arquitetura Multiagente:** Introdução de agentes especializados por domínio (Financeiro, Comercial e Operações) para análises mais profundas.
- **Escalabilidade de Dados:** Implementação de Read Replicas e particionamento de tabelas históricas para suportar volumes massivos de dados.

---

## Licença

Distribuído sob a licença MIT.

Veja o arquivo [LICENSE](LICENSE) para mais informações.

---

## Autor

**Rudolfo Blake**

Backend Developer | Python | MCP | AI Engineering

Email: [rudolfoblake@gmail.com](mailto:rudolfoblake@gmail.com)
