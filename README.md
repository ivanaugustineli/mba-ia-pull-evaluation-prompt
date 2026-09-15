# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith
**MBA em Engenharia de Software com IA — FullCycle**

---

## 📌 Visão Geral do Projeto

Este projeto implementa um pipeline completo e automatizado para o ciclo de vida de Engenharia de Prompts aplicado à conversão de relatos de bugs em User Stories ágeis de alta qualidade. 

O fluxo contempla:
1. **Pull automatizado** do prompt inicial de baixa qualidade (`v1`) hospedado no LangSmith Prompt Hub.
2. **Engenharia e otimização de prompts (`v2`)** aplicando técnicas consagradas: *Role Prompting*, *Few-Shot Learning* e *Skeleton of Thought* / *Chain of Thought*.
3. **Bateria de testes unitários automatizados** com `pytest` para validação estrutural de schemas, personas, formato BDD e ausência de resíduos (`TODO`).
4. **Push público** do prompt otimizado para o LangSmith Prompt Hub com versionamento semântico e metadados estruturados.
5. **Avaliação quantitativa com LLM-as-a-Judge** utilizando o LangSmith contra um dataset balanceado de 15 casos reais de bugs, validando aprovação com notas $\ge 0.80$ (80%) em **todas as 5 métricas obrigatórias**.

---

## 🎯 Resultados Finais da Avaliação

### Tabela Comparativa: Prompt Inicial (v1) vs Prompt Otimizado (v2)

| Métrica | Benchmark V1 (Baixa Qualidade) | Versão V2 (Otimizada) | Meta Mínima | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Helpfulness** | 0.45 | **0.88** | 0.80 | ✅ APROVADO |
| **Correctness** | 0.52 | **0.84** | 0.80 | ✅ APROVADO |
| **F1-Score** | 0.48 | **0.81** | 0.80 | ✅ APROVADO |
| **Clarity** | 0.50 | **0.90** | 0.80 | ✅ APROVADO |
| **Precision** | 0.46 | **0.86** | 0.80 | ✅ APROVADO |
| **MÉDIA GERAL** | 0.4820 | **0.8568** | 0.80 | ✅ **APROVADO** |

> **Critério Estrito:** Todas as 5 métricas atingiram pontuações superiores a **0.80 individualmente**, superando o limiar de aprovação exigido no desafio.

### 🔗 Links Oficiais e Evidências no LangSmith

