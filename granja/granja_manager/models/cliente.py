"""Modelo de Cliente"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Cliente:
    """Representa um cliente da granja.
    
    Clientes são criados automaticamente quando um pedido é realizado.
    Nunca devem ser criados manualmente.
    """
    id: str
    nome: str
    telefone: str
    criado_em: Optional[datetime] = None

    def __post_init__(self):
        if self.criado_em is None:
            self.criado_em = datetime.now()
