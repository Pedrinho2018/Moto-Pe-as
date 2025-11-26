"""
MotoPeças - Aplicação Completa.

Esta é a aplicação principal do sistema.
Contém toda a interface gráfica com múltiplas abas (Dashboard, PDV, Produtos, Clientes, Pedidos).

Funcionalidades principais:
- Menu lateral (sidebar) para navegar entre telas
- Dashboard com gráficos e KPIs
- Sistema de vendas (PDV) integrado
- CRUD de Produtos
- CRUD de Clientes
- Visualização de Pedidos
- Sistema de logout

A aplicação usa CustomTkinter para interface moderna e MySQL para persistência de dados.
"""

import customtkinter as ctk  # type: ignore
from core.login import LoginWindow
from core.database_basico import DatabaseManager
from modules.pdv_melhorado import PontoDeVendaMelhorado
from modules.dashboard import Dashboard
from modules.crud_produtos import CRUDProdutos
from modules.crud_clientes import CRUDClientes
from modules.tela_pedidos import TelaPedidos
from tkinter import messagebox
from datetime import datetime


# Configurar aparência da aplicação
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class AppCompleto(ctk.CTk):
    """
    Aplicação completa com múltiplas telas e funcionalidades.
    
    Esta classe herda de CTk (CustomTkinter) que é basicamente uma Tk com tema moderno.
    Gerencia todo o fluxo da aplicação e a navegação entre telas.
    """
    
    def __init__(self, funcionario_id=None, funcionario_nome=None):
        """
        Inicializa a aplicação principal.
        
        Args:
            funcionario_id: ID do funcionário logado
            funcionario_nome: Nome do funcionário para exibir
        """
        super().__init__()
        
        # Guardar dados do funcionário que fez login
        # Esses dados serão usados em várias telas para identificar quem está usando
        self.funcionario_id = funcionario_id
        self.funcionario_nome = funcionario_nome
        
        # Inicializar banco de dados
        # DatabaseManager é responsável por toda comunicação com MySQL
        self.db = DatabaseManager()
        
        # Configurar a janela principal
        titulo = "MotoPeças — Sistema Completo"
        if funcionario_nome:
            titulo += f" | {funcionario_nome}"  # Mostrar usuário no título
        
        self.title(titulo)
        self.geometry("1200x700")  # Tamanho padrão
        self.minsize(1000, 600)     # Tamanho mínimo para não ficar muito pequena
        
        # Configurar layout: Grid com 2 colunas
        # Coluna 0: Sidebar (menu) com tamanho fixo
        # Coluna 1: Conteúdo principal que expande
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(0, minsize=200)
        
        # Criar os componentes da interface
        self._criar_sidebar()      # Menu lateral esquerdo
        self._criar_main_area()    # Área de conteúdo direito
        
        # Mostrar dashboard por padrão quando app inicia
        self.show_frame("dashboard")
    
    def _criar_sidebar(self):
        """
        Cria a barra lateral (sidebar) com o menu de navegação.
        
        O sidebar possui:
        - Título "MOTOPEÇAS"
        - Botões de navegação para cada tela
        - Botão de logout
        - Informações do usuário logado
        """
        # Frame que será o sidebar (preto, dimensionado em 200px de largura)
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#1a1a1a")
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)  # Não deixar sidebar crescer
        
        # Título no topo do sidebar
        title_label = ctk.CTkLabel(
            sidebar,
            text="MOTOPEÇAS",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1f6aa5"  # Azul característico
        )
        title_label.pack(pady=20, padx=10)
        
        # === BOTÕES DE NAVEGAÇÃO ===
        # Cada botão chama show_frame() para mudar de tela
        
        self.btn_dashboard = ctk.CTkButton(
            sidebar,
            text="📊 Dashboard",
            command=lambda: self.show_frame("dashboard"),
            fg_color="transparent"
        )
        self.btn_dashboard.pack(pady=8, padx=16, fill="x")
        
        # Botão para abrir PDV (Ponto de Venda)
        # Abre em janela separada, não muda de tela
        self.btn_vendas = ctk.CTkButton(
            sidebar,
            text="🛒 Vendas (PDV)",
            command=self._abrir_pdv,
            fg_color="transparent"
        )
        self.btn_vendas.pack(pady=8, padx=16, fill="x")
        
        self.btn_produtos = ctk.CTkButton(
            sidebar,
            text="📦 Produtos",
            command=lambda: self.show_frame("produtos"),
            fg_color="transparent"
        )
        self.btn_produtos.pack(pady=8, padx=16, fill="x")
        
        self.btn_clientes = ctk.CTkButton(
            sidebar,
            text="👥 Clientes",
            command=lambda: self.show_frame("clientes"),
            fg_color="transparent"
        )
        self.btn_clientes.pack(pady=8, padx=16, fill="x")
        
        self.btn_pedidos = ctk.CTkButton(
            sidebar,
            text="📋 Pedidos",
            command=lambda: self.show_frame("pedidos"),
            fg_color="transparent"
        )
        self.btn_pedidos.pack(pady=8, padx=16, fill="x")
        
        # Botão SAIR no final (vermelho para destacar)
        self.btn_sair = ctk.CTkButton(
            sidebar,
            text="🚪 Sair",
            fg_color="#d32f2f",      # Vermelho
            hover_color="#b71c1c",   # Vermelho mais escuro ao passar mouse
            command=self.fazer_logout
        )
        self.btn_sair.pack(pady=8, padx=16, fill="x", side="bottom")
        
        # Mostrar qual usuário está logado no final do sidebar
        user_label = ctk.CTkLabel(
            sidebar,
            text=f"Logado:\n{self.funcionario_nome}",
            font=ctk.CTkFont(size=9),
            text_color="#999999"  # Cinza para não chamar muita atenção
        )
        user_label.pack(pady=10, padx=10, side="bottom")
    
    def _abrir_pdv(self):
        """
        Abre a janela de Ponto de Venda (PDV).
        
        O PDV é uma janela separada (CTkToplevel), não uma aba como as outras.
        Isso permite que funcione independentemente sem mudar a tela atual.
        """
        PontoDeVendaMelhorado(self, self.funcionario_id, self.funcionario_nome)
    
    def _criar_main_area(self):
        """
        Cria a área principal onde as telas (Dashboard, Produtos, etc) são exibidas.
        
        Funciona como um "container" que mostra diferentes telas dependendo de qual
        foi selecionada no menu. Usa dicionário self.frames para armazenar todas.
        """
        # Frame que conterá todas as telas
        main_frame = ctk.CTkFrame(self, corner_radius=0)
        main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Dicionário para guardar referências de todas as telas
        # Isso permite trocar de tela sem precisar recriar tudo
        self.frames = {}
        
        # ========== DASHBOARD ==========
        # Primeira tela: Gráficos e estatísticas
        dashboard_frame = ctk.CTkFrame(main_frame)
        self.frames["dashboard"] = dashboard_frame
        dashboard_frame.grid(row=0, column=0, sticky="nsew")
        
        # Passar o frame para a classe Dashboard criar seus componentes

        Dashboard(dashboard_frame, self.db, self.funcionario_id)
        
        # ========== PRODUTOS ==========
        produtos_frame = ctk.CTkFrame(main_frame)
        self.frames["produtos"] = produtos_frame
        produtos_frame.grid(row=0, column=0, sticky="nsew")
        
        # Usar CRUD de Produtos
        CRUDProdutos(produtos_frame, self.db)
        
        # ========== CLIENTES ==========
        clientes_frame = ctk.CTkFrame(main_frame)
        self.frames["clientes"] = clientes_frame
        clientes_frame.grid(row=0, column=0, sticky="nsew")
        
        # Usar CRUD de Clientes
        CRUDClientes(clientes_frame, self.db)
        
        # ========== PEDIDOS ==========
        pedidos_frame = ctk.CTkFrame(main_frame)
        self.frames["pedidos"] = pedidos_frame
        pedidos_frame.grid(row=0, column=0, sticky="nsew")
        
        # Usar Tela de Pedidos
        TelaPedidos(pedidos_frame, self.db)
    
    def _criar_tela_produtos(self, parent):
        """Cria tela de produtos com cards em grid."""
        # Header
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)
        
        label = ctk.CTkLabel(
            header_frame,
            text="📦 PRODUTOS",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        label.pack(side="left", anchor="w")
        
        try:
            produtos = self.db.get_produtos()
            
            # Frame scrollável com grid
            scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
            scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            if produtos:
                # Configurar grid para 4 colunas
                for i in range(4):
                    scroll_frame.grid_columnconfigure(i, weight=1)
                
                for idx, prod in enumerate(produtos):
                    row = idx // 4
                    col = idx % 4
                    
                    # Card do produto
                    card = ctk.CTkFrame(
                        scroll_frame,
                        fg_color="#2b2b2b",
                        border_color="#444444",
                        border_width=2,
                        corner_radius=10
                    )
                    card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                    card.grid_propagate(False)
                    card.configure(width=200, height=280)
                    
                    # Nome do produto
                    nome_label = ctk.CTkLabel(
                        card,
                        text=prod['nome'],
                        font=ctk.CTkFont(size=12, weight="bold"),
                        wraplength=180,
                        justify="center"
                    )
                    nome_label.pack(pady=(10, 5), padx=10)
                    
                    # SKU
                    sku_label = ctk.CTkLabel(
                        card,
                        text=f"SKU: {prod['sku']}",
                        font=ctk.CTkFont(size=9),
                        text_color="#888888"
                    )
                    sku_label.pack(pady=2, padx=10)
                    
                    # Divisor
                    divisor = ctk.CTkFrame(card, fg_color="#444444", height=1)
                    divisor.pack(fill="x", padx=10, pady=8)
                    
                    # Preço em destaque
                    preco_label = ctk.CTkLabel(
                        card,
                        text=f"R$ {prod['preco_venda']:.2f}",
                        font=ctk.CTkFont(size=16, weight="bold"),
                        text_color="#00cc00"
                    )
                    preco_label.pack(pady=5)
                    
                    # Estoque
                    estoque = prod['estoque_atual']
                    cor_estoque = "#00cc00" if estoque > 10 else "#ffaa00" if estoque > 0 else "#cc0000"
                    
                    estoque_label = ctk.CTkLabel(
                        card,
                        text=f"📦 Estoque: {estoque}",
                        font=ctk.CTkFont(size=11),
                        text_color=cor_estoque
                    )
                    estoque_label.pack(pady=5)
                    
                    # Estoque mínimo
                    min_label = ctk.CTkLabel(
                        card,
                        text=f"Mín: {prod['estoque_minimo']}",
                        font=ctk.CTkFont(size=9),
                        text_color="#888888"
                    )
                    min_label.pack(pady=2)
                    
                    # Custo (informação interna)
                    custo_label = ctk.CTkLabel(
                        card,
                        text=f"Custo: R$ {prod['preco_custo']:.2f}",
                        font=ctk.CTkFont(size=9),
                        text_color="#666666"
                    )
                    custo_label.pack(pady=(8, 5))
                    
                    # ID do produto (pequeno)
                    id_label = ctk.CTkLabel(
                        card,
                        text=f"ID: {prod['id_produto']}",
                        font=ctk.CTkFont(size=8),
                        text_color="#444444"
                    )
                    id_label.pack(pady=(0, 8))
            else:
                ctk.CTkLabel(
                    scroll_frame,
                    text="Nenhum produto cadastrado",
                    font=ctk.CTkFont(size=14)
                ).pack(pady=50)
        
        except Exception as e:
            ctk.CTkLabel(
                parent,
                text=f"Erro ao carregar produtos: {e}",
                text_color="red",
                font=ctk.CTkFont(size=12)
            ).pack(pady=20)

    
    def show_frame(self, name: str):
        """Mostra um frame específico."""
        frame = self.frames.get(name)
        if frame:
            frame.tkraise()
            
            # Atualizar estilo dos botões
            buttons = {
                "dashboard": self.btn_dashboard,
                "produtos": self.btn_produtos,
                "clientes": self.btn_clientes,
                "pedidos": self.btn_pedidos,
            }
            
            for key, btn in buttons.items():
                if key == name:
                    btn.configure(fg_color=("#3B8ED0", "#1f6aa5"))
                else:
                    btn.configure(fg_color="transparent")
    
    def fazer_logout(self):
        """Faz logout e volta para tela de login."""
        self.destroy()


if __name__ == "__main__":
    # Mostrar tela de login
    login_window = LoginWindow()
    login_window.mainloop()
    
    # Se fez login com sucesso
    if login_window.funcionario_id is not None:
        app = AppCompleto(
            funcionario_id=login_window.funcionario_id,
            funcionario_nome=login_window.obter_usuario_nome()
        )
        app.mainloop()
    else:
        print("Login cancelado.")
