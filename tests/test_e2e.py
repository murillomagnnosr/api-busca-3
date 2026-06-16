"""
End-to-End Tests - Aula 3
Testa fluxos completos de usuário, não apenas funções isoladas.
"""
import pytest


class TestFluxoCriacaoEBusca:
    """Fluxo E2E: criar produtos → buscar → atualizar → deletar"""

    def test_fluxo_completo_produto(self, client):
        """
        Teste E2E completo:
        1. Criar 3 produtos
        2. Buscar por nome
        3. Atualizar um
        4. Deletar um
        5. Verificar estado final
        """
        # 1. Criar 3 produtos
        produto1 = {
            "nome": "Notebook Dell",
            "descricao": "Notebook 15 polegadas",
            "categoria": "Computadores",
            "preco": 3500.00
        }
        response1 = client.post("/produtos", json=produto1)
        assert response1.status_code == 201
        id_produto1 = response1.json()["id"]

        produto2 = {
            "nome": "Mouse Logitech",
            "descricao": "Mouse sem fio",
            "categoria": "Periféricos",
            "preco": 89.90
        }
        response2 = client.post("/produtos", json=produto2)
        assert response2.status_code == 201
        id_produto2 = response2.json()["id"]

        produto3 = {
            "nome": "Teclado Mecânico",
            "descricao": "Teclado RGB",
            "categoria": "Periféricos",
            "preco": 450.00
        }
        response3 = client.post("/produtos", json=produto3)
        assert response3.status_code == 201
        id_produto3 = response3.json()["id"]

        # 2. Listar todos (deve ter 3)
        response_list = client.get("/produtos")
        assert response_list.status_code == 200
        assert len(response_list.json()) == 3

        # 3. Buscar por categoria "Periféricos" (deve trazer 2)
        busca = {
            "categoria": "Periféricos"
        }
        response_search = client.post("/produtos/search", json=busca)
        assert response_search.status_code == 200
        resultados = response_search.json()
        assert len(resultados) == 2
        nomes = [p["nome"] for p in resultados]
        assert "Mouse Logitech" in nomes
        assert "Teclado Mecânico" in nomes

        # 4. Buscar por faixa de preço (50 < preço < 1000)
        busca_preco = {
            "preco_minimo": 50,
            "preco_maximo": 1000
        }
        response_preco = client.post("/produtos/search", json=busca_preco)
        assert response_preco.status_code == 200
        resultados_preco = response_preco.json()
        assert len(resultados_preco) == 2
        for p in resultados_preco:
            assert 50 <= p["preco"] <= 1000

        # 5. Atualizar produto1 (Notebook)
        atualizacao = {
            "nome": "Notebook Dell XPS",
            "descricao": "Notebook 15 polegadas - versão XPS",
            "categoria": "Computadores",
            "preco": 4200.00
        }
        response_update = client.put(f"/produtos/{id_produto1}", json=atualizacao)
        assert response_update.status_code == 200
        assert response_update.json()["nome"] == "Notebook Dell XPS"
        assert response_update.json()["preco"] == 4200.00

        # 6. Obter produto1 para verificar se foi atualizado
        response_get = client.get(f"/produtos/{id_produto1}")
        assert response_get.status_code == 200
        assert response_get.json()["nome"] == "Notebook Dell XPS"
        assert response_get.json()["preco"] == 4200.00

        # 7. Deletar produto2 (Mouse)
        response_delete = client.delete(f"/produtos/{id_produto2}")
        assert response_delete.status_code == 200

        # 8. Verificar que produto2 não existe mais
        response_get_deleted = client.get(f"/produtos/{id_produto2}")
        assert response_get_deleted.status_code == 404

        # 9. Listar finais (deve ter 2, não 3)
        response_final_list = client.get("/produtos")
        assert response_final_list.status_code == 200
        assert len(response_final_list.json()) == 2

    def test_fluxo_multiplos_filtros(self, client):
        """Teste E2E: aplicar múltiplos filtros combinados"""
        # Criar 5 produtos com diferentes características
        produtos = [
            {"nome": "Monitor Samsung", "descricao": "4K 27\"", "categoria": "Monitores", "preco": 1200.00},
            {"nome": "Monitor Dell", "descricao": "Full HD 24\"", "categoria": "Monitores", "preco": 600.00},
            {"nome": "Webcam Logitech", "descricao": "1080p", "categoria": "Webcams", "preco": 250.00},
            {"nome": "Headset Gamer", "descricao": "7.1 Surround", "categoria": "Áudio", "preco": 350.00},
            {"nome": "SSD Samsung", "descricao": "1TB NVMe", "categoria": "Armazenamento", "preco": 800.00},
        ]

        for p in produtos:
            response = client.post("/produtos", json=p)
            assert response.status_code == 201

        # Filtro 1: Apenas Monitores (2 resultados)
        busca1 = {"categoria": "Monitores"}
        result1 = client.post("/produtos/search", json=busca1)
        assert len(result1.json()) == 2

        # Filtro 2: Monitores entre 500-1000 (1 resultado - Dell)
        busca2 = {
            "categoria": "Monitores",
            "preco_minimo": 500,
            "preco_maximo": 1000
        }
        result2 = client.post("/produtos/search", json=busca2)
        assert len(result2.json()) == 1
        assert result2.json()[0]["nome"] == "Monitor Dell"

        # Filtro 3: Tudo entre 300-900 (3 resultados)
        busca3 = {
            "preco_minimo": 300,
            "preco_maximo": 900
        }
        result3 = client.post("/produtos/search", json=busca3)
        assert len(result3.json()) == 3

        # Filtro 4: Busca por nome "Samsung" (2 resultados)
        busca4 = {"nome": "Samsung"}
        result4 = client.post("/produtos/search", json=busca4)
        assert len(result4.json()) == 2

    def test_fluxo_erro_criacao_atualizar(self, client, produto_base):
        """Teste E2E: tentativa de criar com erro, depois atualizar com sucesso"""
        # Tentar criar com preço inválido (deve falhar validação Pydantic)
        produto_invalido = {
            "nome": "Produto",
            "descricao": "Desc",
            "categoria": "Cat",
            "preco": -100.00  # Inválido
        }
        response_error = client.post("/produtos", json=produto_invalido)
        assert response_error.status_code == 422

        # Contar produtos (ainda 1 - o base)
        response_list1 = client.get("/produtos")
        assert len(response_list1.json()) == 1

        # Atualizar produto base com dados válidos
        atualizacao = {
            "nome": produto_base.nome + " Atualizado",
            "descricao": "Nova descrição",
            "categoria": "Nova Categoria",
            "preco": 899.99
        }
        response_update = client.put(f"/produtos/{produto_base.id}", json=atualizacao)
        assert response_update.status_code == 200
        assert response_update.json()["preco"] == 899.99

        # Tentar atualizar com preço inválido
        atualizacao_invalida = {
            "nome": "Teste",
            "descricao": "Teste",
            "categoria": "Teste",
            "preco": 0  # Inválido
        }
        response_error_update = client.put(f"/produtos/{produto_base.id}", json=atualizacao_invalida)
        assert response_error_update.status_code == 422
