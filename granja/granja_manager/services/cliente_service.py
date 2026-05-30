"""Serviço de Cliente"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Tuple
import logging
from ..models import Cliente, Pedido
from ..database.repositories import ClienteRepository, PedidoRepository

logger = logging.getLogger(__name__)


class ClienteService:
    """Serviço para gerenciar clientes."""

    def __init__(self):
        self.cliente_repo = ClienteRepository()
        self.pedido_repo = PedidoRepository()

    def criar_cliente(self, nome: str, telefone: str) -> Cliente:
        """Cria um novo cliente.
        
        Args:
            nome: Nome do cliente
            telefone: Telefone com WhatsApp
            
        Returns:
            Cliente criado
        """
        if not nome or not nome.strip():
            raise ValueError("Nome do cliente é obrigatório")
        
        cliente = Cliente(
            id=str(uuid.uuid4()),
            nome=nome.strip(),
            telefone=telefone.strip() if telefone else ""
        )
        
        cliente_id = self.cliente_repo.create(cliente)
        logger.info(f"Cliente criado: {nome}")
        return self.cliente_repo.find_by_id(cliente_id)

    def obter_cliente_ou_criar(self, nome: str, telefone: str) -> Cliente:
        """Obtém um cliente existente ou cria um novo.
        
        Este é o método principal para o fluxo de pedidos:
        Quando um pedido é criado, verifica-se se o cliente existe.
        Se não existir, é criado automaticamente.
        """
        # Normaliza entrada
        nome = nome.strip() if nome else ""
        telefone = telefone.strip() if telefone else ""
        
        if not nome:
            raise ValueError("Nome do cliente é obrigatório")
        
        # Tenta encontrar cliente existente
        cliente = self.cliente_repo.find_by_nome_e_telefone(nome, telefone)
        
        if cliente:
            logger.info(f"Cliente encontrado: {nome}")
            return cliente
        
        # Cria novo cliente
        logger.info(f"Criando novo cliente: {nome}")
        return self.criar_cliente(nome, telefone)

    def obter_cliente(self, cliente_id: str) -> Optional[Cliente]:
        """Obtém um cliente pelo ID."""
        return self.cliente_repo.find_by_id(cliente_id)

    def listar_clientes(self) -> List[Cliente]:
        """Lista todos os clientes."""
        return self.cliente_repo.find_all()

    def pesquisar_clientes(self, query: str) -> List[Cliente]:
        """Pesquisa clientes por nome ou telefone."""
        return self.cliente_repo.search(query)

    def deletar_cliente(self, cliente_id: str) -> bool:
        """Deleta um cliente apenas se não tiver pedidos."""
        return self.cliente_repo.delete(cliente_id)

    def obter_historico_cliente(self, cliente_id: str) -> List[Pedido]:
        """Obtém todo o histórico de pedidos de um cliente."""
        return self.pedido_repo.find_by_cliente_id(cliente_id)

    def obter_pendencias_cliente(self, cliente_id: str) -> Tuple[float, int]:
        """Obtém o valor total e quantidade de pedidos pendentes de um cliente.
        
        Returns:
            Tupla (total_pendente, quantidade_pedidos_pendentes)
        """
        pedidos = self.pedido_repo.find_by_cliente_id(cliente_id)
        pendentes = [p for p in pedidos if not p.pago]
        
        total = sum(p.total for p in pendentes)
        quantidade = len(pendentes)
        
        return total, quantidade

    def obter_clientes_com_pendencias(self) -> List[Dict]:
        """Retorna lista de clientes com pedidos pendentes.
        
        Returns:
            Lista de dicionários com informações de pendências
        """
        todos_pedidos = self.pedido_repo.find_all()
        clientes_dict: Dict[str, Dict] = {}
        
        for pedido in todos_pedidos:
            if not pedido.pago:  # Apenas pedidos não pagos
                if pedido.cliente_id not in clientes_dict:
                    cliente = self.obter_cliente(pedido.cliente_id)
                    if cliente:
                        clientes_dict[pedido.cliente_id] = {
                            "cliente": cliente,
                            "pedidos": [],
                            "total_pendente": 0.0
                        }
                
                if pedido.cliente_id in clientes_dict:
                    clientes_dict[pedido.cliente_id]["pedidos"].append(pedido)
                    clientes_dict[pedido.cliente_id]["total_pendente"] += pedido.total
        
        return list(clientes_dict.values())

    def total_clientes_ativos(self) -> int:
        """Retorna o número de clientes que já fizeram pedidos."""
        return len(self.cliente_repo.find_all())
