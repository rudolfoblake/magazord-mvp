# BI Copilot: Business Intelligence via Model Context Protocol (MCP)

Desenvolvido por **Rudolfo Blake**

## Objetivo

Este projeto implementa um MVP de Business Intelligence para e-commerce utilizando o Model Context Protocol (MCP).

O objetivo é permitir que modelos de linguagem consultem indicadores de negócio através de ferramentas controladas e auditáveis, sem acesso direto ao banco de dados.

A solução combina PostgreSQL, Redis, Python, Node.js e Google Gemini para responder perguntas em linguagem natural sobre faturamento, GMV, ticket médio, produtos, categorias, cancelamentos e indicadores operacionais.

Toda a lógica de negócio e os cálculos são executados no servidor através de ferramentas MCP especializadas. Dessa forma, os dados retornados ao modelo já chegam processados e validados, reduzindo erros de interpretação e eliminando a necessidade de acesso direto ao banco.

Este projeto foi desenvolvido como resposta ao desafio técnico da Magazord.

---

## Documentação Complementar

* [instrucoes_desafio.md](instrucoes_desafio.md): requisitos e escopo do desafio.
* [relatorio_de_melhorias.md](relatorio_de_melhorias.md): melhorias futuras, observabilidade, escalabilidade e evolução da arquitetura.

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

## Estrutura do Projeto

O projeto segue uma arquitetura modular, separando responsabilidades entre o servidor de ferramentas (MCP Server) e o cliente de interação (MCP Client).

```text
magazord-mvp/
├── database/               # Migrações e scripts SQL
├── init/                   # Scripts de inicialização do Docker e dump do banco
├── mcp-client/             # Cliente Node.js + TypeScript
│   ├── src/                # Lógica de integração com Gemini e MCP
│   └── Dockerfile          # Definição do container do cliente
├── mcp-server/             # Servidor Python (FastMCP)
│   ├── src/
│   │   ├── business_rules/ # Regras de faturamento e negócio
│   │   ├── database/       # Configuração de conexão (SQLAlchemy)
│   │   ├── repositories/   # Acesso a dados (Data Access Layer)
│   │   ├── services/       # Lógica de processamento e serviços
│   │   └── tools/          # Definição das ferramentas expostas via MCP
│   ├── tests/              # Testes unitários e de integração
│   └── Dockerfile          # Definição do container do servidor
├── docker-compose.yml      # Orquestração de serviços (Postgres, Redis, Server, Client)
└── .env.example            # Modelo de variáveis de ambiente
```

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

## Exemplos Reais de Consultas

O sistema permite realizar consultas complexas em linguagem natural. Abaixo estão exemplos reais de interações:

### 1. Comparativo de GMV Mensal
**Pergunta:** "Qual foi o nosso GMV no último mês e qual foi a variação percentual em relação ao mês anterior?"

