"""Módulo de repositórios"""

from .cliente_repository import ClienteRepository
from .produto_repository import ProdutoRepository
from .pedido_repository import PedidoRepository
from .item_repository import ItemPedidoRepository
from .gasto_repository import GastoRepository
from .insumo_repository import InsumoRepository

__all__ = [
    "ClienteRepository",
    "ProdutoRepository", 
    "PedidoRepository",
    "ItemPedidoRepository",
    "GastoRepository",
    "InsumoRepository"
]
