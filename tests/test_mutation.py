"""
Mutation Testing - Aula 3
Testes projetados para detectar bugs causados por mutações simples no código.
Cada mutante representa um bug potencial.
"""
import pytest


class TestMutacaoValidacaoPreco:
    """Detecta mutações em validações de preço"""

    def test_mutacao_preco_zero_deve_falhar(self, client):
        """
        Mutante: preco > 0 → preco >= 0
        Sem este teste, preço zero seria aceito.
        """
        produto = {
            "nome": "Produto Zero",
            "descricao": "Teste",
            "categoria": "Teste",
            "preco": 0
        }
        response = client.post("/produtos", json=produto)
        assert response.status_code == 422, "Preço 0 deve ser rejeitado"

    def test_mutacao_preco_negativo_deve_falhar(self, client):
        """
        Mutante: preco > 0 → preco < 0 (ou removido)
        Sem este teste, preço negativo seria aceito.
        """
        produto = {
            "nome": "Produto Negativo",
            "descricao": "Teste",
            "categoria": "Teste",
            "preco": -50.00
        }
        response = client.post("/produtos", json=produto)
        assert response.status_code == 422, "Preço negativo deve ser rejeitado"

    def test_mutacao_preco_maximo_limite_critico(self, client):
        """
        Mutante: preco > 10000 → preco >= 10000
        Bug: Se limite fosse >= ao invés de >, preço 10001 seria aceito quando deve ser rejeitado.
        """
        produto = {
            "nome": "Produto Caro",
            "descricao": "Muito caro",
            "categoria": "Premium",
            "preco": 10001.00
        }
        response = client.post("/produtos", json=produto)
        assert response.status_code == 503, "Preço 10001 deve ser rejeitado por limite"

    def test_mutacao_preco_dentro_limite_deve_passar(self, client):
        """
        Teste complementar: garante que preços válidos são aceitos.
        Detecta se limite foi alterado para algo muito restrictivo.
        """
        produto = {
            "nome": "Produto OK",
            "descricao": "Preço dentro do limite",
            "categoria": "Normal",
            "preco": 9999.99
        }
        response = client.post("/produtos", json=produto)
        assert response.status_code == 201, "Preço 9999.99 deve ser aceito"

    def test_mutacao_preco_exatamente_10000_deve_passar(self, client):
        """
        Teste: Preço 10000 é limite máximo inclusivo.
        Detecta se limite foi alterado de > para >=.
        """
        produto = {
            "nome": "Produto Limite",
            "descricao": "Preço no limite exato",
            "categoria": "Normal",
            "preco": 10000.00
        }
        response = client.post("/produtos", json=produto)
        assert response.status_code == 201, "Preço 10000.00 deve ser aceito (está no limite)"


class TestMutacaoBusca:
    """Detecta mutações na lógica de busca e filtros"""

    def test_mutacao_filtro_nome_case_insensitive(self, client):
        """
        Mutante: ilike() → like() (case-sensitive)
        Bug: Busca por "NOTEBOOK" não encontraria "notebook" se fosse case-sensitive.
        """
        # Criar produto com nome minúsculo
        produto = {
            "nome": "notebook dell",
            "descricao": "Computador portátil",
            "categoria": "Computadores",
            "preco": 3000.00
        }
        client.post("/produtos", json=produto)

        # Buscar com uppercase (ilike deve encontrar)
        busca = {"nome": "NOTEBOOK"}
        response = client.post("/produtos/search", json=busca)
        assert response.status_code == 200
        assert len(response.json()) > 0, "Busca case-insensitive deve funcionar"

    def test_mutacao_filtro_preco_minimo_inclusivo(self, client):
        """
        Mutante: preco >= minimo → preco > minimo
        Bug: Produto com preço exatamente igual ao mínimo seria excluído.
        """
        produto = {
            "nome": "Produto Limite",
            "descricao": "No limite de preço",
            "categoria": "Teste",
            "preco": 500.00
        }
        client.post("/produtos", json=produto)

        # Buscar com preco_minimo = 500 (deve incluir produto com 500)
        busca = {"preco_minimo": 500.00}
        response = client.post("/produtos/search", json=busca)
        assert response.status_code == 200
        assert len(response.json()) > 0, "Filtro >= deve ser inclusivo"

    def test_mutacao_filtro_preco_maximo_inclusivo(self, client):
        """
        Mutante: preco <= maximo → preco < maximo
        Bug: Produto com preço exatamente igual ao máximo seria excluído.
        """
        produto = {
            "nome": "Produto Limite Max",
            "descricao": "No limite máximo de preço",
            "categoria": "Teste",
            "preco": 1000.00
        }
        client.post("/produtos", json=produto)

        # Buscar com preco_maximo = 1000 (deve incluir produto com 1000)
        busca = {"preco_maximo": 1000.00}
        response = client.post("/produtos/search", json=busca)
        assert response.status_code == 200
        assert len(response.json()) > 0, "Filtro <= deve ser inclusivo"

    def test_mutacao_busca_sem_resultados_retorna_404(self, client):
        """
        Mutante: raise HTTPException → return []
        Bug: Se remover a exceção 404, busca sem resultados retornaria lista vazia.
        """
        busca = {"nome": "ProdutoQueNaoExiste"}
        response = client.post("/produtos/search", json=busca)
        assert response.status_code == 404, "Busca sem resultados deve retornar 404"