**Resposta:**
```text
Thinking... 
 
[MCP] Calling tool: get_gmv_comparison with args: { current_period: 'last_month' } 
 
----------------------------------------- 
Com base nos dados extraídos do sistema, apresento a análise de desempenho do GMV do último mês em comparação com o 
 período anterior. 
 
 PERÍODO ANALISADO 
 ----------------------------------------- 
 • Mês Atual (Último Mês): 01/05/2026 a 31/05/2026 (Maio de 2026) 
 • Mês de Comparação: 01/04/2026 a 30/04/2026 (Abril de 2026) 
 ----------------------------------------- 
 
 FATOS 
 ----------------------------------------- 
 • O GMV registrado no último mês (maio/2026) foi de R$ 32.169.897,58. 
 • O GMV registrado no mês anterior (abril/2026) foi de R$ 37.251.930,66. 
 • Houve uma redução absoluta de R$ 5.082.033,08 no faturamento entre os dois períodos. 
 ----------------------------------------- 
 
 PRINCIPAIS MÉTRICAS 
 ----------------------------------------- 
 
 | Período | Intervalo de Datas | GMV (R$) | Variação (%) | 
 | :--- | :--- | :--- | :--- | 
 | Mês Anterior (Abril/2026) | 01/04/2026 a 30/04/2026 | R$ 37.251.930,66 | - | 
 | Último Mês (Maio/2026) | 01/05/2026 a 31/05/2026 | R$ 32.169.897,58 | -13,64% | 
 ----------------------------------------- 
 
 INSIGHTS 
 ----------------------------------------- 
 • O faturamento apresentou uma retração de 13,64% no comparativo mensal (MoM). 
 • Essa queda interrompe ou desacelera o patamar de vendas estabelecido em abril, demandando uma investigação mais 
 profunda sobre os fatores geradores dessa variação. 
 ----------------------------------------- 
 
 HIPÓTESES 
 ----------------------------------------- 
 Como a ferramenta atual retornou estritamente os dados consolidados de GMV, levantamos as seguintes hipóteses para 
 explicar a queda, as quais precisam ser validadas com análises complementares: 
 1. Redução no Ticket Médio: O valor médio gasto por pedido pode ter diminuído em maio. 
 2. Queda no Volume de Pedidos: Pode ter ocorrido uma diminuição no tráfego do site ou na taxa de conversão, resultando 
 em menos transações. 
 3. Sazonalidade: O mês de abril pode ter sido impulsionado por campanhas específicas ou feriados que não se repetiram em 
 maio. 
 4. Aumento de Cancelamentos: Um volume maior de pedidos cancelados em maio pode ter reduzido o GMV faturado final. 
 ----------------------------------------- 
 
 RECOMENDAÇÕES 
 ----------------------------------------- 
 • Análise de Ticket Médio: Executar uma consulta de ticket médio comparativa entre abril e maio para validar a hipótese 
 1. 
 • Análise de Cancelamentos: Avaliar o relatório de cancelamentos do período de maio para identificar se houve gargalos 
 operacionais ou de estoque (hipótese 4). 
 • Desempenho de Produtos: Levantar a lista de produtos mais vendidos em ambos os meses para identificar se a queda foi 
 concentrada em alguma categoria ou produto específico. 
```

### 2. Análise de Cancelamentos por Categoria e Produto
**Pergunta:** "Quais categorias de produtos apresentam a maior taxa de cancelamento de pedidos neste trimestre e quais são os top 3 produtos responsáveis por isso?"

