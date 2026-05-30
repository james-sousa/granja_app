"""Repositório de Itens de Pedido"""

import uuid
from typing import List, Optional
import logging
from .base import BaseRepository
from ..connection import db
from ...models import ItemPedido

logger = logging.getLogger(__name__)


class ItemPedidoRepository(BaseRepository):
    """Repositório para gerenciar itens de pedido no banco de dados."""

    def create(self, item: ItemPedido) -> str:
        """Cria um novo item de pedido."""
        try:
            item.id = str(uuid.uuid4())
            db.execute("""
                INSERT INTO itens_pedido (id, pedido_id, produto_id, quantidade, preco_unitario)
                VALUES (?, ?, ?, ?, ?)
            """, (item.id, item.pedido_id, item.produto_id, item.quantidade, item.preco_unitario))
            db.commit()
            logger.info(f"Item de pedido criado: {item.id}")
            return item.id
        except Exception as e:
            logger.error(f"Erro ao criar item de pedido: {e}")
            db.rollback()
            raise

    def update(self, item: ItemPedido) -> bool:
        """Atualiza um item de pedido."""
        try:
            db.execute("""
                UPDATE itens_pedido 
                SET quantidade = ?, preco_unitario = ?
                WHERE id = ?
            """, (item.quantidade, item.preco_unitario, item.id))
            db.commit()
            logger.info(f"Item de pedido atualizado: {item.id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar item de pedido: {e}")
            db.rollback()
            return False

    def delete(self, item_id: str) -> bool:
        """Deleta um item de pedido."""
        try:
            db.execute("DELETE FROM itens_pedido WHERE id = ?", (item_id,))
            db.commit()
            logger.info(f"Item de pedido deletado: {item_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar item de pedido: {e}")
            db.rollback()
            return False

    def find_by_id(self, item_id: str) -> Optional[ItemPedido]:
        """Encontra um item de pedido pelo ID."""
        try:
            row = db.fetchone(
                """SELECT id, pedido_id, produto_id, quantidade, preco_unitario 
                   FROM itens_pedido WHERE id = ?""",
                (item_id,)
            )
            if row:
                return ItemPedido(
                    id=row[0],
                    pedido_id=row[1],
                    produto_id=row[2],
                    quantidade=row[3],
                    preco_unitario=row[4]
                )
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar item de pedido: {e}")
            return None

    def find_all(self) -> List[ItemPedido]:
        """Retorna todos os itens de pedido."""
        try:
            rows = db.fetchall(
                "SELECT id, pedido_id, produto_id, quantidade, preco_unitario FROM itens_pedido"
            )
            return [
                ItemPedido(
                    id=row[0],
                    pedido_id=row[1],
                    produto_id=row[2],
                    quantidade=row[3],
                    preco_unitario=row[4]
                )
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Erro ao listar itens de pedido: {e}")
            return []

    def find_by_pedido_id(self, pedido_id: str) -> List[ItemPedido]:
        """Encontra todos os itens de um pedido."""
        try:
            rows = db.fetchall(
                """SELECT id, pedido_id, produto_id, quantidade, preco_unitario 
                   FROM itens_pedido WHERE pedido_id = ?""",
                (pedido_id,)
            )
            return [
                ItemPedido(
                    id=row[0],
                    pedido_id=row[1],
                    produto_id=row[2],
                    quantidade=row[3],
                    preco_unitario=row[4]
                )
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Erro ao buscar itens do pedido: {e}")
            return []

    def search(self, query: str) -> List[ItemPedido]:
        """Pesquisa itens de pedido."""
        # Implementação simples - pode ser expandida
        return self.find_all()
