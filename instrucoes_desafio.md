## Desafio: MVP - Copiloto de Business Intelligence (BI) para E-commerce
Neste teste, você irá construir um MVP de um ecossistema inteligente capaz de transformar dados brutos de um e-commerce em insights estratégicos para diretores e tomadores de decisão, utilizando o **Model Context Protocol (MCP)**.
---
## 📅 O Cenário
Você recebeu um banco de dados relacional (disponibilizado via Docker Compose) que contém o histórico de vendas, produtos e clientes (O start inicial do banco pode demorar alguns minutos por causa de seu tamanho).
A diretoria da empresa precisa de um analista de dados disponível 24/7 que responda a perguntas complexas de negócio sobre performance de vendas, saúde financeira e comportamento de estoque. Sua missão é criar a infraestrutura que conecta uma LLM a essa base de dados de forma performática, segura e inteligente.
---
## 🏗️ Requisitos Arquiteturais
O projeto deve ser dividido obrigatoriamente em duas frentes que se comunicam através do protocolo MCP:
### 1. Servidor MCP (Mecanismo de Dados)
* Deve expor os dados do banco de dados fornecido no Docker Compose seguindo a especificação do protocolo MCP (ferramentas, recursos ou prompts).
* Não deve apenas repassar queries SQL brutas para a LLM resolver (a LLM é péssima com matemática pesada). O servidor deve ser inteligente o suficiente para processar e agregar os dados antes de entregá-los.
### 2. Client MCP (Interface de Linha de Comando - CLI)
* Deve ser uma aplicação de terminal interativa.
* Deve se conectar ao Servidor MCP criado.
* Deve integrar-se a uma LLM de sua escolha (OpenAI, Anthropic, Ollama/local, Gemini, etc.) para que o usuário possa conversar em linguagem natural com os dados. Caso queira, podemos fornecer uma chave do Gemini com alguns créditos para você, solicite diretamente ao recrutador.
> ⚠️ **Restrição Tecnológica Obrigatória (Poliglota):**
> Um dos serviços (Server ou Client) deve ser desenvolvido obrigatoriamente em **Python**. O outro serviço deve ser desenvolvido obrigatoriamente em **Node.js** ou **PHP**. Você tem total liberdade para escolher qual tecnologia usará em qual lado.
---
## 📊 O Desafio de Negócio (Escopo Aberto)
Você é o designer da solução. Não iremos especificar quais funções, ferramentas (*Tools*) ou recursos (*Resources*) seu servidor MCP deve expor. No entanto, para o teste ser considerado um sucesso, o seu Client CLI (via LLM) deve ser capaz de responder com precisão absoluta a perguntas como:
* *"Qual foi o nosso GMV no último mês e qual foi a variação percentual em relação ao mês anterior?"*
* *"Quais categorias de produtos apresentam a maior taxa de cancelamento de pedidos neste trimestre e quais são os top 3 produtos responsáveis por isso?"*
* *"Fazendo uma análise comparativa de Ano contra Ano (YoY), nosso ticket médio aumentou ou diminuiu? 
---
## 📈 Melhorias de Performance no Banco de Dados
Como responsável, você deve olhar criticamente para a infraestrutura que recebeu. Junto com o código, você deve entregar um relatório ou proposta técnica contendo:
**Gargalos Identificados:** Quais queries ou operações solicitadas pelas perguntas acima seriam catastróficas para o banco de dados atual em produção se o volume de dados ou de acessos escalasse 100x?
---
## 📝 O que deve ser entregue na Documentação (`README.md`)
A avaliação do seu teste levará muito em conta a sua capacidade de justificar suas escolhas. Clone esse repositório e no seu arquivo de documentação, responda detalhadamente:
* **Justificativa Tecnológica:** Por que você escolheu a Tecnologia X para o Server e a Tecnologia Y para o Client?
* **Design de Ferramentas (MCP):** Qual foi a sua estratégia ao desenhar as interfaces do seu servidor MCP? Como você garantiu que a LLM não recebesse dados demais (estourando a janela de tokens) e nem de menos (gerando alucinações)?
* **Tratamento de Regras de Negócio:** Como você garantiu que pedidos cancelados ou reembolsados não distorcessem as métricas financeiras de faturamento passadas para a IA?
* **Roadmap:** Apesar de ser um MVP, documente! Se algo deixou de ser entregue, justifique! Quais os passos naturais com os dados fornecidos poderiam ser inclusos em um roadmap dessa aplicação? Separe em dois horizontes: curto prazo e médio prazo.
* **Uso de IA:** Seja transparente e específico — em quais partes você usou IA para ajudar (geração de queries SQL, estrutura do servidor MCP, etc.), e onde você fez revisão crítica ou ajustes manuais
---
## ⚙️ Instruções de Execução
O projeto deve ser o mais autosuficiente possível. Forneça instruções claras de:
1. Como subir o banco de dados com o Docker Compose fornecido.
2. Como instalar as dependências e iniciar o Servidor MCP.
3. Como executar o Client CLI e começar a interagir com a inteligência de BI.
---
