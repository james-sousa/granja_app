"""Serviço Financeiro"""

from datetime import datetime
from typing import Dict, List
import logging
from .pedido_service import PedidoService
from .gasto_service import GastoService
from .cliente_service import ClienteService

logger = logging.getLogger(__name__)


class FinanceiroService:
    """Serviço para controle financeiro da granja."""

    def __init__(self):
        self.pedido_service = PedidoService()
        self.gasto_service = GastoService()
        self.cliente_service = ClienteService()

    def obter_receita_mes(self, mes: int = None, ano: int = None) -> float:
        """Calcula receita (pedidos pagos) do mês."""
        if mes is None:
            mes = datetime.now().month
        if ano is None:
            ano = datetime.now().year
        
        pedidos = self.pedido_service.listar_pedidos()
        return sum(p.total for p in pedidos 
                  if p.pago and p.data.month == mes and p.data.year == ano)

    def obter_despesa_mes(self, mes: int = None, ano: int = None) -> float:
        """Calcula despesas do mês."""
        return self.gasto_service.total_gastos_mes(mes, ano)

    def obter_lucro_mes(self, mes: int = None, ano: int = None) -> float:
        """Calcula lucro líquido do mês."""
        receita = self.obter_receita_mes(mes, ano)
        despesa = self.obter_despesa_mes(mes, ano)
        return receita - despesa

    def obter_pendencias_totais(self) -> float:
        """Retorna o valor total pendente de recebimento."""
        grupos = self.cliente_service.obter_clientes_com_pendencias()
        return sum(g["total_pendente"] for g in grupos)

    def obter_status_financeiro_mes(self, mes: int = None, ano: int = None) -> Dict:
        """Obtém status financeiro completo do mês."""
        if mes is None:
            mes = datetime.now().month
        if ano is None:
            ano = datetime.now().year
        
        receita = self.obter_receita_mes(mes, ano)
        despesa = self.obter_despesa_mes(mes, ano)
        lucro = self.obter_lucro_mes(mes, ano)
        pendente = self.obter_pendencias_totais()
        
        return {
            "mes": mes,
            "ano": ano,
            "receita": receita,
            "receita_formatada": self._formatar_brl(receita),
            "despesa": despesa,
            "despesa_formatada": self._formatar_brl(despesa),
            "lucro": lucro,
            "lucro_formatada": self._formatar_brl(lucro),
            "pendente": pendente,
            "pendente_formatada": self._formatar_brl(pendente),
            "total_possivel": receita + pendente,
            "margem_lucro": (lucro / receita * 100) if receita > 0 else 0,
        }

    def obter_clientes_pendentes(self) -> List[Dict]:
        """Obtém lista de clientes com pendências."""
        return self.cliente_service.obter_clientes_com_pendencias()

    def obter_previsao_caixa(self, dias: int = 30) -> Dict[str, float]:
        """Calcula previsão de caixa para próximos dias.
        
        Considera pedidos não pagos que podem vencer.
        """
        from datetime import timedelta
        
        pedidos = self.pedido_service.listar_pedidos()
        previsao = {}
        
        for i in range(1, dias + 1):
            data = datetime.now() + timedelta(days=i)
            data_str = str(data.date())
            previsao[data_str] = 0.0
        
        # Adiciona pedidos não pagos (simulando que podem vencer)
        for pedido in pedidos:
            if not pedido.pago:
                # Assume vencimento após 7 dias da criação
                data_vencimento = pedido.data + timedelta(days=7)
                data_str = str(data_vencimento.date())
                if data_str in previsao:
                    previsao[data_str] += pedido.total
        
        return dict(sorted(previsao.items()))

    def gerar_relatorio_financeiro(self) -> Dict:
        """Gera relatório financeiro completo."""
        mes_atual = datetime.now().month
        ano_atual = datetime.now().year
        
        return {
            "periodo": f"{mes_atual}/{ano_atual}",
            "status_mes": self.obter_status_financeiro_mes(mes_atual, ano_atual),
            "clientes_pendentes": self.obter_clientes_pendentes(),
            "num_clientes_pendentes": len(self.obter_clientes_pendentes()),
            "total_pendente": self.obter_pendencias_totais(),
            "previsao_caixa": self.obter_previsao_caixa(),
        }

    @staticmethod
    def _formatar_brl(valor: float) -> str:
        """Formata valor para Real brasileiro."""
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
