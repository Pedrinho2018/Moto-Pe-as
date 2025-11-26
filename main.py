# -*- coding: utf-8 -*-
"""
Main Entry Point - Iniciador do Sistema MotoPeças

Este é o arquivo principal que inicia toda a aplicação.
Funciona como um ponto de entrada único, controlando o fluxo entre
a tela de login e a aplicação principal.

FLUXO DO SISTEMA:
    1. LoginWindow (login.py) - Autentica funcionário
    2. AppPrincipal - Interface principal com abas:
       - Dashboard
       - PDV (Ponto de Venda)
       - Pedidos
       - CRUD Produtos
       - CRUD Clientes

COMO USAR:
    python main.py

CREDENCIAIS:
    Funcionário: 2 - Vendedor Carlos
    Senha: 123456 (criptografada com bcrypt)

ARQUIVOS PRINCIPAIS:
    - main.py (este arquivo - entry point)
    - core/login.py (tela de login com bcrypt)
    - core/database_basico.py (conexão MySQL)
    - modules/dashboard.py (dashboards e gráficos)
    - modules/pdv_melhorado.py (ponto de venda com quantidade editável)
    - modules/tela_pedidos.py (gerenciamento de pedidos)
    - modules/crud_produtos.py (cadastro de produtos)
    - modules/crud_clientes.py (cadastro de clientes)
"""

import customtkinter as ctk  # type: ignore
from tkinter import messagebox
from core.login import LoginWindow
from core.database_basico import DatabaseManager
from modules.dashboard import Dashboard
from modules.pdv_melhorado import PontoDeVendaMelhorado
from modules.tela_pedidos import TelaPedidos
from modules.crud_produtos import CRUDProdutos
from modules.crud_clientes import CRUDClientes


