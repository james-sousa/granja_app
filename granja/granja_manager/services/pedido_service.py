"""Serviço de Pedidos"""

import uuid
from datetime import datetime
from typing import List, Optional, Tuple
import logging
from ..models import Pedido, ItemPedido, Cliente
from ..database.repositories import PedidoRepository, ProdutoRepository, ClienteRepository
from .cliente_service import ClienteService
from .estoque_service import EstoqueService

logger = logging.getLogger(__name__)


class PedidoService:
    """Serviço para gerenciar pedidos.
    
    Implementa o fluxo obrigatório:
    1. Pedido criado
    2. Verifica cliente (cria se não existir)
    3. Salva pedido
    4. Atualiza estoque
    5. Retorna pedido criado
    """

    def __init__(self):
        self.pedido_repo = PedidoRepository()
        self.produto_repo = ProdutoRepository()
        self.cliente_repo = ClienteRepository()
        self.cliente_service = ClienteService()
        self.estoque_service = EstoqueService()

    def criar_pedido(self, nome_cliente: str, telefone_cliente: str, 
                    itens_data: List[Tuple[str, int, float]]) -> Pedido:
        """Cria um novo pedido com fluxo obrigatório.
        
        Args:
            nome_cliente: Nome do cliente
            telefone_cliente: Telefone do cliente
            itens_data: Lista de tuplas (produto_id, quantidade, preco_unitario)
            
        Returns:
            Pedido criado
            
        Fluxo:
            1. Verifica/cria cliente
            2. Cria itens do pedido
            3. Salva pedido
            4. Atualiza estoque
        """
        if not itens_data:
            raise ValueError("Um pedido deve ter pelo menos um item")
        
        # 1. Verifica cliente e cria se necessário
        cliente = self.cliente_service.obter_cliente_ou_criar(nome_cliente, telefone_cliente)
        logger.info(f"Cliente para pedido: {cliente.nome} ({cliente.id})")
        
        # 2. Cria itens do pedido
        itens = []
        total = 0.0
        
        for produto_id, quantidade, preco_unitario in itens_data:
            if quantidade <= 0:
                raise ValueError(f"Quantidade deve ser maior que 0")
            if preco_unitario < 0:
                raise ValueError(f"Preço não pode ser negativo")
            
            # Verifica estoque
            if not self.estoque_service.validar_estoque(produto_id, quantidade):
                raise ValueError(f"Estoque insuficiente para produto {produto_id}")
            
            item = ItemPedido(
                id=str(uuid.uuid4()),
                pedido_id="temp",  # Será preenchido depois
                produto_id=produto_id,
                quantidade=quantidade,
                preco_unitario=preco_unitario
            )
            itens.append(item)
            total += item.subtotal
        
        # 3. Cria o pedido
        pedido = Pedido(
            id=str(uuid.uuid4()),
            cliente_id=cliente.id,
            data=datetime.now(),
            total=total,
            pago=0,
            concluido=0,
            itens=itens
        )
        
        pedido_id = self.pedido_repo.create(pedido)
        logger.info(f"Pedido criado: {pedido_id} - Cliente: {cliente.nome}")
        
        # 4. Atualiza estoque
        for produto_id, quantidade, _ in itens_data:
            self.estoque_service.remover_estoque(produto_id, quantidade)
        
        return self.pedido_repo.find_by_id(pedido_id)

    def obter_pedido(self, pedido_id: str) -> Optional[Pedido]:
        """Obtém um pedido pelo ID."""
        return self.pedido_repo.find_by_id(pedido_id)

    def listar_pedidos(self) -> List[Pedido]:
        """Lista todos os pedidos."""
        return self.pedido_repo.find_all()

    def pesquisar_pedidos(self, query: str) -> List[Pedido]:
        """Pesquisa pedidos por cliente ou ID."""
        return self.pedido_repo.search(query)

    def marcar_pago(self, pedido_id: str) -> bool:
        """Marca um pedido como pago."""
        resultado = self.pedido_repo.marcar_pago(pedido_id, True)
        if resultado:
            logger.info(f"Pedido {pedido_id} marcado como pago")
        return resultado

    def marcar_nao_pago(self, pedido_id: str) -> bool:
        """Marca um pedido como não pago."""
        resultado = self.pedido_repo.marcar_pago(pedido_id, False)
        if resultado:
            logger.info(f"Pedido {pedido_id} marcado como não pago")
        return resultado

    def marcar_concluido(self, pedido_id: str) -> bool:
        """Marca um pedido como concluído."""
        resultado = self.pedido_repo.marcar_concluido(pedido_id, True)
        if resultado:
            logger.info(f"Pedido {pedido_id} marcado como concluído")
        return resultado

    def reabrir_pedido(self, pedido_id: str) -> bool:
        """Reabre um pedido concluído."""
        resultado = self.pedido_repo.marcar_concluido(pedido_id, False)
        if resultado:
            logger.info(f"Pedido {pedido_id} reaberto")
        return resultado

    def deletar_pedido(self, pedido_id: str) -> bool:
        """Deleta um pedido e restaura o estoque.
        
        Ao deletar um pedido:
        1. Restaura estoque de todos os produtos
        2. Remove o pedido
        """
        try:
            pedido = self.obter_pedido(pedido_id)
            if not pedido:
                raise ValueError(f"Pedido {pedido_id} não encontrado")
            
            # Restaura estoque
            for item in pedido.itens:
                self.estoque_service.adicionar_estoque(item.produto_id, item.quantidade)
            
            # Deleta pedido
            resultado = self.pedido_repo.delete(pedido_id)
            logger.info(f"Pedido {pedido_id} deletado e estoque restaurado")
            return resultado
        except Exception as e:
            logger.error(f"Erro ao deletar pedido: {e}")
            return False

    def obter_pedidos_cliente(self, cliente_id: str) -> List[Pedido]:
        """Obtém todos os pedidos de um cliente."""
        return self.pedido_repo.find_by_cliente_id(cliente_id)

    def contar_pedidos_dia(self) -> int:
        """Conta quantos pedidos foram criados hoje."""
        pedidos = self.listar_pedidos()
        hoje = datetime.now().date()
        return sum(1 for p in pedidos if p.data.date() == hoje)

    def total_vendas_dia(self) -> float:
        """Calcula o total de vendas (todos os pedidos) de hoje."""
        pedidos = self.listar_pedidos()
        hoje = datetime.now().date()
        return sum(p.total for p in pedidos 
                  if p.data.date() == hoje)
