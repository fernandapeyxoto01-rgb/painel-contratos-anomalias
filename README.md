# 📊 Painel de Contratos Anômalos — Ceará Transparente

## 🚀 Sobre o Projeto

Este projeto consiste em um dashboard interativo desenvolvido em Python com Streamlit, com o objetivo de analisar contratos públicos e identificar possíveis anomalias com base em níveis de risco.

Os dados são armazenados em um banco PostgreSQL na nuvem (Supabase) e atualizados automaticamente por meio de um pipeline de dados utilizando Apache Airflow.

Além disso, o sistema conta com um assistente de Inteligência Artificial para consultas e análises dos dados.

---


---

## 🧰 Tecnologias Utilizadas

* Python
* Streamlit
* PostgreSQL (Supabase)
* Apache Airflow
* Pandas
* Plotly
* OpenAI API

---

## 📊 Funcionalidades

* ✔️ Visualização de contratos por nível de risco (Alto, Médio e Baixo)
* ✔️ Indicadores consolidados (KPIs)
* ✔️ Filtros dinâmicos
* ✔️ Ranking de fornecedores por valor total
* ✔️ Distribuição dos contratos por nível de risco
* ✔️ Análise de valores por risco
* ✔️ Assistente de IA integrado para consultas
* ✔️ Atualização automática dos dados via pipeline (Airflow)

---

## ⚙️ Como Executar o Projeto

### 1. Clonar o repositório

```bash
git clone [link do repositório]
cd painel-contratos-anomalias
```

### 2. Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Configure as credenciais do banco e da API utilizando o `secrets.toml` no Streamlit ou variáveis de ambiente.

### 5. Executar o projeto

```bash
streamlit run app.py
```

---

## 🔄 Pipeline de Dados

O projeto utiliza o Apache Airflow para:

* Extração de dados
* Transformação
* Carga no banco PostgreSQL (Supabase)

Isso garante que o dashboard esteja sempre atualizado com dados recentes.

---

## 🎯 Objetivo

Auxiliar na identificação de possíveis irregularidades em contratos públicos, fornecendo uma visão analítica e interativa para apoio à tomada de decisão.

---

## 👩‍💻 Autora

Fernanda Peixoto

---
