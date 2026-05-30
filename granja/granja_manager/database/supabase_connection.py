"""Conexão com o banco de dados Supabase PostgreSQL"""

import logging
from typing import Optional
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class SupabaseConnection:
    """Gerencia a conexão com o banco de dados Supabase PostgreSQL."""

    def __init__(self, supabase_url: str, supabase_key: str):
        """Inicializa a conexão com o Supabase.
        
        Args:
            supabase_url: URL do projeto Supabase
            supabase_key: Chave da API (Service Role Key para operações server-side)
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.client: Optional[Client] = None
        self._connect()

    def _connect(self):
        """Estabelece a conexão com o Supabase."""
        try:
            if not self.supabase_url or not self.supabase_key:
                raise ValueError(
                    "SUPABASE_URL e SUPABASE_ANON_KEY devem estar definidas no arquivo .env"
                )
            
            self.client = create_client(self.supabase_url, self.supabase_key)
            logger.info(f"Conectado ao Supabase: {self.supabase_url}")
        except Exception as e:
            logger.error(f"Erro ao conectar ao Supabase: {e}")
            raise

    def get_client(self) -> Client:
        """Retorna a instância do cliente Supabase.
        
        Returns:
            Cliente Supabase inicializado
        """
        if not self.client:
            self._connect()
        return self.client

    def table(self, table_name: str):
        """Acessa uma tabela no Supabase.
        
        Args:
            table_name: Nome da tabela
            
        Returns:
            Objeto de tabela do Supabase
        """
        return self.client.table(table_name)


# Importa as configurações
try:
    from ...config import SUPABASE_URL, SUPABASE_ANON_KEY
except ImportError:
    # Fallback para quando o módulo é importado de formas diferentes
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    sys.path.insert(0, project_root)
    from config import SUPABASE_URL, SUPABASE_ANON_KEY

# Instância global única do Supabase
try:
    supabase_db = SupabaseConnection(SUPABASE_URL, SUPABASE_ANON_KEY).get_client()
except Exception as e:
    logger.error(f"Falha ao inicializar Supabase: {e}")
    supabase_db = None
