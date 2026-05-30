"""Serviço de Produto"""

import uuid
from typing import List, Optional
import logging
from ..models import Produto
from ..database.repositories import ProdutoRepository

logger = logging.getLogger(__name__)


class ProdutoService:
    """Serviço para gerenciar produtos."""

    def __init__(self):
        self.produto_repo = ProdutoRepository()

    def criar_produto(self, nome: str, preco: float, estoque: int = 0) -> Produto:
        """Cria um novo produto.
        
        Args:
            nome: Nome do produto
            preco: Preço unitário
            estoque: Quantidade em estoque (padrão: 0)
            
        Returns:
            Produto criado
        """
        if not nome or not nome.strip():
            raise ValueError("Nome do produto é obrigatório")
        if preco < 0:
            raise ValueError("Preço não pode ser negativo")
        if estoque < 0:
            raise ValueError("Estoque não pode ser negativo")
        
        produto = Produto(
            id=str(uuid.uuid4()),
            nome=nome.strip(),
            preco=preco,
            estoque=estoque,
            ativo=1
        )
        
        produto_id = self.produto_repo.create(produto)
        logger.info(f"Produto criado: {nome}")
        return self.produto_repo.find_by_id(produto_id)

    def atualizar_produto(self, produto_id: str, nome: str, preco: float, estoque: int) -> bool:
        """Atualiza um produto existente."""
        if preco < 0:
            raise ValueError("Preço não pode ser negativo")
        if estoque < 0:
            raise ValueError("Estoque não pode ser negativo")
        
        produto = self.produto_repo.find_by_id(produto_id)
        if not produto:
            raise ValueError(f"Produto {produto_id} não encontrado")
        
        produto.nome = nome.strip()
        produto.preco = preco
        produto.estoque = estoque
        
        resultado = self.produto_repo.update(produto)
        logger.info(f"Produto atualizado: {produto_id}")
        return resultado

    def obter_produto(self, produto_id: str) -> Optional[Produto]:
        """Obtém um produto pelo ID."""
        return self.produto_repo.find_by_id(produto_id)

    def listar_produtos(self) -> List[Produto]:
        """Lista todos os produtos."""
        return self.produto_repo.find_all()

    def pesquisar_produtos(self, query: str) -> List[Produto]:
        """Pesquisa produtos por nome."""
        return self.produto_repo.search(query)

    def deletar_produto(self, produto_id: str) -> bool:
        """Deleta um produto."""
        return self.produto_repo.delete(produto_id)

    def validar_estoque(self, produto_id: str, quantidade: int) -> bool:
        """Valida se há estoque suficiente."""
        produto = self.obter_produto(produto_id)
        return produto and produto.estoque >= quantidade

    def verificar_alerta_estoque(self, produto_id: str, limite_minimo: int = 10) -> bool:
        """Verifica se o estoque está baixo."""
        produto = self.obter_produto(produto_id)
        return produto and produto.estoque < limite_minimo
