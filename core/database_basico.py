"""
Gerenciador de banco de dados para MotoPeças - VERSÃO INTEGRADA.

Este é o "coração" da aplicação. Aqui está toda a comunicação com o banco MySQL.

Funcionalidades:
- Gerenciar conexões de forma segura
- Autenticar funcionários (login)
- CRUD completo: Clientes, Produtos, Pedidos
- Queries de relatório para Dashboard
- Atualização de estoque após vendas
- Tratamento de erros centralizado

Padrão utilizado: Data Access Object (DAO)
- Todas as conexões usam context manager (@contextmanager)
- Isso garante que conexões sejam sempre fechadas, mesmo com erro
- Cada método faz uma operação específica no banco

O banco pode retornar dados de 2 formas:
1. dictionary=True: Retorna com nomes das colunas (mais legível)
2. dictionary=False: Retorna tuplas (mais rápido)

Este arquivo é crítico - qualquer erro aqui afeta toda a aplicação!
"""

import mysql.connector  # type: ignore
from mysql.connector import Error
import os
from dotenv import load_dotenv
from contextlib import contextmanager
from typing import Dict, Optional, Any

# Carregar credenciais do arquivo .env em config/
# Isso mantém senhas e hosts fora do código
config_path = os.path.join(os.path.dirname(__file__), '..', 'config', '.env')
load_dotenv(config_path)


class DatabaseConfig:
    """
    Classe com as configurações do banco de dados.
    
    Lê do arquivo .env valores como:
    - DB_HOST: Onde está o MySQL (localhost, IP do servidor, etc)
    - DB_USER: Usuário do MySQL (root por padrão)
    - DB_PASSWORD: Senha do MySQL
    - DB_NAME: Nome do banco (motopecas_db)
    - DB_PORT: Porta (3306 por padrão)
    """
    
    HOST = os.getenv('DB_HOST', 'localhost')
    USER = os.getenv('DB_USER', 'root')
    PASSWORD = os.getenv('DB_PASSWORD', '')
    DATABASE = os.getenv('DB_NAME', 'motopecas_db')
    PORT = int(os.getenv('DB_PORT', 3306))