**Resposta:**
```text
Thinking... 
 
 [MCP] Calling tool: get_cancellation_analysis with args: { limit: 3, period: 'current_quarter' } 
 
 ----------------------------------------- 
 Com base nos dados de análise de cancelamentos do trimestre atual, apresento o relatório detalhado sobre as categorias 
 com maior taxa de cancelamento e os principais produtos impactados. 
 
 PERÍODO ANALISADO 
 ----------------------------------------- 
 • Trimestre Atual (Parcial): 01/04/2026 a 03/06/2026 
 ----------------------------------------- 
 
 FATOS 
 ----------------------------------------- 
 • O total de pedidos cancelados no trimestre atual é de 9.144 pedidos, representando uma perda de receita de R$ 
 23.000.283,15. 
 • As três categorias com as maiores taxas percentuais de cancelamento são Brinquedos, Livros e Calçados. 
 • Os três produtos com o maior volume absoluto de itens cancelados pertencem às categorias de Brinquedos, Calçados e 
 Automotivo. 
 ----------------------------------------- 
 
 PRINCIPAIS MÉTRICAS 
 ----------------------------------------- 
 
 1. CATEGORIAS COM MAIOR TAXA DE CANCELAMENTO (%) 
 ----------------------------------------- 
 Estas são as categorias onde a proporção de pedidos cancelados em relação ao total de pedidos é mais elevada: 
 
 | Categoria | Pedidos Cancelados | Pedidos Totais | Taxa de Cancelamento (%) | Receita Cancelada (R$) | 
 | :--- | :---: | :---: | :---: | :--- | 
 | 1. Brinquedos | 2.380 | 9.211 | 25,84% | R$ 2.779.223,60 | 
 | 2. Livros | 3.002 | 11.773 | 25,50% | R$ 1.813.241,10 | 
 | 3. Calçados | 2.353 | 9.323 | 25,24% | R$ 2.564.428,60 | 
 
 *(Nota: Em volume absoluto de pedidos cancelados, a categoria de Eletrônicos lidera com 3.461 pedidos cancelados, 
 gerando R$ 4.926.317,50 de receita cancelada, embora sua taxa percentual não seja a maior).* 
 
 2. TOP 3 PRODUTOS COM MAIOR VOLUME DE CANCELAMENTO (GERAL) 
 ----------------------------------------- 
 Estes são os produtos individuais que registraram o maior número de itens cancelados no trimestre: 
 
 | Rank | ID | Nome do Produto | Categoria | Itens Cancelados | Receita Cancelada (R$) | 
 | :---: | :---: | :--- | :--- | :---: | :--- | 
 | 1º | 111 | Boneca Baby Alive Chora de Verdade Hasbro | Brinquedos | 2.630 | R$ 657.237,00 | 
 | 2º | 87 | Bota Coturno Feminina Couro Sintético | Calçados | 2.605 | R$ 520.739,50 | 
 | 3º | 122 | Câmera de Ré Universal com Sensor de Estacionamento | Automotivo | 2.547 | R$ 458.205,30 | 
 ----------------------------------------- 
 
 INSIGHTS 
 ----------------------------------------- 
 • Concentração de Perda: A categoria de Brinquedos possui a maior taxa de cancelamento (25,84%) e abriga o produto líder 
 em cancelamentos gerais (Boneca Baby Alive, com 2.630 itens cancelados). 
 • Impacto Financeiro: Embora a categoria de Livros tenha uma taxa de cancelamento muito alta (25,50%), o impacto 
 financeiro de Brinquedos (R$ 2,77M) e Calçados (R$ 2,56M) é significativamente maior devido ao valor médio dos produtos. 
 • Problema de Calçados: A categoria de Calçados aparece tanto no top 3 de taxa de cancelamento (25,24%) quanto no top 2 
 de produtos mais cancelados (Bota Coturno Feminina, com 2.605 itens). 
 ----------------------------------------- 
 
 HIPÓTESES 
 ----------------------------------------- 
 Como analista de BI, com base nos padrões observados, podemos levantar as seguintes hipóteses para investigação: 
 1. Problemas de Grade/Tamanho (Calçados): A alta taxa de cancelamento em Calçados (especialmente a Bota Coturno) pode 
 estar relacionada a problemas de ajuste de tamanho, levando o cliente a cancelar ou solicitar devolução rápida. 
 2. Atraso na Entrega ou Falta de Estoque (Brinquedos): O produto "Boneca Baby Alive" pode ter sofrido com ruptura de 
 estoque ou atrasos logísticos graves, gerando cancelamentos por parte dos clientes ou do próprio sistema. 
 3. Expectativa vs. Realidade (Automotivo/Brinquedos): Produtos técnicos ou brinquedos interativos podem apresentar alta 
 taxa de cancelamento por arrependimento de compra ou descrição imprecisa no site. 
 ----------------------------------------- 
 
 RECOMENDAÇÕES 
 ----------------------------------------- 
 • Auditoria de Estoque e Logística: Investigar imediatamente o fluxo de atendimento (fulfillment) do produto *Boneca 
 Baby Alive Chora de Verdade Hasbro* para identificar se há atrasos crônicos de entrega ou furos de estoque. 
 • Revisão de Tabela de Medidas: Revisar a tabela de medidas e a descrição da *Bota Coturno Feminina Couro Sintético* no 
 site para reduzir cancelamentos por erro de tamanho. 
 • Análise de Motivos de Cancelamento: Cruzar estes dados com os motivos de cancelamento registrados pelo SAC (ex: 
 arrependimento, atraso, defeito) para validar as hipóteses levantadas. 
```

