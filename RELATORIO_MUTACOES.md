# Relatório de Testes de Mutação — Aula 3

## Visão Geral

Este documento detalha cada **mutante** (bug potencial) que os testes de mutação são projetados para detectar. Um mutante representa uma pequena alteração no código que causaria um bug real.

## Objetivo

Demonstrar que **cobertura de testes** ≠ **força dos testes**. Mesmo com 100% de cobertura, bugs passam despercebidos se os testes não forem *específicos o suficiente*.

---

## 1. Mutações de Validação de Preço

### Mutante 1.1: `preco > 0` → `preco >= 0`

**Local:** `app/schemas.py` — `ProdutoCreate.validar_preco()`

**Bug:** Permite preço zero, violando regra de negócio.

**Teste que detecta:** `test_mutacao_preco_zero_deve_falhar()`

```python
# Código correto
if v <= 0:
    raise ValueError("Preço deve ser maior que zero")

# Mutante (BUG)
if v < 0:
    raise ValueError("Preço deve ser maior que zero")
    # Permite v = 0! ⚠️
```

**Impacto:** Produto grátis seria criado sem autorização.

---

### Mutante 1.2: Remover validação de preço negativo

**Local:** `app/schemas.py` — `ProdutoCreate.validar_preco()`

**Bug:** Aceita preço negativo (crédito ao invés de débito).

**Teste que detecta:** `test_mutacao_preco_negativo_deve_falhar()`

**Cenário:** 
```json
{"preco": -100.00}  // Sem validação, seria aceito! ⚠️
```

**Impacto:** Usuário recebe crédito ao invés de pagar.

---

### Mutante 1.3: `preco > 10000` → `preco >= 10000`

**Local:** `app/external_service.py` — `validar_preco()`

**Bug:** Aceita preço exatamente 10000, violando limite.

**Teste que detecta:** `test_mutacao_preco_maximo_limite_critico()`

```python
# Código correto
if preco > 10000:
    raise ExternalServiceError(...)

# Mutante (BUG)
if preco >= 10000:  # Rejeita 10000
    raise ExternalServiceError(...)
    # ERRADO! Deveria permitir 10000
```

**Impacto:** Produtos legítimos são rejeitados.

---

### Mutante 1.4: Remover limite de preço máximo

**Local:** `app/external_service.py`

**Bug:** Sem limite, qualquer preço é aceito.

**Teste que detecta:** `test_mutacao_preco_maximo_limite_critico()`

**Cenário:**
```python
preco = 50000.00  # Sem limite, seria aceito! ⚠️
```

**Impacto:** Risco de fraude, produtos super caros são cadastrados.

---

## 2. Mutações em Filtros de Busca

### Mutante 2.1: `ilike()` → `like()` (case-sensitive)

**Local:** `app/main.py` — `buscar_produtos()`

**Bug:** Busca é case-sensitive, não encontra variações.

**Teste que detecta:** `test_mutacao_filtro_nome_case_insensitive()`

```python
# Código correto
query = query.filter(ProdutoDB.nome.ilike(f"%{filtros.nome}%"))

# Mutante (BUG)
query = query.filter(ProdutoDB.nome.like(f"%{filtros.nome}%"))
# Agora "NOTEBOOK" não encontra "notebook"! ⚠️
```

**Cenário:**
```
Banco: "notebook dell"
Busca: "NOTEBOOK"
Resultado correto: encontra ✓
Resultado com mutante: não encontra ✗
```

**Impacto:** Usuário não consegue encontrar produtos.

---

### Mutante 2.2: `preco >= minimo` → `preco > minimo` (filtro mínimo)

**Local:** `app/main.py` — `buscar_produtos()`

**Bug:** Produtos com preço **exatamente igual** ao mínimo são excluídos.

**Teste que detecta:** `test_mutacao_filtro_preco_minimo_inclusivo()`

```python
# Código correto
if filtros.preco_minimo is not None:
    query = query.filter(ProdutoDB.preco >= filtros.preco_minimo)

# Mutante (BUG)
if filtros.preco_minimo is not None:
    query = query.filter(ProdutoDB.preco > filtros.preco_minimo)
    # Produto com preco=500 não aparece na busca com minimo=500! ⚠️
```

**Cenário:**
```
Produto: R$ 500
Filtro mínimo: R$ 500
Resultado correto: encontra ✓
Resultado com mutante: não encontra ✗
```

**Impacto:** Dados desaparecem para o usuário.

---

### Mutante 2.3: `preco <= maximo` → `preco < maximo` (filtro máximo)

**Local:** `app/main.py` — `buscar_produtos()`

**Bug:** Produtos com preço **exatamente igual** ao máximo são excluídos.

