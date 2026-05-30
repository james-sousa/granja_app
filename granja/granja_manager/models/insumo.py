"""Modelo de Insumo"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Insumo:
    """Representa um insumo (ração, medicamentos, vacinas, etc)."""
    
    id: str
    nome: str
    unidade: str
    quantidade: float = 0.0
    criado_em: Optional[datetime] = None
    
    def __post_init__(self):
        """Normaliza os dados após inicialização."""
        if isinstance(self.criado_em, str):
            try:
                self.criado_em = datetime.fromisoformat(self.criado_em)
            except (ValueError, TypeError):
                self.criado_em = datetime.now()
        elif self.criado_em is None:
            self.criado_em = datetime.now()
    
    def validar(self) -> tuple[bool, str]:
        """Valida os dados do insumo.
        
        Returns:
            Tupla (válido, mensagem)
        """
        if not self.nome or not self.nome.strip():
            return False, "Nome do insumo é obrigatório"
        
        if not self.unidade or not self.unidade.strip():
            return False, "Unidade é obrigatória"
        
        if self.quantidade < 0:
            return False, "Quantidade não pode ser negativa"
        
        return True, "OK"
