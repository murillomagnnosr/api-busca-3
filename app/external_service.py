"""External API service for price validation"""
import httpx
import asyncio


class ExternalServiceError(Exception):
    """Erro ao comunicar com serviço externo"""
    pass


async def validar_preco(preco: float) -> bool:
    """
    Valida preço através de API externa.
    Em produção, isto seria uma chamada real.
    """
    if preco > 10000:
        raise ExternalServiceError("Preço acima do limite máximo permitido")

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await asyncio.sleep(0.01)
            return True
    except httpx.TimeoutException:
        raise ExternalServiceError("Serviço respondeu lentamente (timeout)")
    except httpx.RequestError:
        raise ExternalServiceError("Falha ao conectar com serviço externo")
