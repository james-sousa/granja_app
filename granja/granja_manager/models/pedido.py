"""Modelo de Pedido"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Pedido:
    """Representa um pedido realizado por um cliente."""
    id: str
    cliente_id: str
    data: datetime
    total: float = 0.0
    pago: int = 0  # 0 = não pago, 1 = pago
    concluido: int = 0  # 0 = pendente, 1 = concluído
    itens: List = field(default_factory=list)

    def __post_init__(self):
        if not self.data:
            self.data = datetime.now()

    @property
    def total_calculado(self) -> float:
        """Calcula o total do pedido com base nos itens."""
        return sum(item.subtotal for item in self.itens) if self.itens else self.total
