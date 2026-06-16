"""
Unit Tests - Aula 3
5 testes unitários focados em validação Pydantic
(Copiado da Aula 2)
"""
import pytest
from pydantic import ValidationError
from app.schemas import ProdutoCreate


class TestProdutoCreateValidation:
    """Testes unitários para validação de ProdutoCreate"""

    def test_produto_valido(self):
        """Testa criação de produto com dados válidos"""
        produto = ProdutoCreate(
            nome="Notebook",
            descricao="Notebook Dell i7",
            categoria="Eletrônicos",
            preco=3500.00
        )
        assert produto.nome == "Notebook"
        assert produto.preco == 3500.00

    def test_produto_preco_zero_invalido(self):
        """Testa que preço zero é rejeitado"""
        with pytest.raises(ValidationError):
            ProdutoCreate(
                nome="Produto",
                descricao="Descrição",
                categoria="Categoria",
                preco=0
            )

    def test_produto_preco_negativo_invalido(self):
        """Testa que preço negativo é rejeitado"""
        with pytest.raises(ValidationError):
            ProdutoCreate(
                nome="Produto",
                descricao="Descrição",
                categoria="Categoria",
                preco=-100.00
            )

    def test_produto_nome_vazio_invalido(self):
        """Testa que nome vazio é rejeitado"""
        with pytest.raises(ValidationError):
            ProdutoCreate(
                nome="",
                descricao="Descrição",
                categoria="Categoria",
                preco=100.00
            )

    def test_produto_descricao_vazia_invalida(self):
        """Testa que descrição vazia é rejeitada"""
        with pytest.raises(ValidationError):
            ProdutoCreate(
                nome="Produto",
                descricao="",
                categoria="Categoria",
                preco=100.00
            )
