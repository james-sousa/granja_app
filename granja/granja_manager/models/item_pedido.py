"""Modelo de Item de Pedido"""

from dataclasses import dataclass


@dataclass
class ItemPedido:
    """Representa um item dentro de um pedido."""
    id: str
    pedido_id: str
    produto_id: str
    quantidade: int
    preco_unitario: float

    @property
    def subtotal(self) -> float:
        """Calcula o subtotal do item."""
        return self.quantidade * self.preco_unitario
