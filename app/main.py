"""FastAPI Application - Aula 3: E2E e Mutação"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database import engine, get_db
from app.models import ProdutoDB, Base
from app.schemas import ProdutoCreate, ProdutoResponse, SearchFilters
from app.external_service import validar_preco, ExternalServiceError

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    yield


app = FastAPI(title="API Busca 3", lifespan=lifespan)


@app.post("/produtos", status_code=status.HTTP_201_CREATED, response_model=ProdutoResponse)
async def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    """Cria um novo produto após validação de preço"""

    try:
        await validar_preco(produto.preco)
    except ExternalServiceError as e:
        raise HTTPException(status_code=503, detail=f"Serviço externo: {str(e)}")

    novo_produto = ProdutoDB(
        nome=produto.nome,
        descricao=produto.descricao,
        categoria=produto.categoria,
        preco=produto.preco
    )
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto


@app.get("/produtos", response_model=list[ProdutoResponse])
async def listar_produtos(db: Session = Depends(get_db)):
    """Lista todos os produtos"""
    return db.query(ProdutoDB).all()


@app.get("/produtos/{produto_id}", response_model=ProdutoResponse)
async def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    """Obtém um produto específico"""
    produto = db.query(ProdutoDB).filter(ProdutoDB.id == produto_id).first()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    return produto


@app.post("/produtos/search", response_model=list[ProdutoResponse])
async def buscar_produtos(filtros: SearchFilters, db: Session = Depends(get_db)):
    """Busca produtos por nome, descrição ou categoria"""
    query = db.query(ProdutoDB)

    if filtros.nome:
        query = query.filter(ProdutoDB.nome.ilike(f"%{filtros.nome}%"))

    if filtros.descricao:
        query = query.filter(ProdutoDB.descricao.ilike(f"%{filtros.descricao}%"))

    if filtros.categoria:
        query = query.filter(ProdutoDB.categoria.ilike(f"%{filtros.categoria}%"))

    if filtros.preco_minimo is not None:
        query = query.filter(ProdutoDB.preco >= filtros.preco_minimo)

    if filtros.preco_maximo is not None:
        query = query.filter(ProdutoDB.preco <= filtros.preco_maximo)

    resultados = query.all()

    if not resultados:
        raise HTTPException(status_code=404, detail="Nenhum produto encontrado")

    return resultados


@app.put("/produtos/{produto_id}", response_model=ProdutoResponse)
async def atualizar_produto(produto_id: int, produto_update: ProdutoCreate, db: Session = Depends(get_db)):
    """Atualiza um produto existente"""
    produto = db.query(ProdutoDB).filter(ProdutoDB.id == produto_id).first()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    try:
        await validar_preco(produto_update.preco)
    except ExternalServiceError as e:
        raise HTTPException(status_code=503, detail=f"Serviço externo: {str(e)}")

    produto.nome = produto_update.nome
    produto.descricao = produto_update.descricao
    produto.categoria = produto_update.categoria
    produto.preco = produto_update.preco

    db.commit()
    db.refresh(produto)
    return produto


@app.delete("/produtos/{produto_id}")
async def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    """Deleta um produto"""
    produto = db.query(ProdutoDB).filter(ProdutoDB.id == produto_id).first()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    db.delete(produto)
    db.commit()
    return {"mensagem": "Produto deletado com sucesso"}