class TestMutacaoPersistencia:
    """Detecta mutações na persistência de dados"""

    def test_mutacao_criacao_nao_persiste_sem_commit(self, client):
        """
        Mutante: db.commit() → removido
        Bug: Sem commit, dados não seriam salvos no banco.
        """
        produto = {
            "nome": "Produto Teste Commit",
            "descricao": "Teste de persistência",
            "categoria": "Teste",
            "preco": 199.90
        }
        response1 = client.post("/produtos", json=produto)
        assert response1.status_code == 201
        id_produto = response1.json()["id"]

        # Fazer nova requisição para listar (força novo contexto de session)
        response2 = client.get("/produtos")
        assert response2.status_code == 200
        ids = [p["id"] for p in response2.json()]
        assert id_produto in ids, "Produto deve estar persistido"

    def test_mutacao_atualizacao_persiste_alteracoes(self, client, produto_base):
        """
        Mutante: Remover alguma linha de atribuição
        Bug: Atualização não salvaria todos os campos.
        """
        atualizacao = {
            "nome": "Novo Nome",
            "descricao": "Nova Descrição",
            "categoria": "Nova Categoria",
            "preco": 999.99
        }
        response_update = client.put(f"/produtos/{produto_base.id}", json=atualizacao)
        assert response_update.status_code == 200

        # Recuperar e verificar TODOS os campos foram atualizados
        response_get = client.get(f"/produtos/{produto_base.id}")
        assert response_get.status_code == 200
        produto = response_get.json()
        assert produto["nome"] == "Novo Nome"
        assert produto["descricao"] == "Nova Descrição"
        assert produto["categoria"] == "Nova Categoria"
        assert produto["preco"] == 999.99

    def test_mutacao_delecao_realmente_remove(self, client, produto_base):
        """
        Mutante: db.delete() → comentado
        Bug: Delete não removeria o produto.
        """
        # Deletar produto
        response_delete = client.delete(f"/produtos/{produto_base.id}")
        assert response_delete.status_code == 200

        # Tentar acessar (deve 404)
        response_get = client.get(f"/produtos/{produto_base.id}")
        assert response_get.status_code == 404, "Produto deletado não deve existir"

        # Listar (não deve conter o produto)
        response_list = client.get("/produtos")
        ids = [p["id"] for p in response_list.json()]
        assert produto_base.id not in ids, "Produto deletado não deve estar na lista"


class TestMutacaoLogicaCondicional:
    """Detecta mutações em condições lógicas"""

    def test_mutacao_notfound_check_produto_nao_existe(self, client):
        """
        Mutante: if not produto → if produto (logic inversion)
        Bug: Exceção seria lançada quando produto EXISTE ao invés de quando não existe.
        """
        # Tentar acessar produto que não existe
        response = client.get("/produtos/99999")
        assert response.status_code == 404, "Produto inexistente deve retornar 404"

    def test_mutacao_notfound_check_na_busca(self, client):
        """Teste similar para busca - detecta inversão de lógica"""
        # Buscar algo que não existe
        busca = {"nome": "ProdutoFantasma"}
        response = client.post("/produtos/search", json=busca)
        assert response.status_code == 404, "Busca sem resultados deve retornar 404"

    def test_mutacao_notfound_check_update_produto_nao_existe(self, client):
        """
        Mutante: if not produto → if produto
        Bug: Tentativa de atualizar produto inexistente teria resultado oposto.
        """
        atualizacao = {
            "nome": "Teste",
            "descricao": "Teste",
            "categoria": "Teste",
            "preco": 100.00
        }
        response = client.put("/produtos/99999", json=atualizacao)
        assert response.status_code == 404, "Atualizar inexistente deve ser 404"


class TestMutacaoStatusCode:
    """Detecta mutações em status codes HTTP"""

    def test_mutacao_criacao_retorna_201_nao_200(self, client):
        """
        Mutante: status_code=201 → status_code=200
        Bug: Criar produto deveria ser 201 (Created), não 200 (OK).
        """
        produto = {
            "nome": "Produto Novo",
            "descricao": "Teste de status",
            "categoria": "Teste",
            "preco": 299.99
        }
        response = client.post("/produtos", json=produto)
        assert response.status_code == 201, "POST de criação deve retornar 201"

    def test_mutacao_listar_retorna_200(self, client):
        """Verifica que GET retorna 200 (não modificado)"""
        response = client.get("/produtos")
        assert response.status_code == 200, "GET deve retornar 200"

    def test_mutacao_notfound_retorna_404(self, client):
        """Verifica que recurso inexistente retorna 404 (não 200)"""
        response = client.get("/produtos/99999")
        assert response.status_code == 404, "Recurso inexistente deve ser 404"
