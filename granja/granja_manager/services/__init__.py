"""Módulo de Serviços"""

from .cliente_service import ClienteService
from .produto_service import ProdutoService
from .pedido_service import PedidoService
from .estoque_service import EstoqueService
from .gasto_service import GastoService
from .dashboard_service import DashboardService
from .financeiro_service import FinanceiroService
from .auth_service import AuthService

__all__ = [
    "ClienteService",
    "ProdutoService",
    "PedidoService",
    "EstoqueService",
    "GastoService",
    "DashboardService",
    "FinanceiroService",
    "AuthService",
]
