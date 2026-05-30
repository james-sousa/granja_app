"""Helpers e utilitários gerais"""

import os
import logging
from typing import Optional
from datetime import datetime


def setup_logging(log_file: str = "logs/app.log") -> None:
    """Configura o sistema de logging da aplicação."""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info(f"Aplicação iniciada em {datetime.now().isoformat()}")
    logger.info("=" * 50)


def limpar_string(texto: Optional[str]) -> str:
    """Remove espaços em branco extras de uma string."""
    if not texto:
        return ""
    return " ".join(texto.split())


def normalizar_telefone(telefone: str) -> str:
    """Normaliza um telefone removendo caracteres especiais."""
    if not telefone:
        return ""
    # Remove tudo que não é dígito
    return "".join(filter(str.isdigit, telefone))


def gerar_id_unico() -> str:
    """Gera um ID único."""
    import uuid
    return str(uuid.uuid4())


def eh_numero(valor) -> bool:
    """Verifica se um valor é um número."""
    try:
        float(valor)
        return True
    except (ValueError, TypeError):
        return False


def pegar_extenso(numero: int) -> str:
    """Converte número para sua forma extensa (uso futuro)."""
    unidades = ["", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove"]
    
    if numero < len(unidades):
        return unidades[numero]
    return str(numero)


class TimeHelper:
    """Utilitários para trabalhar com tempo."""

    @staticmethod
    def agora() -> datetime:
        """Retorna o momento atual."""
        return datetime.now()

    @staticmethod
    def hoje() -> str:
        """Retorna a data de hoje no formato YYYY-MM-DD."""
        return datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def timestamp() -> int:
        """Retorna o timestamp atual em segundos."""
        return int(datetime.now().timestamp())

    @staticmethod
    def dias_passados(data: datetime) -> int:
        """Calcula quantos dias passaram desde uma data."""
        delta = datetime.now() - data
        return delta.days


class FileHelper:
    """Utilitários para trabalhar com arquivos."""

    @staticmethod
    def arquivo_existe(caminho: str) -> bool:
        """Verifica se um arquivo existe."""
        return os.path.isfile(caminho)

    @staticmethod
    def diretorio_existe(caminho: str) -> bool:
        """Verifica se um diretório existe."""
        return os.path.isdir(caminho)

    @staticmethod
    def criar_diretorio(caminho: str) -> bool:
        """Cria um diretório se não existir."""
        try:
            os.makedirs(caminho, exist_ok=True)
            return True
        except Exception:
            return False

    @staticmethod
    def tamanho_arquivo(caminho: str) -> int:
        """Retorna o tamanho de um arquivo em bytes."""
        try:
            return os.path.getsize(caminho)
        except Exception:
            return 0
