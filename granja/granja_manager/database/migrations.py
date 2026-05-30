# OBSOLETO: substituído pelo Supabase. Este arquivo não é mais utilizado.

"""Migrações do banco de dados"""

import logging
from .connection import db

logger = logging.getLogger(__name__)


class Migrations:
    """Gerencia as migrações do banco de dados."""

    @staticmethod
    def criar_tabelas():
        """Cria todas as tabelas do banco de dados."""
        try:
            db.connect()
            
            # Tabela de clientes
            db.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id TEXT PRIMARY KEY,
                    nome TEXT NOT NULL,
                    telefone TEXT,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("Tabela 'clientes' criada/verificada")

            # Tabela de produtos
            db.execute("""
                CREATE TABLE IF NOT EXISTS produtos (
                    id TEXT PRIMARY KEY,
                    nome TEXT NOT NULL,
                    preco REAL NOT NULL,
                    estoque INTEGER DEFAULT 0,
                    ativo INTEGER DEFAULT 1,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("Tabela 'produtos' criada/verificada")

            # Tabela de pedidos
            db.execute("""
                CREATE TABLE IF NOT EXISTS pedidos (
                    id TEXT PRIMARY KEY,
                    cliente_id TEXT NOT NULL,
                    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total REAL DEFAULT 0,
                    pago INTEGER DEFAULT 0,
                    concluido INTEGER DEFAULT 0,
                    FOREIGN KEY(cliente_id) REFERENCES clientes(id)
                )
            """)
            logger.info("Tabela 'pedidos' criada/verificada")

            # Tabela de itens de pedido
            db.execute("""
                CREATE TABLE IF NOT EXISTS itens_pedido (
                    id TEXT PRIMARY KEY,
                    pedido_id TEXT NOT NULL,
                    produto_id TEXT NOT NULL,
                    quantidade INTEGER NOT NULL,
                    preco_unitario REAL NOT NULL,
                    FOREIGN KEY(pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
                    FOREIGN KEY(produto_id) REFERENCES produtos(id)
                )
            """)
            logger.info("Tabela 'itens_pedido' criada/verificada")

            # Tabela de gastos
            db.execute("""
                CREATE TABLE IF NOT EXISTS gastos (
                    id TEXT PRIMARY KEY,
                    descricao TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    valor REAL NOT NULL,
                    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("Tabela 'gastos' criada/verificada")

            # Criar índices para melhor performance
            db.execute("""
                CREATE INDEX IF NOT EXISTS idx_pedidos_cliente_id 
                ON pedidos(cliente_id)
            """)
            db.execute("""
                CREATE INDEX IF NOT EXISTS idx_pedidos_data 
                ON pedidos(data)
            """)
            db.execute("""
                CREATE INDEX IF NOT EXISTS idx_itens_pedido_id 
                ON itens_pedido(pedido_id)
            """)
            db.execute("""
                CREATE INDEX IF NOT EXISTS idx_gastos_data 
                ON gastos(data)
            """)

            db.commit()
            logger.info("Todas as tabelas criadas com sucesso")

        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            db.rollback()
            raise

    @staticmethod
    def banco_vazio() -> bool:
        """Verifica se o banco de dados está vazio."""
        try:
            db.connect()
            resultado = db.fetchone("SELECT COUNT(*) as count FROM sqlite_master WHERE type='table'")
            return resultado[0] == 0
        except Exception as e:
            logger.error(f"Erro ao verificar se banco está vazio: {e}")
            return False

    @staticmethod
    def resetar_banco():
        """CUIDADO: Reseta o banco de dados completamente."""
        try:
            db.connect()
            # Drop all tables
            cursor = db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = cursor.fetchall()
            
            for table in tables:
                db.execute(f"DROP TABLE IF EXISTS {table[0]}")
                logger.warning(f"Tabela '{table[0]}' removida")
            
            db.commit()
            Migrations.criar_tabelas()
            logger.warning("Banco de dados resetado!")
            
        except Exception as e:
            logger.error(f"Erro ao resetar banco: {e}")
            db.rollback()
            raise