class AppPrincipal(ctk.CTk):
    """
    Aplicação Principal - Interface com múltiplas abas.
    
    Mostra após o login bem-sucedido.
    Contém: Dashboard, PDV, Pedidos, CRUD Produtos, CRUD Clientes
    """
    
    def __init__(self, funcionario_id: int, funcionario_nome: str):
        super().__init__()
        
        self.funcionario_id = funcionario_id
        self.funcionario_nome = funcionario_nome
        self.db = DatabaseManager()
        
        # Configurar janela
        self.title(f"MotoPeças 🏍️ - {funcionario_nome}")
        self.geometry("1600x950")
        self.minsize(1200, 700)
        
        # Tema profissional
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configurar cores personalizadas
        self.configure(fg_color="#0a0e27")  # Azul escuro profissional
        
        # Criar abas
        self._criar_abas()
    
    def _criar_abas(self):
        """Cria as abas principais do sistema com design melhorado."""
        
        # Frame principal com cor de fundo
        main_frame = ctk.CTkFrame(self, fg_color="#0a0e27")
        main_frame.pack(fill="both", expand=True)
        
        # Header com título e info do usuário
        header_frame = ctk.CTkFrame(main_frame, fg_color="#1a1f3a", height=60, corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Título
        titulo = ctk.CTkLabel(
            header_frame,
            text="🏍️ MotoPeças - Sistema de Gestão",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#00d9ff"
        )
        titulo.pack(side="left", padx=20, pady=10)
        
        # Info do usuário
        info_usuario = ctk.CTkLabel(
            header_frame,
            text=f"👤 {self.funcionario_nome}",
            font=ctk.CTkFont(size=12),
            text_color="#a0aec0"
        )
        info_usuario.pack(side="right", padx=20, pady=10)
        
        # Frame para abas com estilo
        tabs_frame = ctk.CTkFrame(main_frame, fg_color="#0f1629", height=50, corner_radius=0)
        tabs_frame.pack(fill="x", padx=0, pady=0)
        tabs_frame.pack_propagate(False)
        
        # Segmentado control para abas (melhorado)
        abas = ctk.CTkSegmentedButton(
            tabs_frame,
            values=["📊 Dashboard", "🛒 PDV", "📦 Pedidos", "📝 Produtos", "👥 Clientes"],
            command=self._mudar_aba,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#1a1f3a",
            selected_color="#0066cc",
            text_color="#a0aec0",
            corner_radius=8
        )
        abas.pack(fill="x", padx=15, pady=8)
        abas.set("📊 Dashboard")
        
        # Container para conteúdo das abas
        self.container = ctk.CTkFrame(main_frame, fg_color="#0a0e27", corner_radius=0)
        self.container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Armazenar abas criadas para não recriar
        self.abas_criadas = {}
        
        # Criar primeira aba
        self._mudar_aba("📊 Dashboard")
    
    def _mudar_aba(self, aba_selecionada):
        """Muda entre abas."""
        
        # Se já foi criada, mostrar novamente (exceto Dashboard que sempre recarrega)
        if aba_selecionada in self.abas_criadas and "Dashboard" not in aba_selecionada:
            # Verificar se o widget ainda existe
            try:
                if self.abas_criadas[aba_selecionada].winfo_exists():
                    for widget in self.container.winfo_children():
                        widget.pack_forget()
                    self.abas_criadas[aba_selecionada].pack(fill="both", expand=True)
                    return
            except:
                pass
            # Se widget foi destruído, remover do cache
            del self.abas_criadas[aba_selecionada]
        
        # Limpar container
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Remover Dashboard do cache se for selecionar ele (força recarregar)
        if "Dashboard" in aba_selecionada and aba_selecionada in self.abas_criadas:
            try:
                self.abas_criadas[aba_selecionada].destroy()
            except:
                pass
            del self.abas_criadas[aba_selecionada]
        
        # Criar nova aba
        novo_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        novo_frame.pack(fill="both", expand=True)
        
        try:
            if "Dashboard" in aba_selecionada:
                Dashboard(novo_frame, self.db, self.funcionario_id)
            
            elif "PDV" in aba_selecionada:
                # PDV integrado como frame na aba
                PontoDeVendaMelhorado(novo_frame, self.funcionario_id, self.funcionario_nome)
            
            elif "Pedidos" in aba_selecionada:
                TelaPedidos(novo_frame, self.db)
            
            elif "Produtos" in aba_selecionada:
                CRUDProdutos(novo_frame, self.db)
            
            elif "Clientes" in aba_selecionada:
                CRUDClientes(novo_frame, self.db)
            
            # Armazenar frame criado
            self.abas_criadas[aba_selecionada] = novo_frame
            
        except Exception as e:
            print(f"[ERRO] {aba_selecionada}: {e}")
            import traceback
            traceback.print_exc()
            ctk.CTkLabel(
                novo_frame, 
                text=f"❌ Erro ao carregar: {str(e)[:100]}",
                text_color="#ff6666"
            ).pack(pady=20)


def main():
    """
    Função principal - inicia o sistema MotoPeças com loop de login/logout.
    """
    
    print("=" * 70)
    print("[MotoPecas] Sistema de Vendas")
    print("=" * 70)
    print()
    
    # Loop contínuo - fica aqui até usuario fechar completamente
    while True:
        print("[SISTEMA] Abrindo LoginWindow...")
        login_window = LoginWindow()
        login_window.mainloop()
        
        # Verificar se login foi bem-sucedido
        if login_window.funcionario_id is not None:
            funcionario_id = login_window.funcionario_id
            funcionario_nome = login_window.obter_usuario_nome()
            
            print(f"[OK] Login bem-sucedido: {funcionario_nome} (ID: {funcionario_id})")
            print()
            
            # Carregar aplicação principal
            print("[SISTEMA] Iniciando aplicação principal...")
            app = AppPrincipal(
                funcionario_id=funcionario_id,
                funcionario_nome=funcionario_nome
            )
            app.mainloop()
            
            print(f"[OK] Logout realizado. Retornando ao login...")
            print()
        else:
            # Usuário fechou login sem autenticar
            print("[SISTEMA] Janela fechada sem autenticação.")
            break
    
    print("[SISTEMA] Aplicação finalizada.")
    print("=" * 70)


if __name__ == "__main__":
    main()