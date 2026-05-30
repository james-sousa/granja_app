"""
Granja Manager
Sistema de Gestão Completo para Granjas
"""

__version__ = "1.0.0"
__author__ = "Granja Manager Team"

from .database import db, Migrations, Seed
from .services import (
    ClienteService,
    ProdutoService,
    PedidoService,
    EstoqueService,
    GastoService,
    DashboardService,
    FinanceiroService,
)
from .utils import Validators, Formatters, setup_logging

__all__ = [
    "db",
    "Migrations",
    "Seed",
    "ClienteService",
    "ProdutoService",
    "PedidoService",
    "EstoqueService",
    "GastoService",
    "DashboardService",
    "FinanceiroService",
    "Validators",
    "Formatters",
    "setup_logging",
]
