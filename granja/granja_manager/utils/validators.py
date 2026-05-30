"""Validadores para entrada de dados"""

import re
from typing import Tuple


class Validators:
    """Classe com validadores da aplicação."""

    @staticmethod
    def validar_telefone(telefone: str) -> Tuple[bool, str]:
        """Valida formato de telefone.
        
        Acceita:
        - 10 a 13 dígitos
        - Com ou sem formatação
        - Com ou sem código de país (55)
        """
        if not telefone:
            return False, "Telefone é obrigatório"
        
        # Remove tudo que não é dígito
        apenas_numeros = re.sub(r"\D", "", telefone)
        
        if not (10 <= len(apenas_numeros) <= 13):
            return False, "Telefone deve ter entre 10 e 13 dígitos"
        
        return True, ""

    @staticmethod
    def validar_quantidade(quantidade) -> Tuple[bool, str]:
        """Valida quantidade de um produto."""
        try:
            qty = int(quantidade)
            if qty <= 0:
                return False, "Quantidade deve ser maior que 0"
            return True, ""
        except (ValueError, TypeError):
            return False, "Quantidade deve ser um número inteiro"

    @staticmethod
    def validar_preco(preco) -> Tuple[bool, str]:
        """Valida preço de um produto."""
        try:
            preco_float = float(str(preco).replace(",", "."))
            if preco_float < 0:
                return False, "Preço não pode ser negativo"
            return True, ""
        except (ValueError, TypeError):
            return False, "Preço deve ser um número válido"

    @staticmethod
    def validar_estoque(estoque) -> Tuple[bool, str]:
        """Valida quantidade em estoque."""
        try:
            est = int(estoque)
            if est < 0:
                return False, "Estoque não pode ser negativo"
            return True, ""
        except (ValueError, TypeError):
            return False, "Estoque deve ser um número inteiro"

    @staticmethod
    def validar_nome_cliente(nome: str) -> Tuple[bool, str]:
        """Valida nome do cliente."""
        if not nome or not nome.strip():
            return False, "Nome do cliente é obrigatório"
        if len(nome.strip()) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres"
        return True, ""

    @staticmethod
    def validar_descricao_gasto(descricao: str) -> Tuple[bool, str]:
        """Valida descrição de um gasto."""
        if not descricao or not descricao.strip():
            return False, "Descrição é obrigatória"
        if len(descricao.strip()) < 3:
            return False, "Descrição deve ter pelo menos 3 caracteres"
        return True, ""

    @staticmethod
    def validar_email(email: str) -> Tuple[bool, str]:
        """Valida email (uso futuro)."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, email):
            return False, "Email inválido"
        return True, ""
