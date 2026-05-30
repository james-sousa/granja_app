"""Serviço de Dashboard"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging
from .pedido_service import PedidoService
from .gasto_service import GastoService
from .produto_service import ProdutoService
from .cliente_service import ClienteService

logger = logging.getLogger(__name__)


class DashboardService:
    """Serviço para gerar métricas do dashboard."""

    def __init__(self):
        self.pedido_service = PedidoService()
        self.gasto_service = GastoService()
        self.produto_service = ProdutoService()
        self.cliente_service = ClienteService()

    def obter_metricas_dia(self) -> Dict:
        """Obtém métricas do dia atual."""
        return {
            "vendas_dia": self.pedido_service.total_vendas_dia(),
            "pedidos_dia": self.pedido_service.contar_pedidos_dia(),
            "gastos_dia": self.gasto_service.total_gastos_dia(),
        }

    def obter_metricas_semana(self) -> Dict:
        """Obtém métricas da semana atual."""
        hoje = datetime.now()
        # Segunda-feira é 0
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        
        # Vendas da semana
        pedidos = self.pedido_service.listar_pedidos()
        pedidos_semana = [p for p in pedidos 
                         if p.data.date() >= inicio_semana.date()]
        vendas_semana = sum(p.total for p in pedidos_semana)
        
        # Gastos da semana
        gastos = self.gasto_service.listar_gastos()
        gastos_semana = sum(g.valor for g in gastos 
                           if g.data.date() >= inicio_semana.date())
        
        # Lucro
        lucro_semana = vendas_semana - gastos_semana
        
        # Pedidos da semana
        pedidos_count = len(pedidos_semana)
        
        return {
            "vendas_semana": vendas_semana,
            "gastos_semana": gastos_semana,
            "lucro_semana": lucro_semana,
            "pedidos_semana": pedidos_count,
        }

    def obter_metricas_mes(self) -> Dict:
        """Obtém métricas do mês atual."""
        mes = datetime.now().month
        ano = datetime.now().year
        
        # Vendas do mês
        pedidos = self.pedido_service.listar_pedidos()
        pedidos_mes = [p for p in pedidos 
                      if p.data.month == mes and p.data.year == ano]
        vendas_mes = sum(p.total for p in pedidos_mes)
        
        # Gastos do mês
        gastos_mes = self.gasto_service.total_gastos_mes(mes, ano)
        
        # Lucro
        lucro_mes = vendas_mes - gastos_mes
        
        return {
            "vendas_mes": vendas_mes,
            "gastos_mes": gastos_mes,
            "lucro_mes": lucro_mes,
        }

    def obter_top_produtos(self, limite: int = 5) -> List[Tuple]:
        """Obtém os produtos mais vendidos.
        
        Returns:
            Lista de tuplas (Produto, quantidade_vendida)
        """
        pedidos = self.pedido_service.listar_pedidos()
        ranking = {}
        
        for pedido in pedidos:
            for item in pedido.itens:
                if item.produto_id not in ranking:
                    ranking[item.produto_id] = 0
                ranking[item.produto_id] += item.quantidade
        
        # Ordena e pega top
        top_ids = sorted(ranking.items(), key=lambda x: x[1], reverse=True)[:limite]
        
        resultado = []
        for produto_id, quantidade in top_ids:
            produto = self.produto_service.obter_produto(produto_id)
            if produto:
                resultado.append((produto, quantidade))
        
        return resultado

    def obter_clientes_ativos(self) -> int:
        """Retorna número de clientes que fizeram pedidos."""
        return self.cliente_service.total_clientes_ativos()

    def obter_total_produtos_ativos(self) -> int:
        """Retorna número de produtos ativos."""
        return len(self.produto_service.listar_produtos())

    def obter_pedidos_pendentes_clientes(self) -> int:
        """Retorna número de clientes com pagamentos pendentes."""
        grupos = self.cliente_service.obter_clientes_com_pendencias()
        return len(grupos)

    def obter_total_pendente(self) -> float:
        """Retorna o total de valores pendentes de receber."""
        grupos = self.cliente_service.obter_clientes_com_pendencias()
        return sum(g["total_pendente"] for g in grupos)

    def gerar_relatorio_completo(self) -> Dict:
        """Gera relatório completo para dashboard."""
        hoje = datetime.now()
        
        return {
            "data_relatorio": hoje.isoformat(),
            "metricas_dia": self.obter_metricas_dia(),
            "metricas_semana": self.obter_metricas_semana(),
            "metricas_mes": self.obter_metricas_mes(),
            "top_produtos": self.obter_top_produtos(),
            "clientes_ativos": self.obter_clientes_ativos(),
            "produtos_ativos": self.obter_total_produtos_ativos(),
            "clientes_pendentes": self.obter_pedidos_pendentes_clientes(),
            "total_pendente": self.obter_total_pendente(),
        }

    def obter_vendas_ultimos_dias(self, dias: int = 30) -> Dict[str, float]:
        """Obtém vendas dos últimos N dias.
        
        Returns:
            Dicionário com data como chave e vendas como valor
        """
        pedidos = self.pedido_service.listar_pedidos()
        vendas_por_dia = {}
        
        for i in range(dias):
            data = (datetime.now() - timedelta(days=i)).date()
            vendas_por_dia[str(data)] = 0.0
        
        for pedido in pedidos:
            data_str = str(pedido.data.date())
            if data_str in vendas_por_dia:
                vendas_por_dia[data_str] += pedido.total
        
        # Ordena por data
        return dict(sorted(vendas_por_dia.items()))

    def obter_gastos_ultimos_dias(self, dias: int = 30) -> Dict[str, float]:
        """Obtém gastos dos últimos N dias.
        
        Returns:
            Dicionário com data como chave e gastos como valor
        """
        gastos = self.gasto_service.listar_gastos()
        gastos_por_dia = {}
        
        for i in range(dias):
            data = (datetime.now() - timedelta(days=i)).date()
            gastos_por_dia[str(data)] = 0.0
        
        for gasto in gastos:
            data_str = str(gasto.data.date())
            if data_str in gastos_por_dia:
                gastos_por_dia[data_str] += gasto.valor
        
        # Ordena por data
        return dict(sorted(gastos_por_dia.items()))
