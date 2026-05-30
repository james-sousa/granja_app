"""Repositório base abstrato"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any


class BaseRepository(ABC):
    """Classe base para todos os repositórios."""

    @abstractmethod
    def create(self, obj: Any) -> str:
        """Cria um novo registro."""
        pass

    @abstractmethod
    def update(self, obj: Any) -> bool:
        """Atualiza um registro existente."""
        pass

    @abstractmethod
    def delete(self, obj_id: str) -> bool:
        """Deleta um registro."""
        pass

    @abstractmethod
    def find_by_id(self, obj_id: str) -> Optional[Any]:
        """Encontra um registro pelo ID."""
        pass

    @abstractmethod
    def find_all(self) -> List[Any]:
        """Retorna todos os registros."""
        pass

    @abstractmethod
    def search(self, query: str) -> List[Any]:
        """Pesquisa registros."""
        pass
