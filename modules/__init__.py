"""
Modules Package - MotoPeças
Módulos de funcionalidades: dashboard, CRUD, PDV
"""

from .dashboard import Dashboard
from .crud_produtos import CRUDProdutos
from .crud_clientes import CRUDClientes
from .tela_pedidos import TelaPedidos
from .pdv import PontoDeVenda
from .pdv_melhorado import PontoDeVendaMelhorado

__all__ = [
    'Dashboard',
    'CRUDProdutos',
    'CRUDClientes',
    'TelaPedidos',
    'PontoDeVenda',
    'PontoDeVendaMelhorado'
]
