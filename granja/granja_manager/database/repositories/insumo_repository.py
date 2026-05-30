"""Repositório de Insumos"""

import logging
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from ...models import Insumo
from ..supabase_connection import supabase_db

logger = logging.getLogger(__name__)


@dataclass
class InsumoDataclass:
    """Mapeamento de Insumo para dataclass."""
    id: str
    nome: str
    unidade: str
    quantidade: float
    criado_em: str


class InsumoRepository:
    """Repositório para gerenciar insumos no Supabase."""
    
    TABLE_NAME = "insumos"
    
    def create(self, insumo: 'Insumo') -> Optional[str]:
        """Cria um novo insumo.
        
        Args:
            insumo: Objeto Insumo
            
        Returns:
            ID do insumo criado ou None em caso de erro
        """
        try:
            data = {
                "id": insumo.id,
                "nome": insumo.nome,
                "unidade": insumo.unidade,
                "quantidade": insumo.quantidade,
                "criado_em": datetime.now().isoformat(),
            }
            
            response = supabase_db.table(self.TABLE_NAME).insert(data).execute()
            logger.info(f"Insumo criado: {insumo.nome}")
            return insumo.id
            
        except Exception as e:
            logger.error(f"Erro ao criar insumo: {e}")
            return None
    
    def find_by_id(self, insumo_id: str) -> Optional[dict]:
        """Busca um insumo pelo ID.
        
        Args:
            insumo_id: ID do insumo
            
        Returns:
            Dicionário com dados do insumo ou None
        """
        try:
            response = supabase_db.table(self.TABLE_NAME).select("*").eq("id", insumo_id).execute()
            
            if response.data and len(response.data) > 0:
                return self._map_to_insumo(response.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar insumo {insumo_id}: {e}")
            return None
    
    def find_all(self) -> List[dict]:
        """Lista todos os insumos.
        
        Returns:
            Lista de dicionários com insumos
        """
        try:
            response = supabase_db.table(self.TABLE_NAME).select("*").execute()
            return [self._map_to_insumo(row) for row in response.data] if response.data else []
            
        except Exception as e:
            logger.error(f"Erro ao listar insumos: {e}")
            return []
    
    def search(self, query: str) -> List[dict]:
        """Pesquisa insumos por nome ou categoria.
        
        Args:
            query: Termo de busca
            
        Returns:
            Lista de insumos encontrados
        """
        try:
            response = supabase_db.table(self.TABLE_NAME).select("*").ilike("nome", f"%{query}%").execute()
            return [self._map_to_insumo(row) for row in response.data] if response.data else []
            
        except Exception as e:
            logger.error(f"Erro ao pesquisar insumos: {e}")
            return []
    
    def update(self, insumo: 'Insumo') -> bool:
        """Atualiza um insumo existente.
        
        Args:
            insumo: Objeto Insumo com dados atualizados
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        try:
            data = {
                "nome": insumo.nome,
                "unidade": insumo.unidade,
                "quantidade": insumo.quantidade,
            }
            
            response = supabase_db.table(self.TABLE_NAME).update(data).eq("id", insumo.id).execute()
            logger.info(f"Insumo atualizado: {insumo.id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar insumo: {e}")
            return False
    
    def atualizar_quantidade(self, insumo_id: str, delta: float) -> bool:
        """Atualiza a quantidade de um insumo (entrada/saída).
        
        Args:
            insumo_id: ID do insumo
            delta: Valor a adicionar (positivo) ou subtrair (negativo)
            
        Returns:
            True se bem-sucedido
        """
        try:
            # Busca o insumo atual
            insumo = self.find_by_id(insumo_id)
            if not insumo:
                return False
            
            nova_quantidade = insumo.get("quantidade", 0) + delta
            
            response = supabase_db.table(self.TABLE_NAME).update({
                "quantidade": nova_quantidade
            }).eq("id", insumo_id).execute()
            
            logger.info(f"Quantidade de insumo {insumo_id} atualizada: +{delta}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar quantidade: {e}")
            return False
    
    def delete(self, insumo_id: str) -> bool:
        """Deleta um insumo.
        
        Args:
            insumo_id: ID do insumo
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        try:
            response = supabase_db.table(self.TABLE_NAME).delete().eq("id", insumo_id).execute()
            logger.info(f"Insumo deletado: {insumo_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao deletar insumo: {e}")
            return False
    
    def _map_to_insumo(self, row: dict) -> dict:
        """Converte linha do Supabase para dicionário.
        
        Args:
            row: Linha do banco
            
        Returns:
            Dicionário com dados do insumo
        """
        return {
            "id": row.get("id"),
            "nome": row.get("nome"),
            "unidade": row.get("unidade", "un."),
            "quantidade": float(row.get("quantidade", 0)),
            "criado_em": row.get("criado_em"),
        }
