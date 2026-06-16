"""SQLAlchemy ORM Models"""
from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class ProdutoDB(Base):
    """Tabela de produtos no banco de dados"""
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False, index=True)
    descricao = Column(String, nullable=False)
    categoria = Column(String, nullable=False, index=True)
    preco = Column(Float, nullable=False)

    def __repr__(self):
        return f"<ProdutoDB(id={self.id}, nome='{self.nome}', preco={self.preco})>"
