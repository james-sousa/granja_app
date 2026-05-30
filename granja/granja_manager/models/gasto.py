"""Modelo de Gasto"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Gasto:
    """Representa um gasto/despesa da granja."""
    id: str
    descricao: str
    categoria: str
    valor: float
    data: Optional[datetime] = None

    CATEGORIAS_VALIDAS = [
        "Insumos",
        "Energia",
        "Funcionários",
        "Medicamentos",
        "Transporte",
        "Outros"
    ]

    def __post_init__(self):
        if self.data is None:
            self.data = datetime.now()

    def validar(self) -> tuple[bool, str]:
        """Valida os dados do gasto."""
        if not self.descricao or not self.descricao.strip():
            return False, "Descrição é obrigatória"
        if self.valor < 0:
            return False, "Valor não pode ser negativo"
        if self.categoria not in self.CATEGORIAS_VALIDAS:
            return False, f"Categoria inválida. Válidas: {', '.join(self.CATEGORIAS_VALIDAS)}"
        return True, ""
