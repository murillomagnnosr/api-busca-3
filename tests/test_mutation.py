"""
Mutation Testing - Aula 3
3 testes de mutacao para detectar bugs potenciais
"""
import pytest


class TestMutacaoValidacaoPreco:
    """Detecta mutacoes em validacoes de preco"""

    def test_mutacao_preco_zero_deve_falhar(self, client):
        """Detecta: preco > 0 - preco >= 0"""
        produto = {
            "nome": "Produto Zero",
            "descricao": "Teste",
            "categoria": "Teste",
            "preco": 0
        }
        response = client.post("/produtos", json=produto)
        assert response.status_code == 422

    def test_mutacao_preco_negativo_deve_falhar(self, client):
        """Detecta: preco > 0 - preco < 0 removido"""
        produto = {
            "nome": "Produto Negativo",
            "descricao": "Teste",
            "categoria": "Teste",
            "preco": -50.00
        }
        response = client.post("/produtos", json=produto)
        assert response.status_code == 422

    def test_mutacao_notfound_check(self, client):
        """Detecta: if not produto - if produto (logica invertida)"""
        response = client.get("/produtos/99999")
        assert response.status_code == 404
