"""Repositório de Gastos usando Supabase"""

from typing import List, Optional
import logging
from datetime import datetime
from ...models import Gasto
from .base import BaseRepository
from ..supabase_connection import supabase_db

logger = logging.getLogger(__name__)


class GastoRepository(BaseRepository):
    """Repositório para gerenciar gastos no Supabase."""

    TABLE_NAME = "gastos"

    def create(self, gasto: Gasto) -> str:
        """Cria um novo gasto.
        
        Args:
            gasto: Objeto Gasto a ser criado
            
        Returns:
            ID do gasto criado
        """
        try:
            data = {
                "id": gasto.id,
                "descricao": gasto.descricao,
                "categoria": gasto.categoria,
                "valor": float(gasto.valor),
                "data": gasto.data.isoformat() if gasto.data else datetime.now().isoformat()
            }
            
            response = supabase_db.table(self.TABLE_NAME).insert(data).execute()
            logger.info(f"Gasto criado: {gasto.id} - {gasto.descricao}")
            return gasto.id
        except Exception as e:
            logger.error(f"Erro ao criar gasto: {e}")
            return None

    def find_by_id(self, gasto_id: str) -> Optional[Gasto]:
        """Encontra um gasto pelo ID.
        
        Args:
            gasto_id: ID do gasto
            
        Returns:
            Objeto Gasto ou None se não encontrado
        """
        try:
            response = supabase_db.table(self.TABLE_NAME).select("*").eq("id", gasto_id).single().execute()
            
            if response.data:
                return self._map_to_gasto(response.data)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar gasto {gasto_id}: {e}")
            return None

    def find_all(self) -> List[Gasto]:
        """Retorna todos os gastos.
        
        Returns:
            Lista de objetos Gasto
        """
        try:
            response = supabase_db.table(self.TABLE_NAME).select("*").execute()
            
            if response.data:
                return [self._map_to_gasto(row) for row in response.data]
            return []
        except Exception as e:
            logger.error(f"Erro ao listar gastos: {e}")
            return []

    def find_by_categoria(self, categoria: str) -> List[Gasto]:
        """Encontra gastos por categoria.
        
        Args:
            categoria: Categoria dos gastos
            
        Returns:
            Lista de objetos Gasto
        """
        try:
            response = supabase_db.table(self.TABLE_NAME).select("*").eq("categoria", categoria).execute()
            
            if response.data:
                return [self._map_to_gasto(row) for row in response.data]
            return []
        except Exception as e:
            logger.error(f"Erro ao buscar gastos por categoria: {e}")
            return []

    def search(self, query: str) -> List[Gasto]:
        """Pesquisa gastos por descrição.
        
        Args:
            query: Termo de busca
            
        Returns:
            Lista de objetos Gasto que correspondem à busca
        """
        try:
            # Busca por descrição (case-insensitive)
            response = supabase_db.table(self.TABLE_NAME).select("*").ilike("descricao", f"%{query}%").execute()
            
            if response.data:
                return [self._map_to_gasto(row) for row in response.data]
            return []
        except Exception as e:
            logger.error(f"Erro ao pesquisar gastos: {e}")
            return []

    def update(self, gasto: Gasto) -> bool:
        """Atualiza um gasto existente.
        
        Args:
            gasto: Objeto Gasto com dados atualizados
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        try:
            data = {
                "descricao": gasto.descricao,
                "categoria": gasto.categoria,
                "valor": float(gasto.valor),
                "data": gasto.data.isoformat() if gasto.data else datetime.now().isoformat()
            }
            
            response = supabase_db.table(self.TABLE_NAME).update(data).eq("id", gasto.id).execute()
            logger.info(f"Gasto atualizado: {gasto.id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar gasto: {e}")
            return False

    def delete(self, gasto_id: str) -> bool:
        """Deleta um gasto.
        
        Args:
            gasto_id: ID do gasto a deletar
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        try:
            response = supabase_db.table(self.TABLE_NAME).delete().eq("id", gasto_id).execute()
            logger.info(f"Gasto deletado: {gasto_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar gasto: {e}")
            return False

    def _map_to_gasto(self, data: dict) -> Gasto:
        """Mapeia dados do Supabase para objeto Gasto.
        
        Args:
            data: Dicionário com dados do gasto
            
        Returns:
            Objeto Gasto
        """
        data_gasto = None
        if data.get("data"):
            try:
                data_gasto = datetime.fromisoformat(data["data"].replace('Z', '+00:00'))
            except:
                data_gasto = datetime.now()
        
        return Gasto(
            id=data["id"],
            descricao=data["descricao"],
            categoria=data["categoria"],
            valor=float(data["valor"]),
            data=data_gasto
        )
