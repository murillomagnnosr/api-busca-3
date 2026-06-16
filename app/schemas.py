"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ProdutoCreate(BaseModel):
    """Schema para criar/atualizar produtos"""
    nome: str = Field(..., min_length=1, max_length=200)
    descricao: str = Field(..., min_length=1, max_length=500)
    categoria: str = Field(..., min_length=1, max_length=100)
    preco: float = Field(..., gt=0)

    @field_validator("preco")
    @classmethod
    def validar_preco(cls, v):
        if v <= 0:
            raise ValueError("Preço deve ser maior que zero")
        return round(v, 2)


class ProdutoResponse(BaseModel):
    """Schema para resposta de produtos"""
    id: int
    nome: str
    descricao: str
    categoria: str
    preco: float

    class Config:
        from_attributes = True


class SearchFilters(BaseModel):
    """Schema para filtros de busca"""
    nome: Optional[str] = None
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    preco_minimo: Optional[float] = None
    preco_maximo: Optional[float] = None

    @field_validator("preco_minimo", "preco_maximo", mode="before")
    @classmethod
    def validar_precos(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Preços de filtro devem ser maiores que zero")
        return v