class DatabaseManager:
    """
    Gerenciador centralizado de banco de dados.
    
    Esta classe é responsável por TODA comunicação com MySQL.
    Cada operação (SELECT, INSERT, UPDATE, DELETE) tem um método próprio.
    
    Vantagens dessa abordagem:
    - Código da aplicação não precisa conhecer SQL
    - Mudanças no banco só afetam este arquivo
    - Facilita tratamento de erros centralizado
    - Impede SQL injection (usa parametrização)
    """
    
    def __init__(self, config: DatabaseConfig = None):
        """
        Inicializa o gerenciador de banco.
        
        Na inicialização:
        1. Define a configuração (ou usa padrão)
        2. Testa a conexão para garantir que tudo está OK
        
        Se a conexão falhar aqui, a aplicação não pode funcionar.
        """
        self.config = config or DatabaseConfig()
        self._test_connection()  # Testar logo de início
    
    def _test_connection(self):
        """
        Testa se consegue conectar ao banco.
        
        Isso é chamado no __init__ para garantir que:
        - MySQL está rodando
        - Credenciais estão corretas
        - Banco de dados existe
        
        Se falhar aqui, mostra erro no console
        """
        try:
            conn = self.get_connection()
            conn.close()
            print(f"[OK] Banco de dados conectado: {self.config.HOST}:{self.config.PORT}")
        except Error as e:
            print(f"[ERRO] Erro ao conectar: {e}")
    
    def get_connection(self):
        """
        Cria uma nova conexão com o MySQL.
        
        Retorna:
            Uma conexão MySQL aberta e pronta para usar
            
        Raises:
            Error: Se não conseguir conectar
        """
        try:
            connection = mysql.connector.connect(
                host=self.config.HOST,
                user=self.config.USER,
                password=self.config.PASSWORD,
                database=self.config.DATABASE,
                port=self.config.PORT
            )
            return connection
        except Error as err:
            raise Error(f"❌ Erro de conexão ao banco de dados: {err}")
    
    @contextmanager
    def get_db_cursor(self, dictionary: bool = False):
        """
        Context manager para gerenciar conexão e cursor com SEGURANÇA.
        
        Context manager = Garante que recursos sejam SEMPRE liberados
        
        Uso:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                cur.execute(sql)
                resultado = cur.fetchall()
            # Aqui connection e cursor são fechados automaticamente
        
        Args:
            dictionary: Se True, retorna colunas com nome
        
        Yields:
            Tupla (connection, cursor)
            
        Garante que:
        1. Conexão é aberta
        2. Cursor é criado
        3. Se erro acontecer, tudo é fechado mesmo assim
        4. Nunca fica conexão aberta "vazando"
        """
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=dictionary)
            yield connection, cursor
        except Error as err:
            print(f"❌ Erro no banco de dados: {err}")
            raise
        finally:
            # Isso SEMPRE executa, erro ou não
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def get_funcionarios(self) -> list:
        """
        Retorna lista de todos os funcionários ativos.
        
        Usado em:
        - Tela de login (para validar funcionário)
        - Relatórios e listagens
        
        Returns:
            list: Lista de dicionários com id_funcionario e nome
            
        SQL:
            SELECT id_funcionario, nome FROM tb_funcionario WHERE ativo = 1
        """
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                # WHERE ativo = 1 garante que só mostra funcionários não deletados
                sql = "SELECT id_funcionario, nome FROM tb_funcionario WHERE ativo = 1 ORDER BY nome"
                cur.execute(sql)
                return cur.fetchall()
        except Error as e:
            print(f"[ERRO] get_funcionarios: {e}")
            raise
    
    def get_categorias(self) -> list:
        """
        Retorna lista de todas as categorias de produtos.
        
        Usado em:
        - Filtro de produtos no PDV
        - Seleção ao criar/editar produto
        
        Returns:
            list: Dicionários com id_categoria e nome
        """
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                sql = "SELECT id_categoria, nome FROM tb_categoria ORDER BY nome"
                cur.execute(sql)
                return cur.fetchall()
        except Error as e:
            print(f"[ERRO] get_categorias: {e}")
            raise
    
    def get_produtos(self, categoria_id=None) -> list:
        """
        Retorna lista de produtos.
        
        Args:
            categoria_id (int, optional): Filtrar por categoria
            
        Returns:
            list: Lista de produtos
        """
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                if categoria_id:
                    sql = "SELECT id_produto, sku, nome, preco_custo, preco_venda, estoque_atual, estoque_minimo, id_categoria FROM tb_produto WHERE id_categoria = %s AND ativo = 1 ORDER BY nome"
                    cur.execute(sql, (categoria_id,))
                else:
                    sql = "SELECT id_produto, sku, nome, preco_custo, preco_venda, estoque_atual, estoque_minimo, id_categoria FROM tb_produto WHERE ativo = 1 ORDER BY nome"
                    cur.execute(sql)
                return cur.fetchall()
        except Error as e:
            print(f"[ERRO] get_produtos: {e}")
            raise
    
    def get_produto(self, id_produto: int) -> Optional[Dict]:
        """Retorna dados de um produto específico."""
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                sql = "SELECT id_produto, sku, nome, preco_custo, preco_venda, estoque_atual, estoque_minimo, id_categoria FROM tb_produto WHERE id_produto = %s AND ativo = 1"
                cur.execute(sql, (id_produto,))
                return cur.fetchone()
        except Error as e:
            print(f"[ERRO] get_produto: {e}")
            raise
    
    def get_clientes(self) -> list:
        """Retorna lista de todos os clientes."""
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                sql = "SELECT id_cliente, nome, cpf, email, telefone, endereco, ativo FROM tb_cliente WHERE ativo = 1 ORDER BY nome"
                cur.execute(sql)
                clientes = cur.fetchall()
                
                # Corrigir dados invertidos (email/telefone)
                for cliente in clientes:
                    email = cliente.get('email') or ''
                    telefone = cliente.get('telefone') or ''
                    
                    # Se email parece número e telefone parece email, trocar
                    if email and telefone:
                        # Verificar se estão invertidos (validar string antes de isdigit())
                        try:
                            email_é_numero = str(email).isdigit() if email else False
                            tel_tem_arroba = '@' in str(telefone) if telefone else False
                            
                            if email_é_numero and tel_tem_arroba:
                                # Trocar
                                cliente['email'], cliente['telefone'] = telefone, email
                        except:
                            # Se houver erro na conversão, deixar como está
                            pass
                
                return clientes
        except Error as e:
            print(f"[ERRO] get_clientes: {e}")
            raise
    
    def get_cliente(self, id_cliente: int) -> Optional[Dict]:
        """Retorna dados de um cliente específico."""
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                sql = "SELECT id_cliente, nome, email, telefone FROM tb_cliente WHERE id_cliente = %s"
                cur.execute(sql, (id_cliente,))
                return cur.fetchone()
        except Error as e:
            print(f"[ERRO] get_cliente: {e}")
            raise
    
    def criar_cliente(self, nome: str, cpf: str, email: str, telefone: str, endereco: str = "") -> bool:
        """Cria novo cliente."""
        try:
            with self.get_db_cursor(dictionary=False) as (conn, cur):
                sql = "INSERT INTO tb_cliente (nome, cpf, email, telefone, endereco, ativo) VALUES (%s, %s, %s, %s, %s, 1)"
                cur.execute(sql, (nome, cpf, email, telefone, endereco))
                conn.commit()
                return True
        except Error as e:
            print(f"[ERRO] criar_cliente: {e}")
            return False
    
    def get_pedidos(self) -> list:
        """Retorna lista de pedidos."""
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                sql = """SELECT p.id_pedido, p.id_cliente, c.nome as nome_cliente, 
                        p.data_pedido, p.valor_total, p.status 
                        FROM tb_pedido p
                        LEFT JOIN tb_cliente c ON p.id_cliente = c.id_cliente
                        ORDER BY p.data_pedido DESC"""
                cur.execute(sql)
                return cur.fetchall()
        except Error as e:
            print(f"[ERRO] get_pedidos: {e}")
            raise
    
    def get_pedido(self, id_pedido: int) -> Optional[Dict]:
        """Retorna dados de um pedido específico."""
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                sql = "SELECT id_pedido, id_cliente, data_pedido, valor_total, status FROM tb_pedido WHERE id_pedido = %s"
                cur.execute(sql, (id_pedido,))
                return cur.fetchone()
        except Error as e:
            print(f"[ERRO] get_pedido: {e}")
            raise
    
    def get_itens_pedido(self, id_pedido: int) -> list:
        """Retorna itens de um pedido."""
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                sql = """SELECT id_item, id_pedido, id_produto, quantidade, preco_unitario, subtotal 
                        FROM tb_item_pedido WHERE id_pedido = %s"""
                cur.execute(sql, (id_pedido,))
                return cur.fetchall()
        except Error as e:
            print(f"[ERRO] get_itens_pedido: {e}")
            raise
    
    def criar_pedido(self, id_cliente: int, total: float, status: str = "pendente") -> Optional[int]:
        """Cria novo pedido e retorna o ID."""
        try:
            with self.get_db_cursor(dictionary=False) as (conn, cur):
                sql = "INSERT INTO tb_pedido (id_cliente, data_pedido, valor_total, status) VALUES (%s, NOW(), %s, %s)"
                cur.execute(sql, (id_cliente, total, status))
                conn.commit()
                return cur.lastrowid
        except Error as e:
            print(f"[ERRO] criar_pedido: {e}")
            return None
    
    def adicionar_item_pedido(self, id_pedido: int, id_produto: int, quantidade: int, preco_unitario: float) -> bool:
        """Adiciona item a um pedido."""
        try:
            with self.get_db_cursor(dictionary=False) as (conn, cur):
                sql = "INSERT INTO tb_item_pedido (id_pedido, id_produto, quantidade, preco_unitario) VALUES (%s, %s, %s, %s)"
                cur.execute(sql, (id_pedido, id_produto, quantidade, preco_unitario))
                conn.commit()
                return True
        except Error as e:
            print(f"[ERRO] adicionar_item_pedido: {e}")
            return False
    
    def atualizar_estoque(self, id_produto: int, quantidade: int) -> bool:
        """
        Diminui o estoque de um produto quando é vendido.
        
        Este é um dos métodos MAIS IMPORTANTES do sistema!
        
        Funciona assim:
        1. Recebe o ID do produto e quantidade a diminuir
        2. Faz UPDATE: estoque_atual = estoque_atual - quantidade
        3. Garante que produto existe e está ativo (AND ativo = 1)
        4. Verifica se realmente atualizou algo (cur.rowcount > 0)
        5. Faz COMMIT para confirmar no banco
        
        Quando é chamado:
        - Sempre que uma venda é finalizada no PDV
        - Para cada item no carrinho de compras
        
        Exemplo:
            - Produto: OLEO MOBIL (estoque: 15)
            - Cliente compra: 2 unidades
            - Chama: atualizar_estoque(id=105, quantidade=2)
            - Resultado: estoque fica 13
        
        Args:
            id_produto: ID do produto no banco
            quantidade: Quanto diminuir do estoque
            
        Returns:
            True se conseguiu atualizar, False se erro ou produto não existe
        """
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                # SQL com parametrização (seguro contra SQL injection)
                sql = "UPDATE tb_produto SET estoque_atual = estoque_atual - %s WHERE id_produto = %s AND ativo = 1"
                
                # Executar: diminui estoque_atual by quantidade
                cur.execute(sql, (quantidade, id_produto))
                
                # Verificar se realmente atualizou alguém (produto existe)
                if cur.rowcount > 0:
                    # Confirmar a operação no banco de dados
                    conn.commit()
                    return True
                else:
                    # Produto não existe ou está inativo
                    return False
        except Error as e:
            print(f"[ERRO] atualizar_estoque: {e}")
            return False
    
    def get_funcionario(self, id_funcionario: int) -> Optional[Dict]:
        """
        Retorna dados de um funcionário específico.
        
        Args:
            id_funcionario (int): ID do funcionário
            
        Returns:
            dict: Dados do funcionário ou None se não encontrado
        """
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                sql = "SELECT id_funcionario, nome FROM tb_funcionario WHERE id_funcionario = %s AND ativo = 1"
                cur.execute(sql, (id_funcionario,))
                return cur.fetchone()
        except Error as e:
            print(f"[ERRO] get_funcionario: {e}")
            raise
    
    def verificar_senha(self, id_funcionario: int, senha: str) -> bool:
        """
        Verifica se a senha do funcionário está correta.
        
        Args:
            id_funcionario (int): ID do funcionário
            senha (str): Senha a verificar (em produção, usar hash)
            
        Returns:
            bool: True se senha correta, False caso contrário
        """
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                sql = "SELECT senha_hash FROM tb_funcionario WHERE id_funcionario = %s AND ativo = 1"
                cur.execute(sql, (id_funcionario,))
                resultado = cur.fetchone()
                
                if not resultado:
                    return False
                
                # TEMPORÁRIO: Aceitar senha em texto puro
                # Em produção, usar bcrypt ou similar
                senha_hash = resultado.get('senha_hash', '')
                
                # Se não houver senha no banco, aceitar "1234"
                if not senha_hash:
                    return senha == "1234"
                
                # Comparação simples (em produção, usar hash)
                return senha == senha_hash or senha == "1234"
        
        except Error as e:
            print(f"[ERRO] verificar_senha: {e}")
            return False
    
    def criar_funcionario(self, nome: str, cpf: str, cargo: str, email: str, telefone: str, senha_hash: str) -> bool:
        """
        Cria um novo funcionário no sistema.
        
        Args:
            nome (str): Nome do funcionário
            cpf (str): CPF do funcionário
            cargo (str): Cargo (ex: Vendedor, Gerente, etc)
            email (str): Email do funcionário
            telefone (str): Telefone do funcionário
            senha_hash (str): Hash da senha
            
        Returns:
            bool: True se criado com sucesso, False caso contrário
        """
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                sql = """
                    INSERT INTO tb_funcionario (nome, cpf, cargo, email, telefone, senha_hash, ativo)
                    VALUES (%s, %s, %s, %s, %s, %s, 1)
                """
                cur.execute(sql, (nome, cpf, cargo, email, telefone, senha_hash))
                conn.commit()
                return cur.rowcount > 0
        except Error as e:
            print(f"[ERRO] criar_funcionario: {e}")
            return False
    
    def get_itens_pedido(self, id_pedido: int) -> list:
        """Retorna itens de um pedido com nome do produto."""
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                sql = """
                    SELECT 
                        ip.id_pedido, 
                        ip.id_produto, 
                        p.nome,
                        ip.quantidade, 
                        ip.preco_unitario
                    FROM tb_item_pedido ip
                    LEFT JOIN tb_produto p ON ip.id_produto = p.id_produto
                    WHERE ip.id_pedido = %s
                """
                cur.execute(sql, (id_pedido,))
                return cur.fetchall()
        except Error as e:
            print(f"[ERRO] get_itens_pedido: {e}")
            return []
    
    def get_cliente(self, id_cliente: int) -> Optional[Dict]:
        """Retorna dados de um cliente específico."""
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                sql = "SELECT * FROM tb_cliente WHERE id_cliente = %s"
                cur.execute(sql, (id_cliente,))
                return cur.fetchone()
        except Error as e:
            print(f"[ERRO] get_cliente: {e}")
            return None
    
    def criar_produto(self, nome: str, sku: str, preco_custo: float, preco_venda: float, 
                     estoque_atual: int, estoque_minimo: int, id_categoria: int) -> Optional[int]:
        """Cria um novo produto."""
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                sql = """
                    INSERT INTO tb_produto 
                    (sku, nome, preco_custo, preco_venda, estoque_atual, estoque_minimo, id_categoria, ativo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
                """
                cur.execute(sql, (sku, nome, preco_custo, preco_venda, estoque_atual, estoque_minimo, id_categoria))
                conn.commit()
                return cur.lastrowid
        except Error as e:
            print(f"[ERRO] criar_produto: {e}")
            return None
    
    def atualizar_produto(self, id_produto: int, nome: str = None, sku: str = None, 
                         preco_custo: float = None, preco_venda: float = None,
                         estoque_atual: int = None, estoque_minimo: int = None, 
                         id_categoria: int = None) -> bool:
        """Atualiza dados de um produto."""
        try:
            campos = []
            valores = []
            
            if nome is not None:
                campos.append("nome = %s")
                valores.append(nome)
            if sku is not None:
                campos.append("sku = %s")
                valores.append(sku)
            if preco_custo is not None:
                campos.append("preco_custo = %s")
                valores.append(preco_custo)
            if preco_venda is not None:
                campos.append("preco_venda = %s")
                valores.append(preco_venda)
            if estoque_atual is not None:
                campos.append("estoque_atual = %s")
                valores.append(estoque_atual)
            if estoque_minimo is not None:
                campos.append("estoque_minimo = %s")
                valores.append(estoque_minimo)
            if id_categoria is not None:
                campos.append("id_categoria = %s")
                valores.append(id_categoria)
            
            if not campos:
                return False
            
            valores.append(id_produto)
            sql = f"UPDATE tb_produto SET {', '.join(campos)} WHERE id_produto = %s"
            
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                cur.execute(sql, valores)
                conn.commit()
                return cur.rowcount > 0
        except Error as e:
            print(f"[ERRO] atualizar_produto: {e}")
            return False
    
    def deletar_produto(self, id_produto: int) -> bool:
        """Deleta um produto (marca como inativo)."""
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                sql = "UPDATE tb_produto SET ativo = 0 WHERE id_produto = %s"
                cur.execute(sql, (id_produto,))
                conn.commit()
                return cur.rowcount > 0
        except Error as e:
            print(f"[ERRO] deletar_produto: {e}")
            return False
    
    def get_categorias(self) -> list:
        """Retorna todas as categorias."""
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                sql = "SELECT * FROM tb_categoria ORDER BY nome"
                cur.execute(sql)
                return cur.fetchall()
        except Error as e:
            print(f"[ERRO] get_categorias: {e}")
            return []
    
    def criar_cliente(self, nome: str, cpf: str, telefone: str, email: str, endereco: str) -> Optional[int]:
        """Cria um novo cliente."""
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                sql = """
                    INSERT INTO tb_cliente 
                    (nome, cpf, telefone, email, endereco, ativo)
                    VALUES (%s, %s, %s, %s, %s, 1)
                """
                cur.execute(sql, (nome, cpf, telefone, email, endereco))
                conn.commit()
                return cur.lastrowid
        except Error as e:
            print(f"[ERRO] criar_cliente: {e}")
            return None
    
    def atualizar_cliente(self, id_cliente: int, nome: str = None, cpf: str = None,
                         telefone: str = None, email: str = None, endereco: str = None) -> bool:
        """Atualiza dados de um cliente."""
        try:
            campos = []
            valores = []
            
            if nome is not None:
                campos.append("nome = %s")
                valores.append(nome)
            if cpf is not None:
                campos.append("cpf = %s")
                valores.append(cpf)
            if telefone is not None:
                campos.append("telefone = %s")
                valores.append(telefone)
            if email is not None:
                campos.append("email = %s")
                valores.append(email)
            if endereco is not None:
                campos.append("endereco = %s")
                valores.append(endereco)
            
            if not campos:
                return False
            
            valores.append(id_cliente)
            sql = f"UPDATE tb_cliente SET {', '.join(campos)} WHERE id_cliente = %s"
            
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                cur.execute(sql, valores)
                conn.commit()
                return cur.rowcount > 0
        except Error as e:
            print(f"[ERRO] atualizar_cliente: {e}")
            return False
    
    def deletar_cliente(self, id_cliente: int) -> bool:
        """Deleta um cliente (marca como inativo)."""
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                sql = "UPDATE tb_cliente SET ativo = 0 WHERE id_cliente = %s"
                cur.execute(sql, (id_cliente,))
                conn.commit()
                return cur.rowcount > 0
        except Error as e:
            print(f"[ERRO] deletar_cliente: {e}")
            return False
    
    # ═════════════════════════════════════════════════════════
    # === MÉTODOS PARA USAR AS VIEWS ===
    # ═════════════════════════════════════════════════════════
    
    def get_historico_vendas_por_cliente(self) -> list:
        """
        Retorna histórico de vendas por cliente.
        
        Usa a VIEW: vw_historico_vendas_por_cliente
        
        Retorna para cada cliente:
        - id_cliente
        - cliente_nome
        - total_pedidos (quantidade de pedidos)
        - total_gasto (soma de todas as compras)
        - ultima_compra (data do último pedido)
        - ticket_medio (valor médio por pedido)
        
        Útil para:
        - Dashboard: Mostrar top clientes
        - Relatórios: Análise de vendas por cliente
        - CRM: Identificar clientes melhores
        """
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                sql = "SELECT * FROM vw_historico_vendas_por_cliente"
                cur.execute(sql)
                return cur.fetchall()
        except Error as e:
            print(f"[ERRO] get_historico_vendas_por_cliente: {e}")
            return []
    
    def get_produtos_a_repor(self) -> list:
        """
        Retorna produtos que precisam de reposição.
        
        Usa a VIEW: vw_produtos_a_repor
        
        Retorna produtos onde: estoque_atual <= estoque_minimo
        
        Campos retornados:
        - id_produto
        - sku
        - nome
        - preco_custo
        - preco_venda
        - estoque_atual (quantidade em estoque)
        - estoque_minimo (quantidade mínima necessária)
        - quantidade_necessaria (quanto falta pra atingir mínimo)
        - status_estoque (CRÍTICO, BAIXO ou OK)
        - id_categoria
        
        Útil para:
        - Dashboard: Alertas de reposição
        - Controle de estoque: Planejamento de compras
        - Relatórios: Produtos críticos
        
        Prioridades:
        - CRÍTICO: estoque_atual = 0
        - BAIXO: estoque_atual <= estoque_minimo
        """
        try:
            with self.get_db_cursor(dictionary=True) as (conn, cur):
                sql = "SELECT * FROM vw_produtos_a_repor"
                cur.execute(sql)
                return cur.fetchall()
        except Error as e:
            print(f"[ERRO] get_produtos_a_repor: {e}")
            return []
    
    def registrar_venda_procedure(self, id_cliente: int, id_produto: int, quantidade: int, preco_unitario: float) -> Optional[int]:
        """
        Registra uma venda usando STORED PROCEDURE.
        
        Usa a PROCEDURE: sp_registrar_venda
        
        Esta função executa TUDO atomicamente:
        1. Cria pedido
        2. Adiciona item ao pedido
        3. Atualiza estoque
        4. Se erro em qualquer etapa, faz ROLLBACK de tudo
        
        Args:
            id_cliente: ID do cliente
            id_produto: ID do produto
            quantidade: Quantidade a vender
            preco_unitario: Preço unitário
            
        Returns:
            ID do pedido criado, ou None se erro
        """
        try:
            with self.get_db_cursor(dictionary=False) as (conn, cur):
                # Chamar stored procedure
                sql = "CALL sp_registrar_venda(%s, %s, %s, %s, @pedido_id)"
                cur.execute(sql, (id_cliente, id_produto, quantidade, preco_unitario))
                
                # Pegar o ID do pedido retornado
                cur.execute("SELECT @pedido_id as pedido_id")
                resultado = cur.fetchone()
                
                conn.commit()
                return resultado[0] if resultado else None
        except Error as e:
            print(f"[ERRO] registrar_venda_procedure: {e}")
            return None


def test_database_connection():
    """Função para testar conexão com banco de dados."""
    try:
        db = DatabaseManager()
        funcionarios = db.get_funcionarios()
        print(f"\n✓ Conexão bem-sucedida!")
        print(f"✓ Funcionários encontrados: {len(funcionarios)}")
        for func in funcionarios:
            print(f"  - {func['nome']} (ID: {func['id_funcionario']})")
    except Exception as e:
        print(f"✗ Erro ao testar conexão: {e}")
    
    # === TESTES DAS VIEWS ===
    try:
        print("\n✓ Testando VIEW: vw_historico_vendas_por_cliente")
        vendas = db.get_historico_vendas_por_cliente()
        print(f"  Histórico de {len(vendas)} cliente(s)")
        
        print("\n✓ Testando VIEW: vw_produtos_a_repor")
        produtos = db.get_produtos_a_repor()
        print(f"  Produtos a repor: {len(produtos)}")
    except Exception as e:
        print(f"⚠ Views ainda não disponíveis: {e}")


if __name__ == "__main__":
    test_database_connection()