**Teste que detecta:** `test_mutacao_filtro_preco_maximo_inclusivo()`

**Cenário:**
```
Produto: R$ 1000
Filtro máximo: R$ 1000
Resultado correto: encontra ✓
Resultado com mutante: não encontra ✗
```

**Impacto:** Faixa de preço não é respeitada.

---

### Mutante 2.4: Remover exceção 404 em busca vazia

**Local:** `app/main.py` — `buscar_produtos()`

**Bug:** Retorna lista vazia `[]` ao invés de erro 404.

**Teste que detecta:** `test_mutacao_busca_sem_resultados_retorna_404()`

```python
# Código correto
if not resultados:
    raise HTTPException(status_code=404, detail="...")
return resultados

# Mutante (BUG)
return resultados  # Sem validação!
# Busca sem resultados retorna [], não 404! ⚠️
```

**Impacto:** Cliente não consegue distinguir "sem resultados" de erro.

---

## 3. Mutações de Persistência

### Mutante 3.1: Remover `db.commit()` na criação

**Local:** `app/main.py` — `criar_produto()`

**Bug:** Dados não são salvos no banco de dados.

**Teste que detecta:** `test_mutacao_criacao_nao_persiste_sem_commit()`

```python
# Código correto
db.add(novo_produto)
db.commit()
db.refresh(novo_produto)
return novo_produto

# Mutante (BUG)
db.add(novo_produto)
# db.commit()  ← REMOVIDO!
db.refresh(novo_produto)
return novo_produto
# Produto não é salvo! ⚠️
```

**Impacto:** Dados perdidos na próxima requisição.

---

### Mutante 3.2: Não atualizar um dos campos

**Local:** `app/main.py` — `atualizar_produto()`

**Bug:** Campo não é atualizado, fica com valor antigo.

**Teste que detecta:** `test_mutacao_atualizacao_persiste_alteracoes()`

```python
# Código correto
produto.nome = produto_update.nome
produto.descricao = produto_update.descricao
produto.categoria = produto_update.categoria
produto.preco = produto_update.preco

# Mutante (BUG)
produto.nome = produto_update.nome
# produto.descricao = produto_update.descricao  ← REMOVIDO!
produto.categoria = produto_update.categoria
produto.preco = produto_update.preco
# Descrição fica com valor antigo! ⚠️
```

**Impacto:** Atualização incompleta, dados inconsistentes.

---

### Mutante 3.3: Remover `db.delete()` na deleção

**Local:** `app/main.py` — `deletar_produto()`

**Bug:** Produto não é deletado, só retorna mensagem.

**Teste que detecta:** `test_mutacao_delecao_realmente_remove()`

```python
# Código correto
db.delete(produto)
db.commit()
return {"mensagem": "Produto deletado com sucesso"}

# Mutante (BUG)
# db.delete(produto)  ← REMOVIDO!
db.commit()
return {"mensagem": "Produto deletado com sucesso"}
# Produto ainda existe no banco! ⚠️
```

**Impacto:** "Deletado" não significa deletado.

---

## 4. Mutações de Lógica Condicional

### Mutante 4.1: Inversão de lógica em `obter_produto()`

**Local:** `app/main.py` — `obter_produto()`

**Bug:** Lança erro quando produto **existe**, não quando não existe.

**Teste que detecta:** `test_mutacao_notfound_check_produto_nao_existe()`

```python
# Código correto
if not produto:
    raise HTTPException(status_code=404, ...)
return produto

# Mutante (BUG)
if produto:  # Lógica invertida!
    raise HTTPException(status_code=404, ...)
return produto
# Erro quando produto EXISTE! ⚠️
```

**Impacto:** Endpoint sempre falha.

---

### Mutante 4.2: Inversão de lógica em `buscar_produtos()`

**Local:** `app/main.py` — `buscar_produtos()`

**Bug:** Lança 404 quando **encontra** resultados, ao invés de quando não encontra.

**Teste que detecta:** `test_mutacao_notfound_check_na_busca()`

**Impacto:** Busca bem-sucedida retorna erro.

---

### Mutante 4.3: Inversão de lógica em `atualizar_produto()`

**Local:** `app/main.py` — `atualizar_produto()`

**Bug:** Permite atualizar produto inexistente, nega produto existente.

**Teste que detecta:** `test_mutacao_notfound_check_update_produto_nao_existe()`

**Impacto:** Validação invertida, dados corrompidos.

---

## 5. Mutações de Status Code

### Mutante 5.1: `201 Created` → `200 OK` em POST

**Local:** `app/main.py` — `criar_produto()`

**Bug:** Usa status code errado para recurso criado.

**Teste que detecta:** `test_mutacao_criacao_retorna_201_nao_200()`

