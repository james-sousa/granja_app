"""Serviço de Estoque"""

import logging
from typing import Optional
from ..database.repositories import ProdutoRepository

logger = logging.getLogger(__name__)


class EstoqueService:
    """Serviço para gerenciar estoque de produtos."""

    def __init__(self):
        self.produto_repo = ProdutoRepository()

    def validar_estoque(self, produto_id: str, quantidade: int) -> bool:
        """Valida se há estoque suficiente."""
        produto = self.produto_repo.find_by_id(produto_id)
        if not produto:
            return False
        return produto.estoque >= quantidade

    def remover_estoque(self, produto_id: str, quantidade: int) -> bool:
        """Remove quantidade do estoque (entrada de pedido).
        
        Args:
            produto_id: ID do produto
            quantidade: Quantidade a remover
            
        Returns:
            True se bem-sucedido
        """
        if not self.validar_estoque(produto_id, quantidade):
            logger.error(f"Estoque insuficiente para produto {produto_id}")
            return False
        
        resultado = self.produto_repo.atualizar_estoque(produto_id, -quantidade)
        if resultado:
            logger.info(f"Estoque removido: {produto_id} - {quantidade} unidades")
        return resultado

    def adicionar_estoque(self, produto_id: str, quantidade: int) -> bool:
        """Adiciona quantidade ao estoque (devolução de pedido).
        
        Args:
            produto_id: ID do produto
            quantidade: Quantidade a adicionar
            
        Returns:
            True se bem-sucedido
        """
        resultado = self.produto_repo.atualizar_estoque(produto_id, quantidade)
        if resultado:
            logger.info(f"Estoque adicionado: {produto_id} - {quantidade} unidades")
        return resultado

    def obter_estoque(self, produto_id: str) -> Optional[int]:
        """Obtém a quantidade em estoque de um produto."""
        produto = self.produto_repo.find_by_id(produto_id)
        return produto.estoque if produto else None

    def produtos_com_estoque_baixo(self, limite: int = 10) -> list:
        """Retorna produtos com estoque abaixo do limite."""
        produtos = self.produto_repo.find_all()
        return [p for p in produtos if p.estoque < limite and p.ativo]

    def gerar_alerta_estoque(self) -> dict:
        """Gera alertas de estoque baixo."""
        alertas = {}
        baixos = self.produtos_com_estoque_baixo()
        
        for produto in baixos:
            alertas[produto.id] = {
                "nome": produto.nome,
                "estoque": produto.estoque,
                "alerta": "Estoque baixo - Reposição necessária"
            }
        
        return alertas
