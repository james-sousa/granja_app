"""Modelo de Produto"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Produto:
    """Representa um produto disponível na granja."""
    id: str
    nome: str
    preco: float
    estoque: int = 0
    ativo: int = 1
    criado_em: Optional[datetime] = None

    def __post_init__(self):
        if self.criado_em is None:
            self.criado_em = datetime.now()
