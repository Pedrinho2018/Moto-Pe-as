"""
Modelos de dados para MotoPeças - VERSÃO INTEGRADA.

Contém classes para todas as entidades do sistema.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Funcionario:
    """Modelo de dados para Funcionário."""
    id_funcionario: int
    nome: str
    ativo: bool = True


@dataclass
class Categoria:
    """Modelo de dados para Categoria de Produtos."""
    id_categoria: int
    nome: str


@dataclass
class Produto:
    """Modelo de dados para Produto."""
    id_produto: int
    nome: str
    preco: float
    estoque: int
    id_categoria: int


@dataclass
class Cliente:
    """Modelo de dados para Cliente."""
    id_cliente: int
    nome: str
    email: str
    telefone: str


@dataclass
class ItemPedido:
    """Modelo de dados para Item de Pedido."""
    id_item: int
    id_pedido: int
    id_produto: int
    quantidade: int
    preco_unitario: float
    subtotal: float


@dataclass
class Pedido:
    """Modelo de dados para Pedido."""
    id_pedido: int
    id_cliente: int
    data_pedido: datetime
    total: float
    status: str

