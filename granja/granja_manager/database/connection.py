# OBSOLETO: substituído pelo Supabase. Este arquivo não é mais utilizado.

"""Conexão com o banco de dados SQLite"""

import sqlite3
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Gerencia a conexão com o banco de dados SQLite."""

    def __init__(self, db_path: str = "data/granja.db"):
        """Inicializa a conexão com o banco de dados.
        
        Args:
            db_path: Caminho para o arquivo do banco de dados
        """
        self.db_path = db_path
        self._ensure_db_dir()
        self.connection: Optional[sqlite3.Connection] = None

    def _ensure_db_dir(self):
        """Cria o diretório para o banco de dados se não existir."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Diretório criado: {db_dir}")

    def connect(self):
        """Estabelece a conexão com o banco de dados."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            # Habilita chaves estrangeiras
            self.connection.execute("PRAGMA foreign_keys = ON")
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Conectado ao banco de dados: {self.db_path}")
            return self.connection
        except sqlite3.Error as e:
            logger.error(f"Erro ao conectar ao banco de dados: {e}")
            raise

    def disconnect(self):
        """Fecha a conexão com o banco de dados."""
        if self.connection:
            self.connection.close()
            logger.info("Desconectado do banco de dados")

    def execute(self, sql: str, params: tuple = ()):
        """Executa uma query SQL.
        
        Args:
            sql: Comando SQL
            params: Parâmetros da query
            
        Returns:
            Cursor da query
        """
        if not self.connection:
            self.connect()
        try:
            return self.connection.execute(sql, params)
        except sqlite3.Error as e:
            logger.error(f"Erro ao executar query: {e}")
            raise

    def commit(self):
        """Commit da transação."""
        if self.connection:
            self.connection.commit()

    def rollback(self):
        """Rollback da transação."""
        if self.connection:
            self.connection.rollback()

    def fetchone(self, sql: str, params: tuple = ()):
        """Executa uma query e retorna um resultado."""
        cursor = self.execute(sql, params)
        return cursor.fetchone()

    def fetchall(self, sql: str, params: tuple = ()):
        """Executa uma query e retorna todos os resultados."""
        cursor = self.execute(sql, params)
        return cursor.fetchall()

    def begin_transaction(self):
        """Inicia uma transação."""
        self.execute("BEGIN TRANSACTION")

    def end_transaction(self):
        """Finaliza uma transação."""
        self.commit()


# Instância global
db = DatabaseConnection()
