# OBSOLETO: substituído pelo Supabase. Este arquivo não é mais utilizado.

"""Seed inicial do banco de dados"""

import uuid
from datetime import datetime
import logging
from .connection import db
from ..models import Produto

logger = logging.getLogger(__name__)


class Seed:
    """Popula o banco de dados com dados iniciais."""

    @staticmethod
    def executar():
        """Executa o seed se o banco estiver vazio."""
        try:
            db.connect()
            
            # Verifica se há produtos
            resultado = db.fetchone("SELECT COUNT(*) FROM produtos")
            if resultado[0] > 0:
                logger.info("Banco já possui dados, skip seed")
                return

            logger.info("Iniciando seed inicial...")
            db.begin_transaction()

            # Produtos padrão
            produtos = [
                ("Dúzia de Ovos Caipira", 18.00, 120),
                ("Dúzia de Ovos Brancos", 12.50, 200),
                ("Frango Inteiro (kg)", 22.00, 35),
                ("Filé de Frango (kg)", 28.00, 20),
                ("Coxa de Frango (kg)", 18.50, 40),
            ]

            for nome, preco, estoque in produtos:
                produto_id = str(uuid.uuid4())
                db.execute("""
                    INSERT INTO produtos (id, nome, preco, estoque, ativo)
                    VALUES (?, ?, ?, ?, 1)
                """, (produto_id, nome, preco, estoque))
                logger.info(f"Produto criado: {nome}")

            db.end_transaction()
            logger.info("Seed inicial concluído com sucesso!")

        except Exception as e:
            logger.error(f"Erro ao executar seed: {e}")
            db.rollback()
            raise
