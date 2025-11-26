"""
Core Module - MotoPeças
Módulo de infraestrutura: banco de dados, autenticação e modelos
"""

from .database_basico import DatabaseManager
from .models_basico import Cliente, Produto, Pedido
from .login import LoginWindow

__all__ = ['DatabaseManager', 'Cliente', 'Produto', 'Pedido', 'LoginWindow']
