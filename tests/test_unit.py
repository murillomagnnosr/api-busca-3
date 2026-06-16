"""
Unit Tests - Aula 3
Testes de unidades isoladas (funções, validações, schemas)
Sem HTTP, sem banco de dados - apenas lógica pura.
"""
import pytest
from pydantic import ValidationError
from app.schemas import ProdutoCreate, SearchFilters, ProdutoResponse


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
        with pytest.raises(ValidationError) as exc_info:
            ProdutoCreate(
                nome="Produto",
                descricao="Descrição",
                categoria="Categoria",
                preco=0
            )
        assert "greater than 0" in str(exc_info.value).lower()

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

    def test_produto_categoria_vazia_invalida(self):
        """Testa que categoria vazia é rejeitada"""
        with pytest.raises(ValidationError):
            ProdutoCreate(
                nome="Produto",
                descricao="Descrição",
                categoria="",
                preco=100.00
            )

    def test_produto_nome_muito_longo(self):
        """Testa limite de caracteres do nome"""
        nome_longo = "A" * 201  # Excede max_length=200
        with pytest.raises(ValidationError):
            ProdutoCreate(
                nome=nome_longo,
                descricao="Descrição",
                categoria="Categoria",
                preco=100.00
            )

    def test_produto_descricao_muito_longa(self):
        """Testa limite de caracteres da descrição"""
        desc_longa = "A" * 501  # Excede max_length=500
        with pytest.raises(ValidationError):
            ProdutoCreate(
                nome="Produto",
                descricao=desc_longa,
                categoria="Categoria",
                preco=100.00
            )


class TestSearchFiltersValidation:
    """Testes unitários para validação de SearchFilters"""

    def test_filtro_vazio(self):
        """Testa criação de filtro vazio (todos opcionais)"""
        filtro = SearchFilters()
        assert filtro.nome is None
        assert filtro.preco_minimo is None
        assert filtro.preco_maximo is None

    def test_filtro_apenas_nome(self):
        """Testa filtro com apenas nome"""
        filtro = SearchFilters(nome="Notebook")
        assert filtro.nome == "Notebook"
        assert filtro.preco_minimo is None

    def test_filtro_faixa_preco(self):
        """Testa filtro com faixa de preço"""
        filtro = SearchFilters(
            preco_minimo=100.00,
            preco_maximo=1000.00
        )
        assert filtro.preco_minimo == 100.00
        assert filtro.preco_maximo == 1000.00

    def test_filtro_preco_minimo_negativo_invalido(self):
        """Testa que preço mínimo negativo é rejeitado"""
        with pytest.raises(ValidationError):
            SearchFilters(preco_minimo=-100.00)

    def test_filtro_preco_maximo_negativo_invalido(self):
        """Testa que preço máximo negativo é rejeitado"""
        with pytest.raises(ValidationError):
            SearchFilters(preco_maximo=-100.00)

    def test_filtro_preco_zero_invalido(self):
        """Testa que preço zero é rejeitado"""
        with pytest.raises(ValidationError):
            SearchFilters(preco_minimo=0)

    def test_filtro_todos_campos(self):
        """Testa filtro com todos os campos preenchidos"""
        filtro = SearchFilters(
            nome="Notebook",
            descricao="Dell",
            categoria="Eletrônicos",
            preco_minimo=1000.00,
            preco_maximo=5000.00
        )
        assert filtro.nome == "Notebook"
        assert filtro.descricao == "Dell"
        assert filtro.categoria == "Eletrônicos"
        assert filtro.preco_minimo == 1000.00
        assert filtro.preco_maximo == 5000.00


class TestProdutoResponseSchema:
    """Testes unitários para resposta de produtos"""

    def test_produto_response_criacao(self):
        """Testa criação de ProdutoResponse"""
        produto = ProdutoResponse(
            id=1,
            nome="Notebook",
            descricao="Notebook Dell",
            categoria="Eletrônicos",
            preco=3500.00
        )
        assert produto.id == 1
        assert produto.nome == "Notebook"
        assert produto.preco == 3500.00

    def test_produto_response_serializacao(self):
        """Testa serialização para JSON"""
        produto = ProdutoResponse(
            id=1,
            nome="Mouse",
            descricao="Mouse sem fio",
            categoria="Periféricos",
            preco=150.00
        )
        json_data = produto.model_dump_json()
        assert '"id": 1' in json_data or '"id":1' in json_data
        assert "Mouse" in json_data


class TestPrecoRounding:
    """Testes de arredondamento de preço"""

    def test_preco_com_muitas_casas_decimais(self):
        """Testa que preço com 3+ casas decimais é arredondado"""
        produto = ProdutoCreate(
            nome="Produto",
            descricao="Descrição",
            categoria="Categoria",
            preco=99.9999
        )
        # Deve arredondar para 2 casas decimais
        assert produto.preco == 100.00

    def test_preco_duas_casas_decimais(self):
        """Testa preço com 2 casas decimais"""
        produto = ProdutoCreate(
            nome="Produto",
            descricao="Descrição",
            categoria="Categoria",
            preco=99.99
        )
        assert produto.preco == 99.99

    def test_preco_uma_casa_decimal(self):
        """Testa preço com 1 casa decimal"""
        produto = ProdutoCreate(
            nome="Produto",
            descricao="Descrição",
            categoria="Categoria",
            preco=99.9
        )
        assert produto.preco == 99.90


class TestValidacaoPrecosLimites:
    """Testes de casos limites para preço"""

    def test_preco_muito_pequeno(self):
        """Testa menor preço possível (acima de zero)"""
        produto = ProdutoCreate(
            nome="Produto",
            descricao="Descrição",
            categoria="Categoria",
            preco=0.01
        )
        assert produto.preco == 0.01

    def test_preco_muito_grande(self):
        """Testa preço muito grande"""
        produto = ProdutoCreate(
            nome="Produto",
            descricao="Descrição",
            categoria="Categoria",
            preco=999999.99
        )
        assert produto.preco == 999999.99

    def test_preco_um(self):
        """Testa preço = 1.00"""
        produto = ProdutoCreate(
            nome="Produto",
            descricao="Descrição",
            categoria="Categoria",
            preco=1.00
        )
        assert produto.preco == 1.00


class TestFiltrosOptionals:
    """Testes para campos opcionais dos filtros"""

    def test_filtro_nome_presente(self):
        """Testa filtro com nome presente"""
        filtro = SearchFilters(nome="Test")
        assert filtro.nome == "Test"
        assert filtro.descricao is None

    def test_filtro_multiplos_opcionais(self):
        """Testa combinações de campos opcionais"""
        filtro1 = SearchFilters(nome="Test")
        assert filtro1.nome == "Test"

        filtro2 = SearchFilters(preco_minimo=100)
        assert filtro2.preco_minimo == 100

        filtro3 = SearchFilters(categoria="Cat")
        assert filtro3.categoria == "Cat"
