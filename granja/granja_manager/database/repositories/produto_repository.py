"""Repositório de Produtos usando Supabase"""

from typing import List, Optional
import logging
from datetime import datetime
from ...models import Produto
from .base import BaseRepository
from ..supabase_connection import supabase_db

logger = logging.getLogger(__name__)


class ProdutoRepository(BaseRepository):
    """Repositório para gerenciar produtos no Supabase."""

    TABLE_NAME = "produtos"

    def create(self, produto: Produto) -> str:
        """Cria um novo produto.
        
        Args:
            produto: Objeto Produto a ser criado
            
        Returns:
            ID do produto criado
        """
        try:
            data = {
                "id": produto.id,
                "nome": produto.nome,
                "preco": float(produto.preco),
                "estoque": int(produto.estoque),
                "ativo": int(produto.ativo),
                "criado_em": produto.criado_em.isoformat() if produto.criado_em else datetime.now().isoformat()
            }
            
            response = supabase_db.table(self.TABLE_NAME).insert(data).execute()
            logger.info(f"Produto criado: {produto.id} - {produto.nome}")
            return produto.id
        except Exception as e:
            logger.error(f"Erro ao criar produto: {e}")
            return None

    def find_by_id(self, produto_id: str) -> Optional[Produto]:
        """Encontra um produto pelo ID.
        
        Args:
            produto_id: ID do produto
            
        Returns:
            Objeto Produto ou None se não encontrado
        """
        try:
            response = supabase_db.table(self.TABLE_NAME).select("*").eq("id", produto_id).single().execute()
            
            if response.data:
                return self._map_to_produto(response.data)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar produto {produto_id}: {e}")
            return None

    def find_all(self) -> List[Produto]:
        """Retorna todos os produtos.
        
        Returns:
            Lista de objetos Produto
        """
        try:
            response = supabase_db.table(self.TABLE_NAME).select("*").execute()
            
            if response.data:
                return [self._map_to_produto(row) for row in response.data]
            return []
        except Exception as e:
            logger.error(f"Erro ao listar produtos: {e}")
            return []

    def search(self, query: str) -> List[Produto]:
        """Pesquisa produtos por nome.
        
        Args:
            query: Termo de busca
            
        Returns:
            Lista de objetos Produto que correspondem à busca
        """
        try:
            # Busca por nome (case-insensitive)
            response = supabase_db.table(self.TABLE_NAME).select("*").ilike("nome", f"%{query}%").execute()
            
            if response.data:
                return [self._map_to_produto(row) for row in response.data]
            return []
        except Exception as e:
            logger.error(f"Erro ao pesquisar produtos: {e}")
            return []

    def update(self, produto: Produto) -> bool:
        """Atualiza um produto existente.
        
        Args:
            produto: Objeto Produto com dados atualizados
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        try:
            data = {
                "nome": produto.nome,
                "preco": float(produto.preco),
                "estoque": int(produto.estoque),
                "ativo": int(produto.ativo)
            }
            
            response = supabase_db.table(self.TABLE_NAME).update(data).eq("id", produto.id).execute()
            logger.info(f"Produto atualizado: {produto.id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar produto: {e}")
            return False

    def delete(self, produto_id: str) -> bool:
        """Deleta um produto.
        
        Args:
            produto_id: ID do produto a deletar
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        try:
            response = supabase_db.table(self.TABLE_NAME).delete().eq("id", produto_id).execute()
            logger.info(f"Produto deletado: {produto_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar produto: {e}")
            return False

    def atualizar_estoque(self, produto_id: str, delta: int) -> bool:
        """Atualiza o estoque de um produto.
        
        Args:
            produto_id: ID do produto
            delta: Valor a adicionar/subtrair do estoque (positivo ou negativo)
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        try:
            # Busca o produto atual
            produto = self.find_by_id(produto_id)
            if not produto:
                logger.error(f"Produto {produto_id} não encontrado")
                return False
            
            # Calcula novo estoque
            novo_estoque = produto.estoque + delta
            
            # Atualiza no Supabase
            data = {"estoque": int(novo_estoque)}
            response = supabase_db.table(self.TABLE_NAME).update(data).eq("id", produto_id).execute()
            
            logger.info(f"Estoque atualizado: {produto_id} - delta: {delta}, novo estoque: {novo_estoque}")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar estoque: {e}")
            return False

    def _map_to_produto(self, data: dict) -> Produto:
        """Mapeia dados do Supabase para objeto Produto.
        
        Args:
            data: Dicionário com dados do produto
            
        Returns:
            Objeto Produto
        """
        criado_em = None
        if data.get("criado_em"):
            try:
                criado_em = datetime.fromisoformat(data["criado_em"].replace('Z', '+00:00'))
            except:
                criado_em = datetime.now()
        
        return Produto(
            id=data["id"],
            nome=data["nome"],
            preco=float(data["preco"]),
            estoque=int(data.get("estoque", 0)),
            ativo=int(data.get("ativo", 1)),
            criado_em=criado_em
        )