### 3. Comparativo YoY de Ticket Médio
**Pergunta:** "Fazendo uma análise comparativa de Ano contra Ano (YoY), nosso ticket médio aumentou ou diminuiu?"

**Resposta:**
```text
Thinking... 
 
 [MCP] Calling tool: get_average_ticket_yoy with args: {} 
 
 ----------------------------------------- 
 Com base nos dados extraídos para a comparação de Ano contra Ano (YoY), apresento a análise do ticket médio da empresa. 
 
 PERÍODO ANALISADO 
 ----------------------------------------- 
 • Ano Atual (YTD - Acumulado): 01/01/2026 a 03/06/2026 
 • Ano Anterior (YTD - Equivalente): 01/01/2025 a 03/06/2025 
 ----------------------------------------- 
 
 FATOS 
 ----------------------------------------- 
 • O ticket médio no acumulado do ano atual (2026) é de R$ 2.507,21. 
 • O ticket médio no mesmo período acumulado do ano anterior (2025) foi de R$ 2.512,42. 
 • Houve uma redução absoluta de R$ 5,21 por pedido. 
 • A variação percentual YoY foi de -0,21%, caracterizando uma estabilidade com leve viés de queda. 
 ----------------------------------------- 
 
 PRINCIPAIS MÉTRICAS 
 ----------------------------------------- 
 
 | Métrica | Acumulado 2025 (YTD) | Acumulado 2026 (YTD) | Variação Absoluta (R$) | Variação Percentual (%) | 
 | :--- | :---: | :---: | :---: | :---: | 
 | Ticket Médio | R$ 2.512,42 | R$ 2.507,21 | -R$ 5,21 | -0,21% | 
 ----------------------------------------- 
 
 INSIGHTS 
 ----------------------------------------- 
 • Estabilidade de Consumo: O comportamento de compra do cliente final permaneceu praticamente idêntico ao do ano passado 
 no que tange ao valor gasto por transação. Uma variação de apenas -0,21% indica que as forças de mercado, inflação 
 repassada ou mudanças no catálogo não alteraram significativamente o tamanho do carrinho de compras. 
 • Foco no Volume: Como o ticket médio está estável, qualquer oscilação expressiva no GMV total acumulado do ano (seja 
 para cima ou para baixo) terá sido gerada quase que exclusivamente pela variação no volume de pedidos faturados, e não 
 pelo valor médio das vendas. 
 ----------------------------------------- 
 
 HIPÓTESES 
 ----------------------------------------- 
 1. Mix de Produtos Consistente: O mix de categorias vendidas manteve a mesma proporção de produtos de alto e baixo valor 
 agregado entre 2025 e 2026. 
 2. Elasticidade de Preço: Políticas de descontos ou promoções aplicadas em 2026 conseguiram sustentar o volume de 
 vendas, mas não foram agressivas o suficiente para depreciar o ticket médio, mantendo o equilíbrio com o ano anterior. 
 ----------------------------------------- 
 
 RECOMENDAÇÕES 
 ----------------------------------------- 
 • Análise de Volume de Pedidos: Recomenda-se extrair o volume total de transações YoY para identificar se o faturamento 
 global está crescendo por tração de novos clientes/pedidos. 
 • Estratégias de Upselling e Cross-selling: Para forçar o crescimento do ticket médio no próximo trimestre, sugere-se 
 testar estratégias de recomendação de produtos complementares no carrinho ou criar faixas de frete grátis ligeiramente 
 acima do ticket médio atual (ex: frete grátis para compras acima de R$ 2.700,00). 
```

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

1.  Criar o arquivo de ambiente:
    ```bash
    cp .env.example .env
    ```
