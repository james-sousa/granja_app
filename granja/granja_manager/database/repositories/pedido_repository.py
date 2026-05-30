"""Repositório de Pedidos usando Supabase"""

from typing import List, Optional
import logging
from datetime import datetime
from ...models import Pedido, ItemPedido
from .base import BaseRepository
from ..supabase_connection import supabase_db

logger = logging.getLogger(__name__)


class PedidoRepository(BaseRepository):
    """Repositório para gerenciar pedidos no Supabase.
    
    Gerencia a relação 1:N entre pedidos e itens_pedido.
    """

    PEDIDOS_TABLE = "pedidos"
    ITENS_TABLE = "itens_pedido"

    def create(self, pedido: Pedido) -> str:
        """Cria um novo pedido com seus itens.
        
        Args:
            pedido: Objeto Pedido a ser criado com lista de itens
            
        Returns:
            ID do pedido criado
        """
        try:
            # Calcula total do pedido
            total = sum(item.quantidade * item.preco_unitario for item in pedido.itens)
            
            # Insere pedido
            pedido_data = {
                "id": pedido.id,
                "cliente_id": pedido.cliente_id,
                "data": pedido.data.isoformat() if pedido.data else datetime.now().isoformat(),
                "total": float(total),
                "pago": int(pedido.pago),
                "concluido": int(pedido.concluido)
            }
            
            response = supabase_db.table(self.PEDIDOS_TABLE).insert(pedido_data).execute()
            
            # Insere itens do pedido
            for item in pedido.itens:
                item_data = {
                    "id": item.id,
                    "pedido_id": pedido.id,
                    "produto_id": item.produto_id,
                    "quantidade": int(item.quantidade),
                    "preco_unitario": float(item.preco_unitario)
                }
                supabase_db.table(self.ITENS_TABLE).insert(item_data).execute()
            
            logger.info(f"Pedido criado: {pedido.id} com {len(pedido.itens)} itens")
            return pedido.id
        except Exception as e:
            logger.error(f"Erro ao criar pedido: {e}")
            return None

    def find_by_id(self, pedido_id: str) -> Optional[Pedido]:
        """Encontra um pedido pelo ID com seus itens.
        
        Args:
            pedido_id: ID do pedido
            
        Returns:
            Objeto Pedido ou None se não encontrado
        """
        try:
            # Busca pedido
            response = supabase_db.table(self.PEDIDOS_TABLE).select("*").eq("id", pedido_id).single().execute()
            
            if not response.data:
                return None
            
            pedido_data = response.data
            
            # Busca itens do pedido
            items_response = supabase_db.table(self.ITENS_TABLE).select("*").eq("pedido_id", pedido_id).execute()
            
            itens = []
            if items_response.data:
                itens = [self._map_to_item_pedido(row) for row in items_response.data]
            
            return self._map_to_pedido(pedido_data, itens)
        except Exception as e:
            logger.error(f"Erro ao buscar pedido {pedido_id}: {e}")
            return None

    def find_all(self) -> List[Pedido]:
        """Retorna todos os pedidos com seus itens.
        
        Returns:
            Lista de objetos Pedido
        """
        try:
            response = supabase_db.table(self.PEDIDOS_TABLE).select("*").execute()
            
            if not response.data:
                return []
            
            pedidos = []
            for pedido_data in response.data:
                # Busca itens de cada pedido
                items_response = supabase_db.table(self.ITENS_TABLE).select("*").eq("pedido_id", pedido_data["id"]).execute()
                
                itens = []
                if items_response.data:
                    itens = [self._map_to_item_pedido(row) for row in items_response.data]
                
                pedidos.append(self._map_to_pedido(pedido_data, itens))
            
            return pedidos
        except Exception as e:
            logger.error(f"Erro ao listar pedidos: {e}")
            return []

    def find_by_cliente_id(self, cliente_id: str) -> List[Pedido]:
        """Encontra todos os pedidos de um cliente.
        
        Args:
            cliente_id: ID do cliente
            
        Returns:
            Lista de objetos Pedido
        """
        try:
            response = supabase_db.table(self.PEDIDOS_TABLE).select("*").eq("cliente_id", cliente_id).execute()
            
            if not response.data:
                return []
            
            pedidos = []
            for pedido_data in response.data:
                # Busca itens de cada pedido
                items_response = supabase_db.table(self.ITENS_TABLE).select("*").eq("pedido_id", pedido_data["id"]).execute()
                
                itens = []
                if items_response.data:
                    itens = [self._map_to_item_pedido(row) for row in items_response.data]
                
                pedidos.append(self._map_to_pedido(pedido_data, itens))
            
            return pedidos
        except Exception as e:
            logger.error(f"Erro ao buscar pedidos do cliente: {e}")
            return []

    def search(self, query: str) -> List[Pedido]:
        """Pesquisa pedidos por ID ou nome do cliente.
        
        Args:
            query: Termo de busca
            
        Returns:
            Lista de objetos Pedido que correspondem à busca
        """
        try:
            # Busca por ID do pedido
            response = supabase_db.table(self.PEDIDOS_TABLE).select("*").ilike("id", f"%{query}%").execute()
            
            pedidos = []
            if response.data:
                for pedido_data in response.data:
                    items_response = supabase_db.table(self.ITENS_TABLE).select("*").eq("pedido_id", pedido_data["id"]).execute()
                    itens = []
                    if items_response.data:
                        itens = [self._map_to_item_pedido(row) for row in items_response.data]
                    pedidos.append(self._map_to_pedido(pedido_data, itens))
            
            return pedidos
        except Exception as e:
            logger.error(f"Erro ao pesquisar pedidos: {e}")
            return []

    def update(self, pedido: Pedido) -> bool:
        """Atualiza um pedido existente.
        
        Args:
            pedido: Objeto Pedido com dados atualizados
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        try:
            # Calcula total
            total = sum(item.quantidade * item.preco_unitario for item in pedido.itens)
            
            data = {
                "total": float(total),
                "pago": int(pedido.pago),
                "concluido": int(pedido.concluido)
            }
            
            response = supabase_db.table(self.PEDIDOS_TABLE).update(data).eq("id", pedido.id).execute()
            logger.info(f"Pedido atualizado: {pedido.id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar pedido: {e}")
            return False

    def delete(self, pedido_id: str) -> bool:
        """Deleta um pedido e seus itens.
        
        Args:
            pedido_id: ID do pedido a deletar
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        try:
            # Deleta itens primeiro (relacionamento 1:N)
            supabase_db.table(self.ITENS_TABLE).delete().eq("pedido_id", pedido_id).execute()
            
            # Deleta pedido
            response = supabase_db.table(self.PEDIDOS_TABLE).delete().eq("id", pedido_id).execute()
            logger.info(f"Pedido deletado: {pedido_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar pedido: {e}")
            return False

    def marcar_pago(self, pedido_id: str, pago: bool) -> bool:
        """Marca um pedido como pago ou não.
        
        Args:
            pedido_id: ID do pedido
            pago: True para marcar como pago, False caso contrário
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        try:
            data = {"pago": 1 if pago else 0}
            response = supabase_db.table(self.PEDIDOS_TABLE).update(data).eq("id", pedido_id).execute()
            logger.info(f"Pedido {pedido_id} marcado como {'pago' if pago else 'não pago'}")
            return True
        except Exception as e:
            logger.error(f"Erro ao marcar pedido como pago: {e}")
            return False

    def marcar_concluido(self, pedido_id: str, concluido: bool) -> bool:
        """Marca um pedido como concluído ou não.
        
        Args:
            pedido_id: ID do pedido
            concluido: True para marcar como concluído, False caso contrário
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        try:
            data = {"concluido": 1 if concluido else 0}
            response = supabase_db.table(self.PEDIDOS_TABLE).update(data).eq("id", pedido_id).execute()
            logger.info(f"Pedido {pedido_id} marcado como {'concluído' if concluido else 'pendente'}")
            return True
        except Exception as e:
            logger.error(f"Erro ao marcar pedido como concluído: {e}")
            return False

    def _map_to_pedido(self, data: dict, itens: List[ItemPedido]) -> Pedido:
        """Mapeia dados do Supabase para objeto Pedido.
        
        Args:
            data: Dicionário com dados do pedido
            itens: Lista de itens do pedido
            
        Returns:
            Objeto Pedido
        """
        data_pedido = None
        if data.get("data"):
            try:
                data_pedido = datetime.fromisoformat(data["data"].replace('Z', '+00:00'))
            except:
                data_pedido = datetime.now()
        
        return Pedido(
            id=data["id"],
            cliente_id=data["cliente_id"],
            data=data_pedido or datetime.now(),
            total=float(data.get("total", 0.0)),
            pago=int(data.get("pago", 0)),
            concluido=int(data.get("concluido", 0)),
            itens=itens
        )

    def _map_to_item_pedido(self, data: dict) -> ItemPedido:
        """Mapeia dados do Supabase para objeto ItemPedido.
        
        Args:
            data: Dicionário com dados do item
            
        Returns:
            Objeto ItemPedido
        """
        return ItemPedido(
            id=data["id"],
            pedido_id=data["pedido_id"],
            produto_id=data["produto_id"],
            quantidade=int(data["quantidade"]),
            preco_unitario=float(data["preco_unitario"])
        )
