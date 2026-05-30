"""Repositório de Clientes usando Supabase"""

from typing import List, Optional
import logging
from datetime import datetime
from ...models import Cliente
from .base import BaseRepository
from ..supabase_connection import supabase_db

logger = logging.getLogger(__name__)


class ClienteRepository(BaseRepository):
    """Repositório para gerenciar clientes no Supabase."""

    TABLE_NAME = "clientes"

    def create(self, cliente: Cliente) -> str:
        """Cria um novo cliente.
        
        Args:
            cliente: Objeto Cliente a ser criado
            
        Returns:
            ID do cliente criado
        """
        try:
            data = {
                "id": cliente.id,
                "nome": cliente.nome,
                "telefone": cliente.telefone,
                "criado_em": cliente.criado_em.isoformat() if cliente.criado_em else datetime.now().isoformat()
            }
            
            response = supabase_db.table(self.TABLE_NAME).insert(data).execute()
            logger.info(f"Cliente criado: {cliente.id} - {cliente.nome}")
            return cliente.id
        except Exception as e:
            logger.error(f"Erro ao criar cliente: {e}")
            return None

    def find_by_id(self, cliente_id: str) -> Optional[Cliente]:
        """Encontra um cliente pelo ID.
        
        Args:
            cliente_id: ID do cliente
            
        Returns:
            Objeto Cliente ou None se não encontrado
        """
        try:
            response = supabase_db.table(self.TABLE_NAME).select("*").eq("id", cliente_id).single().execute()
            
            if response.data:
                return self._map_to_cliente(response.data)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar cliente {cliente_id}: {e}")
            return None

    def find_all(self) -> List[Cliente]:
        """Retorna todos os clientes.
        
        Returns:
            Lista de objetos Cliente
        """
        try:
            response = supabase_db.table(self.TABLE_NAME).select("*").execute()
            
            if response.data:
                return [self._map_to_cliente(row) for row in response.data]
            return []
        except Exception as e:
            logger.error(f"Erro ao listar clientes: {e}")
            return []

    def find_by_nome_e_telefone(self, nome: str, telefone: str) -> Optional[Cliente]:
        """Encontra um cliente pelo nome e telefone.
        
        Args:
            nome: Nome do cliente
            telefone: Telefone do cliente
            
        Returns:
            Objeto Cliente ou None se não encontrado
        """
        try:
            response = supabase_db.table(self.TABLE_NAME).select("*").eq("nome", nome).eq("telefone", telefone).execute()
            
            if response.data and len(response.data) > 0:
                return self._map_to_cliente(response.data[0])
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por nome e telefone: {e}")
            return None

    def search(self, query: str) -> List[Cliente]:
        """Pesquisa clientes por nome ou telefone.
        
        Args:
            query: Termo de busca
            
        Returns:
            Lista de objetos Cliente que correspondem à busca
        """
        try:
            # Busca por nome (case-insensitive)
            response = supabase_db.table(self.TABLE_NAME).select("*").ilike("nome", f"%{query}%").execute()
            
            if response.data:
                return [self._map_to_cliente(row) for row in response.data]
            return []
        except Exception as e:
            logger.error(f"Erro ao pesquisar clientes: {e}")
            return []

    def update(self, cliente: Cliente) -> bool:
        """Atualiza um cliente existente.
        
        Args:
            cliente: Objeto Cliente com dados atualizados
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        try:
            data = {
                "nome": cliente.nome,
                "telefone": cliente.telefone
            }
            
            response = supabase_db.table(self.TABLE_NAME).update(data).eq("id", cliente.id).execute()
            logger.info(f"Cliente atualizado: {cliente.id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar cliente: {e}")
            return False

    def delete(self, cliente_id: str) -> bool:
        """Deleta um cliente.
        
        Args:
            cliente_id: ID do cliente a deletar
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        try:
            response = supabase_db.table(self.TABLE_NAME).delete().eq("id", cliente_id).execute()
            logger.info(f"Cliente deletado: {cliente_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar cliente: {e}")
            return False

    def _map_to_cliente(self, data: dict) -> Cliente:
        """Mapeia dados do Supabase para objeto Cliente.
        
        Args:
            data: Dicionário com dados do cliente
            
        Returns:
            Objeto Cliente
        """
        criado_em = None
        if data.get("criado_em"):
            try:
                criado_em = datetime.fromisoformat(data["criado_em"].replace('Z', '+00:00'))
            except:
                criado_em = datetime.now()
        
        return Cliente(
            id=data["id"],
            nome=data["nome"],
            telefone=data.get("telefone", ""),
            criado_em=criado_em
        )