2.  Preencher as variáveis obrigatórias:
    *   `GEMINI_API_KEY`: Sua chave de API do Google Gemini.
    *   `TZ`: Timezone do sistema (ex: `America/Sao_Paulo`).
    *   `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: Credenciais do banco de dados.
    *   `DATABASE_URL`: String de conexão para o SQLAlchemy.
    *   `REDIS_URL`: URL de conexão para o Redis.
    *   `MCP_SERVER_URL`: URL onde o cliente encontrará o servidor MCP (dentro ou fora do Docker).

### Subir os serviços

```bash
docker compose up --build -d
```

### Executar o cliente

O cliente roda em modo interativo. Use o comando abaixo para iniciar a CLI:

```bash
docker compose --profile client run --rm mcp-client
```

### Executar os Testes

Para garantir a integridade da lógica de negócio e das ferramentas, você pode rodar os testes automatizados:

```bash
# Rodar testes do servidor
docker compose exec mcp-server pytest
```

---

## Decisões de Arquitetura

### Justificativa Tecnológica

*   **MCP Server (Python + FastMCP)**: Escolhido pela maturidade do ecossistema de análise de dados (Pandas, SQLAlchemy) e pela facilidade de integração com o protocolo MCP via biblioteca FastMCP. Python permite expressar regras de negócio analíticas de forma concisa e eficiente.
*   **MCP Client (Node.js + TypeScript)**: Utilizado para garantir uma CLI performática e tipos seguros. A integração com o SDK do Google Generative AI é extremamente estável em ambiente Node, facilitando o tratamento de streams e interações interativas.
*   **PostgreSQL**: Banco de dados relacional robusto para garantir a integridade dos dados transacionais do e-commerce.
*   **Redis**: Essencial para cache de indicadores pesados, reduzindo o custo computacional e financeiro (tokens) em perguntas repetitivas.

### Design de Ferramentas (MCP)

A estratégia de design focou em **ferramentas especializadas e granulares** em vez de uma ferramenta única de "execução de SQL".

*   **Controle de Contexto**: Cada ferramenta retorna apenas o necessário para a resposta (ex: agregados mensais em vez de linhas individuais de pedidos). Isso evita o estouro da janela de tokens da LLM.
*   **Redução de Alucinações**: Ao receber dados já processados pelo servidor (como variações percentuais e status validados), o modelo não precisa realizar cálculos complexos, apenas interpretar os fatos retornados.
*   **Granularidade**: Ferramentas como `get_gmv_comparison` e `get_cancellation_analysis` isolam responsabilidades, permitindo que a LLM orquestre múltiplas chamadas se necessário, mas sempre com dados validados.

### Flexibilidade de Períodos

Diferente de soluções rígidas, o sistema suporta tanto períodos relativos quanto datas customizadas para todas as ferramentas:

*   **Relativos:** `today`, `yesterday`, `current_month`, `last_month`, `current_quarter`, `last_quarter`, `current_year`, `last_year`.
*   **Customizados:**
    *   **Mês Específico:** `2025-01` (Ex: "Qual o GMV de Janeiro de 2025?")
    *   **Dia Específico:** `2025-06-02`
    *   **Trimestre Específico:** `2025-Q1`

Essa flexibilidade permite realizar análises históricas precisas e responder a perguntas sobre qualquer período passado.

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

O projeto utiliza decoradores para desacoplar funcionalidades de infraestrutura da lógica de negócio, conforme implementado em [server.py](mcp-server/src/server.py).

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

## Uso de Inteligência Artificial

O desenvolvimento do projeto foi conduzido por mim desde a etapa de concepção da solução até a validação final dos resultados.

O processo começou com pesquisa e levantamento de boas práticas para entender como atender aos requisitos do desafio utilizando MCP, PostgreSQL, Redis, LLMs e arquitetura modular. Essa etapa envolveu estudo técnico, análise de referências do mercado e validação de alternativas arquiteturais.

Durante o desenvolvimento utilizei ChatGPT como apoio para pesquisa, validação de abordagens e discussão de alternativas técnicas.

Após a definição inicial da arquitetura, utilizei um agente especializado de desenvolvimento configurado por mim dentro da IDE Trae. Esse agente foi construído a partir de prompts próprios que venho refinando ao longo dos últimos meses para atividades de arquitetura, desenvolvimento, revisão de código e análise técnica.

O agente recebeu diretrizes detalhadas sobre:

* arquitetura do sistema
* responsabilidades dos componentes
* padrões de código
* princípios SOLID
* separação de responsabilidades
* observabilidade
* escalabilidade
* boas práticas de desenvolvimento

A partir dessa base, a IA auxiliou na geração inicial de código, prototipação de componentes, criação de consultas SQL, estruturação das ferramentas MCP e implementação de partes da solução.

Entretanto, todo o processo ocorreu em um modelo Human-in-the-Loop, onde cada etapa foi revisada, ajustada e validada manualmente.

As principais atividades realizadas manualmente incluíram:

* definição da arquitetura
* refinamento das regras de negócio
* revisão e correção de código
* validação das consultas SQL
* debugging
* testes locais
* validação das métricas financeiras
* revisão da documentação
* ajustes de observabilidade e resiliência

Além disso, utilizei outras ferramentas de IA como apoio complementar para revisão técnica e validação cruzada das implementações, incluindo Gemini e Manus.

Todo o sistema foi executado e validado localmente através de Docker Compose. As respostas produzidas pela aplicação foram testadas em múltiplos cenários e comparadas manualmente para verificar consistência dos resultados.

Durante o desenvolvimento foram realizados diversos ciclos de revisão e validação, incluindo conferência dos indicadores retornados pelas ferramentas MCP, comparação de resultados entre execuções e revisão das respostas utilizando diferentes modelos de IA como mecanismo adicional de verificação.

Em resumo, a IA foi utilizada como acelerador de desenvolvimento e revisão técnica, mas todas as decisões finais de arquitetura, regras de negócio, validação dos indicadores e aprovação das implementações permaneceram sob minha responsabilidade.

Outro ponto importante é que o projeto não foi construído de forma linear. A arquitetura evoluiu ao longo do desenvolvimento através de ciclos sucessivos de implementação, testes, revisão e refatoração.

Diversas melhorias surgiram durante esse processo. Inicialmente algumas responsabilidades estavam distribuídas diretamente nas ferramentas MCP, mas conforme a solução amadureceu foram sendo extraídas para componentes reutilizáveis e desacoplados.

Exemplos dessa evolução incluem:

* Introdução de decorators para cache e telemetria.
* Centralização das regras de negócio de faturamento.
* Criação de uma camada de observabilidade com logging estruturado.
* Implementação de Circuit Breaker para aumentar a resiliência da integração com a LLM.
* Evolução das consultas SQL para modelos mais consistentes e reutilizáveis.
* Refinamento do design das ferramentas MCP para reduzir acoplamento e melhorar a qualidade do contexto enviado à IA.

Esse processo foi iterativo. Muitas decisões arquiteturais não surgiram prontas no início do projeto, mas foram sendo refinadas conforme novos cenários eram identificados durante os testes, validações de métricas e revisões técnicas.

---

## Roadmap de Evolução

O projeto possui um plano de evolução detalhado para cenários de alta escala e produção. Para uma análise técnica completa de cada ponto, acesse o [Relatório de Melhorias e Evolução da Arquitetura](relatorio_de_melhorias.md).

### Curto Prazo (Q3 2026)
- **Suporte Multi-idioma:** Otimização dos prompts do sistema para suporte nativo a análises em Inglês e Espanhol.
- **Exportação de Relatórios:** Implementação de ferramentas para geração de PDFs e planilhas formatadas a partir dos insights da IA.
- **Refatoração para ORM:** Migração das queries SQL puras para modelos declarativos do SQLAlchemy, aumentando a segurança de tipos e facilitando a manutenção.
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