```python
# Código correto
@app.post("/produtos", status_code=status.HTTP_201_CREATED)

# Mutante (BUG)
@app.post("/produtos", status_code=status.HTTP_200_OK)
# Retorna 200 ao invés de 201! ⚠️
```

**Impacto:** Cliente não consegue distinguir GET de POST.

---

### Mutante 5.2: GET retorna status code errado

**Local:** `app/main.py` — `listar_produtos()`

**Bug:** GET retorna status diferente de 200.

**Teste que detecta:** `test_mutacao_listar_retorna_200()`

---

### Mutante 5.3: Remover 404 em recurso inexistente

**Local:** `app/main.py` — `obter_produto()`

**Bug:** Retorna 200 mesmo quando produto não existe.

**Teste que detecta:** `test_mutacao_notfound_retorna_404()`

```python
# Resultado com mutante
GET /produtos/99999
→ 200 OK com null/vazio  ⚠️ ERRADO

# Resultado correto
GET /produtos/99999
→ 404 Not Found  ✓ CORRETO
```

**Impacto:** Cliente não consegue detectar erros.

---

## 📊 Resumo de Mutantes

| # | Categoria | Bug | Teste | Impacto |
|---|-----------|-----|-------|---------|
| 1.1 | Validação | `>` → `>=` preço | `test_mutacao_preco_zero_deve_falhar` | Produto grátis |
| 1.2 | Validação | Sem rejeição negativo | `test_mutacao_preco_negativo_deve_falhar` | Crédito indevido |
| 1.3 | Validação | `>` → `>=` limite | `test_mutacao_preco_maximo_limite_critico` | Produto rejeitado |
| 2.1 | Filtro | `ilike` → `like` | `test_mutacao_filtro_nome_case_insensitive` | Produto não encontrado |
| 2.2 | Filtro | `>=` → `>` mínimo | `test_mutacao_filtro_preco_minimo_inclusivo` | Dados desaparecem |
| 2.3 | Filtro | `<=` → `<` máximo | `test_mutacao_filtro_preco_maximo_inclusivo` | Faixa errada |
| 2.4 | Filtro | Sem 404 | `test_mutacao_busca_sem_resultados_retorna_404` | Erro indistinto |
| 3.1 | Persist | Sem `commit()` | `test_mutacao_criacao_nao_persiste_sem_commit` | Dados perdidos |
| 3.2 | Persist | Campo não atualiza | `test_mutacao_atualizacao_persiste_alteracoes` | Inconsistência |
| 3.3 | Persist | Sem `delete()` | `test_mutacao_delecao_realmente_remove` | Não deleta |
| 4.1 | Lógica | `if not` → `if` | `test_mutacao_notfound_check_produto_nao_existe` | Erro invertido |
| 4.2 | Lógica | `if not` → `if` | `test_mutacao_notfound_check_na_busca` | Sucesso = erro |
| 4.3 | Lógica | `if not` → `if` | `test_mutacao_notfound_check_update_produto_nao_existe` | Validação errada |
| 5.1 | Status | 201 → 200 | `test_mutacao_criacao_retorna_201_nao_200` | GET confundido com POST |
| 5.2 | Status | GET status errado | `test_mutacao_listar_retorna_200` | Erro silencioso |
| 5.3 | Status | Sem 404 | `test_mutacao_notfound_retorna_404` | Erro indistinto |

---

## 🎯 Aprendizado Chave

### Cobertura ≠ Força

Você pode ter **100% cobertura** mas ainda deixar **todos esses bugs passarem** se os testes forem genéricos demais.

**Exemplo genérico (FRACO):**
```python
def test_criar_produto(self, client):
    response = client.post("/produtos", json={...})
    assert response.status_code in [200, 201]  # ← Muito genérico!
    # Passaria com mutante 5.1 (201 → 200)
```

**Exemplo específico (FORTE):**
```python
def test_mutacao_criacao_retorna_201_nao_200(self, client):
    response = client.post("/produtos", json={...})
    assert response.status_code == 201  # ← Exato!
    # Falha com mutante 5.1
```

### Testes Devem Ser Desconfortáveis

Se um pequeno typo (`>` para `>=`) não quebra seus testes, o teste é **fraco**.

Bons testes:
- ✅ Testam casos limites (0, -1, máximo)
- ✅ Validam status codes exatos
- ✅ Verificam dados reais persistidos
- ✅ Detectam lógica invertida

---

## 🚀 Próximos Passos

1. **Rodar mutmut** (ferramente real de mutação):
   ```powershell
   mutmut run
   mutmut results
   ```

2. **Adicionar mais mutantes** para casos de negócio
3. **Aula 4:** Quality Gates e Observabilidade

---

**Desenvolvido para fins educacionais — demonstração de força em testes.**
