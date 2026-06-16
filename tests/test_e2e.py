"""
End-to-End Tests - Aula 3
3 testes E2E cobrindo fluxos completos do usuário
"""
import pytest


class TestFluxoCriacaoEBusca:
    """Fluxo E2E: criar produtos - buscar - atualizar"""

    def test_fluxo_completo_crud(self, client):
        """Teste E2E: criar produto, ler, atualizar e deletar"""
        produto = {
            "nome": "Notebook Dell",
            "descricao": "Notebook 15 polegadas",
            "categoria": "Computadores",
            "preco": 3500.00
        }
        response = client.post("/produtos", json=produto)
        assert response.status_code == 201
        id_produto = response.json()["id"]

        response = client.get(f"/produtos/{id_produto}")
        assert response.status_code == 200
        assert response.json()["nome"] == "Notebook Dell"

        atualizacao = {
            "nome": "Notebook Dell XPS",
            "descricao": "Notebook atualizado",
            "categoria": "Computadores",
            "preco": 4200.00
        }
        response = client.put(f"/produtos/{id_produto}", json=atualizacao)
        assert response.status_code == 200
        assert response.json()["preco"] == 4200.00

        response = client.delete(f"/produtos/{id_produto}")
        assert response.status_code == 200

        response = client.get(f"/produtos/{id_produto}")
        assert response.status_code == 404

    def test_fluxo_busca_por_categoria(self, client):
        """Teste E2E: buscar produtos por categoria"""
        produtos = [
            {"nome": "Monitor", "descricao": "4K", "categoria": "Monitores", "preco": 1200.00},
            {"nome": "Teclado", "descricao": "Mecanico", "categoria": "Perifericos", "preco": 450.00},
            {"nome": "Mouse", "descricao": "Sem fio", "categoria": "Perifericos", "preco": 150.00},
        ]
        for p in produtos:
            assert client.post("/produtos", json=p).status_code == 201

        busca = {"categoria": "Perifericos"}
        result = client.post("/produtos/search", json=busca)
        assert result.status_code == 200
        assert len(result.json()) == 2

    def test_fluxo_validacao_erro(self, client, produto_base):
        """Teste E2E: validacao com erro seguida de atualizacao valida"""
        produto_invalido = {
            "nome": "Produto",
            "descricao": "Desc",
            "categoria": "Cat",
            "preco": -100.00
        }
        response = client.post("/produtos", json=produto_invalido)
        assert response.status_code == 422

        atualizacao = {
            "nome": "Produto Valido",
            "descricao": "Descricao corrigida",
            "categoria": "Categoria",
            "preco": 199.99
        }
        response = client.put(f"/produtos/{produto_base.id}", json=atualizacao)
        assert response.status_code == 200