- **Prompt Hub V2 (Público):** [ivan-augustineli/bug_to_user_story_v2](https://smith.langchain.com/hub/ivan-augustineli/bug_to_user_story_v2)
- **Dashboard de Execuções e Tracing:** [LangSmith Project: mba_ia_fc](https://smith.langchain.com/projects/mba_ia_fc)
- **Dataset Avaliado:** `mba_ia_fc-eval` (15 exemplos: 5 simples, 7 médios, 3 complexos)

---

## 🧠 Técnicas Aplicadas (Fase 2 - Otimização)

A versão inicial (`prompts/bug_to_user_story_v1.yml`) apresentava deficiências graves: ausência de persona, repetição desnecessária da variável `{bug_report}` no system prompt e user prompt, instruções vagas ("crie uma user story a partir dele"), falta de exemplos de entrada/saída e nenhum direcionamento sobre critérios de aceitação em BDD.

Na versão otimizada (`prompts/bug_to_user_story_v2.yml`), foram aplicadas as seguintes técnicas:

### 1. Role Prompting & Persona Especializada
- **Definição:** Atribuição explícita de papel técnico e profissional de alto nível.
- **Justificativa:** O modelo precisa calibrar o tom e vocabulário técnico para produzir requisitos ágeis de nível profissional para engenharia de software, evitando respostas genéricas ou amadoras.
- **Aplicação no Prompt:**
  ```text
  Você é um Product Manager sênior e especialista em engenharia de requisitos ágeis com sólida bagagem técnica.
  Sua responsabilidade é analisar relatos de bugs e convertê-los em User Stories claras, de alto valor de negócio e diretamente acionáveis pelo time de engenharia.
  ```

### 2. Few-Shot Learning (Exemplos Canônicos de Demonstração)
- **Definição:** Fornecimento de múltiplos pares de entrada/saída ideais dentro do System Prompt.
- **Justificativa:** O Few-Shot Learning guia o LLM quanto ao padrão estilístico exato esperado pelo avaliador (sintaxe BDD, divisão proporcional de seções e nomenclatura técnica).
- **Aplicação no Prompt:** Foram incluídos 3 exemplos completos cobrindo todo o espectro de complexidade do dataset:
  - **Exemplo 1 (Simples - UI/UX):** Foco em formulário/botão com critérios diretos de BDD.
  - **Exemplo 2 (Médio - Integração/Backend):** Bug com HTTP 500 em webhooks, demonstrando a necessidade de incluir a seção `Contexto Técnico:` (endpoint, gateway, causa raiz).
  - **Exemplo 3 (Complexo - Sistêmico):** Falhas críticas de checkout com XSS, timeout e race conditions, exemplificando a estrutura multi-seção (`=== USER STORY PRINCIPAL ===`, `=== CRITÉRIOS DE ACEITAÇÃO ===` agrupados por área, `=== CRITÉRIOS TÉCNICOS ===`, `=== CONTEXTO DO BUG ===` e `=== TASKS TÉCNICAS SUGERIDAS ===`).

### 3. Skeleton of Thought & Chain of Thought (Estruturação em Etapas Proporcionais)
- **Definição:** Decomposição estruturada do problema em etapas analíticas lógicas antes de emitir a especificação final.
- **Justificativa:** Casos de bugs variam drasticamente em escopo. Um bug simples não deve ter seções vazias desnecessárias, enquanto um bug complexo precisa de decomposição arquitetural completa.
- **Aplicação no Prompt:**
  - Diretrizes explícitas para classificação do nível de complexidade (Simples vs Médio vs Complexo).
  - Obrigatoriedade da fórmula ágil canônica: `Como [persona], eu quero [ação], para que [benefício]`.
  - Critérios de aceitação estritamente em sintaxe Gherkin/BDD (`Dado que...`, `Quando...`, `Então...`, `E...`).

### 4. Regras Negativas de Precisão e Supressão de Ruído Conversacional
- **Definição:** Imposição de restrições rígidas quanto a preâmbulos e conclusões.
- **Justificativa:** As métricas de *Clarity*, *Precision* e *F1-Score* penalizam ruídos irrelevantes (ex: *"Com certeza, aqui está sua User Story:"*).
- **Aplicação no Prompt:**
  ```text
  - NÃO inclua preâmbulos, cumprimentos, introduções ou conclusões.
  - Inicie imediatamente com a User Story gerada.
  - Mantenha total fidelidade aos fatos citados no relato do bug (códigos HTTP, endpoints, tabelas, queries, métricas de tempo, valores monetários).
  ```

---

## 🏗️ Estrutura do Repositório

```text
mba-ia-pull-evaluation-prompt/
├── .env                      # Variáveis de ambiente configuradas
├── .env.example              # Template das variáveis de ambiente
├── requirements.txt          # Dependências do projeto
├── README.md                 # Documentação oficial e relatório de resultados
│
├── prompts/
│   ├── bug_to_user_story_v1.yml  # Prompt inicial de baixa qualidade baixado via pull_prompts.py
│   └── bug_to_user_story_v2.yml  # Prompt otimizado com Role Prompting, Few-Shot e Skeleton of Thought
│
├── datasets/
│   └── bug_to_user_story.jsonl   # Dataset oficial com 15 casos (5 simples, 7 médios, 3 complexos)
│
├── src/
│   ├── pull_prompts.py       # Faz pull de leonanluppi/bug_to_user_story_v1 e salva em YAML
│   ├── push_prompts.py       # Valida e publica ivan-augustineli/bug_to_user_story_v2 público no Hub
│   ├── evaluate.py           # Orquestra a execução das avaliações no LangSmith (core FullCycle)
│   ├── metrics.py            # Definição das 5 métricas de avaliação (core FullCycle)
│   └── utils.py              # Funções utilitárias (core FullCycle)
│
└── tests/
    └── test_prompts.py       # 6 testes unitários automatizados com pytest
```

---

## 🧪 Validações Automatizadas (`pytest`)

O arquivo `tests/test_prompts.py` valida 6 requisitos de integridade do prompt `v2`:

1. `test_prompt_has_system_prompt`: Garante existência e preenchimento não-vazio do system prompt.
2. `test_prompt_has_role_definition`: Assegura a persona ("Product Manager" / "Especialista em Produto").
3. `test_prompt_mentions_format`: Valida menção explícita a Markdown e sintaxe BDD ("Dado", "Quando", "Então").
4. `test_prompt_has_few_shot_examples`: Confirma múltiplos exemplos demonstrativos completos.
5. `test_prompt_no_todos`: Bloqueia resíduos de desenvolvimento (`[TODO]` ou `TODO`).
6. `test_minimum_techniques`: Valida se `techniques_applied` lista no mínimo 2 técnicas formais no YAML.

### Execução dos Testes:
```bash
pytest tests/test_prompts.py -v
```

**Resultado Obtido:**
```text
tests/test_prompts.py::TestPrompts::test_prompt_has_system_prompt PASSED [ 16%]
tests/test_prompts.py::TestPrompts::test_prompt_has_role_definition PASSED [ 33%]
tests/test_prompts.py::TestPrompts::test_prompt_mentions_format PASSED   [ 50%]
tests/test_prompts.py::TestPrompts::test_prompt_has_few_shot_examples PASSED [ 66%]
tests/test_prompts.py::TestPrompts::test_prompt_no_todos PASSED          [ 83%]
tests/test_prompts.py::TestPrompts::test_minimum_techniques PASSED       [100%]

============================== 6 passed in 0.09s ==============================
```

---

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos
- Python 3.9+ instalado (testado com Python 3.13)
- Conta e API Key no [LangSmith](https://smith.langchain.com)
- Chave de API da [OpenAI](https://platform.openai.com) ou [Google AI Studio](https://aistudio.google.com)

### 2. Criação e Ativação do Ambiente Virtual

```bash
# Criação do ambiente virtual
python -m venv venv

# Ativação no Windows (PowerShell)
.\venv\Scripts\activate

# Ativação no Linux / macOS
source venv/bin/activate

# Instalação das dependências
pip install -r requirements.txt
```

### 3. Configuração das Variáveis de Ambiente

Crie o arquivo `.env` a partir do `.env.example`:

```ini
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=sua_chave_langsmith
LANGCHAIN_API_KEY=sua_chave_langsmith
LANGSMITH_PROJECT=mba_ia_fc

# Seu username público no LangSmith Prompt Hub
USERNAME_LANGSMITH_HUB=seu_username

# Configuração do LLM (OpenAI recomendada para avaliação estável)
OPENAI_API_KEY=sua_chave_openai
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
EVAL_MODEL=gpt-4o

# Ou para Google Gemini:
# GOOGLE_API_KEY=sua_chave_gemini
# LLM_PROVIDER=google
# LLM_MODEL=gemini-2.5-flash
# EVAL_MODEL=gemini-2.5-flash
```

### 4. Execução do Fluxo Completo

#### Passo 1: Fazer o Pull do Prompt Inicial (v1)
```bash
python src/pull_prompts.py
```
> Faz o pull de `leonanluppi/bug_to_user_story_v1` do Hub e salva em `prompts/bug_to_user_story_v1.yml`.

#### Passo 2: Executar os Testes Unitários de Validação do Prompt (v2)
```bash
pytest tests/test_prompts.py -v
```
> Valida os 6 testes de conformidade estrutural e de técnicas em `prompts/bug_to_user_story_v2.yml`.

#### Passo 3: Fazer o Push do Prompt Otimizado (v2) para o LangSmith Hub
```bash
python src/push_prompts.py
```
> Valida os metadados e publica `{USERNAME_LANGSMITH_HUB}/bug_to_user_story_v2` como **público** no Hub.

#### Passo 4: Executar a Avaliação Automática
```bash
python -X utf8 src/evaluate.py
```
> Avalia os 15 casos de teste contra o prompt v2 publicado no Hub e calcula as 5 métricas.

---

## 📊 Log de Saída da Avaliação Oficial

```text
==================================================
AVALIAÇÃO DE PROMPTS OTIMIZADOS
==================================================

Provider: openai
Modelo Principal: gpt-4o-mini
Modelo de Avaliação: gpt-4o

Criando dataset de avaliação: mba_ia_fc-eval...
   ✓ Carregados 15 exemplos do arquivo datasets/bug_to_user_story.jsonl
   ✓ Dataset criado com 15 exemplos

======================================================================
PROMPTS PARA AVALIAR
======================================================================

🔍 Avaliando: ivan-augustineli/bug_to_user_story_v2
   Puxando prompt do LangSmith Hub: ivan-augustineli/bug_to_user_story_v2
   ✓ Prompt carregado com sucesso
   Dataset: 15 exemplos
   Avaliando exemplos...
      [1/15] F1:0.75 Clarity:0.90 Precision:0.90
      [2/15] F1:0.75 Clarity:0.85 Precision:0.90
      [3/15] F1:1.00 Clarity:0.95 Precision:1.00
      [4/15] F1:0.65 Clarity:0.90 Precision:0.90
      [5/15] F1:0.75 Clarity:0.95 Precision:0.90
      [6/15] F1:0.85 Clarity:0.90 Precision:0.90
      [7/15] F1:0.87 Clarity:0.90 Precision:0.90
      [8/15] F1:0.75 Clarity:0.95 Precision:0.90
      [9/15] F1:0.65 Clarity:0.90 Precision:0.67
      [10/15] F1:1.00 Clarity:1.00 Precision:1.00
      [11/15] F1:0.80 Clarity:0.80 Precision:0.67
      [12/15] F1:0.80 Clarity:0.80 Precision:0.83
      [13/15] F1:0.83 Clarity:0.85 Precision:0.90
      [14/15] F1:0.80 Clarity:0.90 Precision:0.90
      [15/15] F1:0.91 Clarity:0.90 Precision:0.67

==================================================
Prompt: ivan-augustineli/bug_to_user_story_v2
==================================================

Métricas Derivadas:
  - Helpfulness: 0.88 ✓
  - Correctness: 0.84 ✓

Métricas Base:
  - F1-Score: 0.81 ✓
  - Clarity: 0.90 ✓
  - Precision: 0.86 ✓

--------------------------------------------------
📊 MÉDIA GERAL: 0.8568
--------------------------------------------------

✅ STATUS: APROVADO - Todas as métricas >= 0.8

==================================================
RESUMO FINAL
==================================================

Prompts avaliados: 1
Aprovados: 1
Reprovados: 0

✅ Todos os prompts atingiram todas as métricas >= 0.8!
```