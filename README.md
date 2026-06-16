# API Busca 3 — Aula 3: E2E e Testes de Mutação

Projeto educacional FastAPI focado em **testes End-to-End** e **detecção de mutações** para validar força dos testes.

## 📋 Objetivo

Demonstrar que cobertura de testes não é suficiente — é necessário **realmente proteger o comportamento** do sistema. Este projeto implementa:

- ✅ Testes E2E (fluxos completos de usuário)
- ✅ Testes de mutação (detectam bugs potenciais)
- ✅ Validação de status codes HTTP corretos
- ✅ Persistência de dados em SQLite
- ✅ CI/CD automatizado no GitHub

## 🚀 Setup

### 1. Criar ambiente virtual

```powershell
cd C:\Users\muril\api-busca-3
python -m venv .venv
.venv\Scripts\activate.ps1
```

### 2. Instalar dependências

```powershell
pip install -r requirements.txt
```

### 3. Rodar testes

```powershell
pytest -v
pytest --cov=app --cov-report=html  # Com cobertura
```

### 4. Rodar aplicação

```powershell
uvicorn app.main:app --reload
```

Acesse: http://localhost:8000/docs

## 📁 Estrutura

```
api-busca-3/
├── app/
│   ├── main.py              ← Endpoints FastAPI
│   ├── database.py          ← SQLAlchemy config
│   ├── models.py            ← Tabela ProdutoDB
│   ├── schemas.py           ← Validação Pydantic
│   └── external_service.py  ← API externa mockada
├── tests/
│   ├── conftest.py          ← Fixtures pytest
│   ├── test_e2e.py          ← Testes End-to-End
│   └── test_mutation.py     ← Testes de Mutação
├── .github/
│   └── workflows/ci.yml     ← Pipeline GitHub Actions
└── RELATORIO_MUTACOES.md    ← Documentação de mutantes
```

## 🧪 Tipos de Testes

### Testes E2E (test_e2e.py)

Testam fluxos **completos** de usuário, não funções isoladas:

```python
def test_fluxo_completo_produto(self, client):
    # 1. Criar 3 produtos
    # 2. Buscar por categoria
    # 3. Atualizar um
    # 4. Deletar um
    # 5. Verificar estado final
```

**Por que E2E?**
- Testes unitários podem passar mas fluxo inteiro falha
- Integração entre componentes é testada
- Comportamento real do usuário é validado

### Testes de Mutação (test_mutation.py)

Projetados para **detectar bugs** causados por mutações simples:

```python
def test_mutacao_preco_zero_deve_falhar(self, client):
    """Detecta: preco > 0 → preco >= 0"""
    # Sem este teste, preço zero seria aceito
```

**Mutantes inclusos:**
1. **Validação de preço** — zero/negativo/limite
2. **Filtros de busca** — case-sensitive, operadores (< vs <=)
3. **Persistência** — commit removido
4. **Lógica condicional** — inversão de if/not
5. **Status codes** — 201 vs 200, 404 não retornado

## 📊 Executando Testes

### Rodar tudo

```powershell
pytest -v
```

**Saída esperada:**
```
test_e2e.py::TestFluxoCriacaoEBusca::test_fluxo_completo_produto PASSED
test_e2e.py::TestFluxoCriacaoEBusca::test_fluxo_multiplos_filtros PASSED
test_e2e.py::TestFluxoCriacaoEBusca::test_fluxo_erro_criacao_atualizar PASSED
test_mutation.py::TestMutacaoValidacaoPreco::test_mutacao_preco_zero_deve_falhar PASSED
... (mais 20+ mutação tests)
============================= 24 passed in 1.23s ==============================
```

### Apenas E2E

```powershell
pytest tests/test_e2e.py -v
```

### Apenas Mutação

```powershell
pytest tests/test_mutation.py -v
```

## 🔍 Exemplo: Detectando um Mutante

Suponha que alguém **mude** a validação de preço:

```python
# ANTES (correto)
if preco > 0:
    pass

# DEPOIS (mutante - BUG!)
if preco >= 0:  # Permite zero!
    pass
```

O teste `test_mutacao_preco_zero_deve_falhar` **capturaria este bug**:

```python
def test_mutacao_preco_zero_deve_falhar(self, client):
    produto = {"nome": "P", "descricao": "D", "categoria": "C", "preco": 0}
    response = client.post("/produtos", json=produto)
    assert response.status_code == 422  # ← FALHA se mutante existe!
```

## 📈 Cobertura de Testes

| Categoria | Testes | Cobertura |
|-----------|--------|-----------|
| Validação | 3 | Preço (zero, negativo, limite) |
| Filtros | 4 | Nome, categoria, faixa de preço |
| Persistência | 3 | Criar, atualizar, deletar |
| Status codes | 3 | 201, 200, 404 |
| Lógica | 3 | Inversão de condições |
| **Total E2E** | **3 fluxos** | Operações completas |
| **Total Mutação** | **20+ mutantes** | Bugs potenciais |

## 🐛 Relatório de Mutações

Veja `RELATORIO_MUTACOES.md` para documentação detalhada de cada mutante.

## 🔗 Endpoints

```
POST   /produtos           ← Cria produto
GET    /produtos           ← Lista todos
GET    /produtos/{id}      ← Obtém por ID
POST   /produtos/search    ← Busca com filtros
PUT    /produtos/{id}      ← Atualiza
DELETE /produtos/{id}      ← Deleta
```

### Exemplos de Uso

**Criar produto:**
```bash
curl -X POST http://localhost:8000/produtos \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Notebook",
    "descricao": "Computador portátil",
    "categoria": "Eletrônicos",
    "preco": 3500.00
  }'
```

**Buscar com filtros:**
```bash
curl -X POST http://localhost:8000/produtos/search \
  -H "Content-Type: application/json" \
  -d '{
    "categoria": "Eletrônicos",
    "preco_minimo": 1000,
    "preco_maximo": 5000
  }'
```

## 🎯 Aprendizados da Aula 3

1. **E2E vs Unitário**
   - Testes unitários: ✅ função isolada
   - Testes E2E: ✅ fluxo completo do usuário

2. **Força dos Testes**
   - Cobertura ≠ proteção
   - Mutação detecta gaps reais

3. **Boas Práticas**
   - Testar casos limites (0, -1, máximo)
   - Validar status codes (201 vs 200)
   - Operadores inclusivos (>= vs >)

## 📦 Dependências

- **FastAPI** 0.109.0 — Web framework
- **SQLAlchemy** 2.0.25 — ORM
- **Pydantic** 2.9.2 — Validação
- **Pytest** 8.3.3 — Testing framework
- **HTTPx** 0.25.2 — HTTP client async

## 🚀 Próximos Passos

- Aula 4: Observabilidade e Quality Gates
  - Health checks `/health`
  - Logs estruturados
  - Métricas simples
  - Quality Gate criteria

---

**Desenvolvido para fins educacionais — demonstração de qualidade em desenvolvimento de APIs.**
