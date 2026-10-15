# Produtividade em obras - MVP acadêmico

Prova de conceito desenvolvida para o Projeto Integrador em Computação IV. O
objetivo é demonstrar a coleta, o armazenamento e a análise de dados operacionais
de uma obra, incluindo uma previsão simples de produtividade com aprendizagem de
máquina.

Este repositório contém o backend do protótipo. A entrada de telemetria é simulada
por API, permitindo demonstrar o fluxo sem depender de um equipamento IoT real.

## O que o protótipo demonstra

- cadastro de obras, equipes, serviços e equipamentos;
- apontamento manual de produção e horas trabalhadas;
- recebimento simulado de telemetria de equipamentos;
- cálculo automático de produtividade por `área / horas trabalhadas`;
- previsão com `RandomForestRegressor` a partir do histórico;
- indicadores resumidos para consumo por um dashboard;
- painel administrativo do Django;
- geração automática de uma base fictícia para apresentação.

## Tecnologias

- Python 3.13
- Django 6.1
- Django REST Framework
- pandas
- scikit-learn
- PostgreSQL

## Estrutura

```text
.
|-- manage.py
|-- projeto/                         # Configurações e URLs principais
|-- produtividade/
|   |-- management/commands/
|   |   `-- gerar_dados_demo.py      # Massa de dados para demonstração
|   |-- migrations/                  # Estrutura do banco versionada
|   |-- admin.py                     # Cadastros no Django Admin
|   |-- ml.py                        # Treinamento e previsão
|   |-- models.py                    # Entidades do protótipo
|   |-- serializers.py               # Validação dos dados da API
|   |-- tests.py                     # Testes do fluxo principal
|   |-- urls.py                      # Rotas da aplicação
|   `-- views.py                     # CRUD, previsão e indicadores
`-- requirements.txt
```

## Como executar

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Preencha o arquivo `.env` com os dados do PostgreSQL:

```dotenv
DB_NAME=nome_do_banco
DB_USER=usuario_do_banco
DB_PASSWORD=senha_do_banco
DB_HOST=servidor_do_banco
DB_PORT=5432
```

O PostgreSQL é obrigatório. Com o banco configurado, execute:

```powershell
python manage.py migrate
python manage.py gerar_dados_demo
python manage.py runserver
```

O painel estará em `http://127.0.0.1:8000/` e a API em
`http://127.0.0.1:8000/api/`.

Para utilizar o painel administrativo:

```powershell
python manage.py createsuperuser
```

Depois, acesse `http://127.0.0.1:8000/admin/`.

## Endpoints principais

Todos os cadastros oferecem `GET`, `POST`, `PUT`, `PATCH` e `DELETE` por meio do
Django REST Framework.

| Rota | Finalidade |
|---|---|
| `/api/obras/` | Cadastro de obras |
| `/api/equipes/` | Cadastro de equipes |
| `/api/servicos/` | Cadastro de serviços |
| `/api/equipamentos/` | Cadastro de equipamentos |
| `/api/registros/` | Apontamentos de produtividade |
| `/api/telemetria/` | Leituras simuladas de IoT |
| `/api/resumo/` | Indicadores para o dashboard |
| `/api/prever/` | Previsão de produtividade |

### Registrar produtividade

O campo `produtividade` é opcional. Quando omitido, o sistema calcula o valor por
`area / horas_trabalhadas`.

```json
{
  "obra": 1,
  "equipe": 1,
  "servico": 1,
  "equipamento": 1,
  "area": 120,
  "horas_trabalhadas": 8,
  "horas_equipamento": 6.5,
  "tempo_ocioso": 0.8,
  "condicao_trabalho": 3,
  "origem": "manual"
}
```

A condição de trabalho aceita `1` (ruim), `2` (regular) ou `3` (boa). A origem
aceita `manual` ou `iot`.

### Simular telemetria

```json
{
  "equipamento": 1,
  "obra": 1,
  "horas_operacao": 7.5,
  "tempo_ocioso": 0.8,
  "producao": 125
}
```

### Solicitar uma previsão

São necessários pelo menos 10 registros históricos. O comando
`gerar_dados_demo` cria 20 registros prontos para essa demonstração.

```json
{
  "area": 150,
  "horas": 8,
  "condicao": 3,
  "equipe": 1,
  "servico": 1,
  "obra": 1,
  "equipamento": 1,
  "horas_equipamento": 7,
  "tempo_ocioso": 0.5
}
```

Exemplo de resposta:

```json
{
  "produtividade_prevista": 17.42,
  "erro_medio": 1.83,
  "registros_utilizados": 20
}
```

## Testes

```powershell
python manage.py test
```

Os testes cobrem o cálculo automático, a quantidade mínima de dados, a previsão e
o endpoint de indicadores.

## Limites assumidos para o protótipo

- utiliza exclusivamente PostgreSQL;
- a telemetria é enviada pela API, simulando um ESP32;
- o dashboard é intencionalmente simples e voltado apenas à demonstração;
- o modelo é treinado no momento da previsão, solução suficiente para a pequena
  base acadêmica, mas não indicada para produção;
- autenticação, permissões avançadas e automação de infraestrutura estão fora do
  escopo deste MVP.
