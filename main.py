"""
Main Entry Point - Iniciador do Sistema MotoPeças (Versão Completa)

Este é o arquivo principal que inicia toda a aplicação.
Funciona como um ponto de entrada único, controlando o fluxo entre
a tela de login e a aplicação principal.

FLUXO DO SISTEMA:
    1. Inicia um loop contínuo esperando por login
    2. Quando o funcionário faz login com sucesso, carrega a app completa
    3. Quando o funcionário faz logout, volta para tela de login
    4. Esse loop continua até o usuário fechar completamente a aplicação

COMO USAR:
    python main.py

    
TESTES:
    Funcionário: 1 (Carlos)
    Senha: 1234

VERSÃO:
    - app_completo.py: Versão completa (produtos, clientes, pedidos)

ESTE ARQUIVO (main.py) USA: app_completo.py (versão integrada)

FLUXO DO SISTEMA:
    1. LoginWindow (login.py) - Seleciona funcionário e senha
    2. DatabaseManager (database_basico.py) - Valida credenciais e acessa dados
    3. AppCompleto (app_completo.py) - Dashboard completo com todas as funcionalidades
    4. Logout retorna ao login (loop contínuo)

ARQUIVOS PRINCIPAIS:
    - main.py (este arquivo - entry point)
    - login.py (tela de login)
    - app_completo.py (aplicação completa)
    - database_basico.py (conexão MySQL + todas as queries)
    - models_basico.py (classes de dados integradas)
    - .env (credenciais do banco)

BANCO DE DADOS:
    Database: motopecas_db
    Tabelas: tb_funcionario, tb_produto, tb_cliente, tb_pedido, tb_item_pedido, tb_categoria, tb_log_estoque
    Host: localhost
    Port: 3306
"""

from core.login import LoginWindow
from app_completo import AppCompleto


def main():
    """
    Função principal - inicia o sistema MotoPeças.
    
    Mantém um loop contínuo de login/logout.
    Enquanto o usuário não fechar completamente, volta pro login após logout.
    """
    
    print("=" * 60)
    print("MotoPeças - Sistema de Vendas (Versão Completa)")
    print("=" * 60)
    print()
    
    # Loop contínuo - fica aqui até usuario fechar completamente
    while True:
        # Mostrar janela de login
        print("[SISTEMA] Iniciando LoginWindow...")
        login_window = LoginWindow()
        login_window.mainloop()
        
        # Verificar se login foi bem-sucedido
        if login_window.funcionario_id is not None:
            # Login bem-sucedido, buscar dados do funcionário
            funcionario_id = login_window.funcionario_id
            funcionario_nome = login_window.obter_usuario_nome()
            
            print(f"[OK] Login bem-sucedido para: {funcionario_nome} (ID: {funcionario_id})")
            print()
            
            # Carregar aplicação completa com dados do funcionário
            print("[SISTEMA] Iniciando AppCompleto...")
            app = AppCompleto(
                funcionario_id=funcionario_id,
                funcionario_nome=funcionario_nome
            )
            app.mainloop()
            
            # Quando app fecha, usuário fez logout
            print(f"[OK] Logout realizado. Retornando ao login...")
            print()
            # Loop continua para novo login
        else:
            # Usuário fechou janela de login sem fazer login
            # Isso significa que quer sair completamente
            print("[SISTEMA] Janela de login fechada sem autenticação.")
            break
    
    # Sai do loop - aplicação encerra
    print("[SISTEMA] Sistema finalizado.")


if __name__ == "__main__":
    main()