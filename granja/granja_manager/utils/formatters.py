"""Formatadores para exibição de dados"""

from datetime import datetime
from typing import Optional


class Formatters:
    """Classe com formatadores da aplicação."""

    @staticmethod
    def formato_brl(valor: float) -> str:
        """Formata valor para Real brasileiro.
        
        Ex: 1234.56 -> "R$ 1.234,56"
        """
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @staticmethod
    def formato_telefone(telefone: str) -> str:
        """Formata telefone para exibição.
        
        Ex: "5511987654321" -> "(11) 98765-4321"
        """
        if not telefone:
            return ""
        
        # Remove tudo que não é dígito
        apenas_numeros = "".join(filter(str.isdigit, telefone))
        
        # Remove código do país se presente
        if len(apenas_numeros) == 13 and apenas_numeros.startswith("55"):
            apenas_numeros = apenas_numeros[2:]
        
        # Formata
        if len(apenas_numeros) == 11:
            return f"({apenas_numeros[:2]}) {apenas_numeros[2:7]}-{apenas_numeros[7:]}"
        elif len(apenas_numeros) == 10:
            return f"({apenas_numeros[:2]}) {apenas_numeros[2:6]}-{apenas_numeros[6:]}"
        else:
            return telefone

    @staticmethod
    def formato_data(data: datetime, formato: str = "%d/%m/%Y") -> str:
        """Formata data para exibição.
        
        Args:
            data: Data a formatar
            formato: Formato desejado (padrão: %d/%m/%Y)
        """
        if not data:
            return ""
        return data.strftime(formato)

    @staticmethod
    def formato_data_hora(data: datetime, formato: str = "%d/%m/%Y %H:%M:%S") -> str:
        """Formata data e hora para exibição."""
        if not data:
            return ""
        return data.strftime(formato)

    @staticmethod
    def formato_percentual(valor: float, casas: int = 2) -> str:
        """Formata percentual.
        
        Ex: 0.1234 -> "12,34%"
        """
        return f"{valor * 100:.{casas}f}%".replace(".", ",")

    @staticmethod
    def truncar_texto(texto: str, max_chars: int = 50) -> str:
        """Trunca texto e adiciona reticências se necessário."""
        if len(texto) > max_chars:
            return texto[:max_chars - 3] + "..."
        return texto

    @staticmethod
    def nome_mes(mes: int) -> str:
        """Retorna o nome do mês em português."""
        meses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        return meses[mes - 1] if 1 <= mes <= 12 else ""

    @staticmethod
    def mes_ano_atual() -> str:
        """Retorna "Mês do Ano" atual em português."""
        agora = datetime.now()
        mes = Formatters.nome_mes(agora.month)
        return f"{mes} de {agora.year}"
