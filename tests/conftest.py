"""Pytest fixtures and configuration"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from app.models import ProdutoDB


@pytest.fixture(scope="function")
def db_engine():
    """Cria engine SQLite em memória para testes"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Cria sessão de banco de dados para testes"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Cria cliente HTTP para testes"""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def produto_base(db_session):
    """Cria um produto base para testes"""
    produto = ProdutoDB(
        nome="Produto Base",
        descricao="Descrição do produto base",
        categoria="Eletrônicos",
        preco=599.90
    )
    db_session.add(produto)
    db_session.commit()
    db_session.refresh(produto)
    return produto
