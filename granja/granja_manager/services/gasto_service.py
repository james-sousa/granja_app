"""Serviço de Gastos"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict
import logging
from ..models import Gasto
from ..database.repositories import GastoRepository

logger = logging.getLogger(__name__)


class GastoService:
    """Serviço para gerenciar gastos e despesas."""

    def __init__(self):
        self.gasto_repo = GastoRepository()

    def criar_gasto(self, descricao: str, categoria: str, valor: float) -> Gasto:
        """Cria um novo gasto.
        
        Args:
            descricao: Descrição do gasto
            categoria: Categoria do gasto
            valor: Valor do gasto
            
        Returns:
            Gasto criado
        """
        if not descricao or not descricao.strip():
            raise ValueError("Descrição é obrigatória")
        if valor < 0:
            raise ValueError("Valor não pode ser negativo")
        
        gasto = Gasto(
            id=str(uuid.uuid4()),
            descricao=descricao.strip(),
            categoria=categoria.strip() if categoria else "Outros",
            valor=valor
        )
        
        # Valida
        valido, msg = gasto.validar()
        if not valido:
            raise ValueError(msg)
        
        gasto_id = self.gasto_repo.create(gasto)
        logger.info(f"Gasto criado: {descricao}")
        return self.gasto_repo.find_by_id(gasto_id)

    def atualizar_gasto(self, gasto_id: str, descricao: str, categoria: str, valor: float) -> bool:
        """Atualiza um gasto existente."""
        if valor < 0:
            raise ValueError("Valor não pode ser negativo")
        
        gasto = self.gasto_repo.find_by_id(gasto_id)
        if not gasto:
            raise ValueError(f"Gasto {gasto_id} não encontrado")
        
        gasto.descricao = descricao.strip()
        gasto.categoria = categoria.strip() if categoria else "Outros"
        gasto.valor = valor
        
        resultado = self.gasto_repo.update(gasto)
        logger.info(f"Gasto atualizado: {gasto_id}")
        return resultado

    def obter_gasto(self, gasto_id: str) -> Optional[Gasto]:
        """Obtém um gasto pelo ID."""
        return self.gasto_repo.find_by_id(gasto_id)

    def listar_gastos(self) -> List[Gasto]:
        """Lista todos os gastos."""
        return self.gasto_repo.find_all()

    def pesquisar_gastos(self, query: str) -> List[Gasto]:
        """Pesquisa gastos por descrição ou categoria."""
        return self.gasto_repo.search(query)

    def deletar_gasto(self, gasto_id: str) -> bool:
        """Deleta um gasto."""
        resultado = self.gasto_repo.delete(gasto_id)
        if resultado:
            logger.info(f"Gasto deletado: {gasto_id}")
        return resultado

    def obter_gastos_por_categoria(self, categoria: str) -> List[Gasto]:
        """Obtém gastos de uma categoria específica."""
        return self.gasto_repo.find_by_categoria(categoria)

    def obter_gastos_mes(self, mes: int = None, ano: int = None) -> List[Gasto]:
        """Obtém gastos do mês especificado."""
        if mes is None:
            mes = datetime.now().month
        if ano is None:
            ano = datetime.now().year
        
        gastos = self.listar_gastos()
        return [g for g in gastos if g.data.month == mes and g.data.year == ano]

    def total_gastos_dia(self) -> float:
        """Calcula o total de gastos do dia atual."""
        hoje = datetime.now().date()
        gastos = self.listar_gastos()
        return sum(g.valor for g in gastos if g.data.date() == hoje)

    def total_gastos_mes(self, mes: int = None, ano: int = None) -> float:
        """Calcula o total de gastos do mês."""
        gastos = self.obter_gastos_mes(mes, ano)
        return sum(g.valor for g in gastos)

    def gastos_por_categoria_mes(self, mes: int = None, ano: int = None) -> Dict[str, float]:
        """Retorna gastos agrupados por categoria no mês."""
        gastos = self.obter_gastos_mes(mes, ano)
        resultado = {}
        
        for gasto in gastos:
            if gasto.categoria not in resultado:
                resultado[gasto.categoria] = 0.0
            resultado[gasto.categoria] += gasto.valor
        
        return resultado

    def top_categorias_gastos(self, limite: int = 5) -> List[tuple]:
        """Retorna as top categorias com mais gastos.
        
        Returns:
            Lista de tuplas (categoria, total)
        """
        por_categoria = self.gastos_por_categoria_mes()
        return sorted(por_categoria.items(), key=lambda x: x[1], reverse=True)[:limite]
