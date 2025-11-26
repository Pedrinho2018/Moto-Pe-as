"""
Config Package - MotoPeças
Configurações: variáveis de ambiente, dados de conexão
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
config_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(config_path)

# Configurações do banco de dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'motopecas_db'),
    'port': int(os.getenv('DB_PORT', 3306))
}

__all__ = ['DB_CONFIG']
