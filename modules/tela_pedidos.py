"""
Tela de Pedidos com tabela, filtros e detalhes.

Funcionalidades:
- Exibir pedidos em tabela com status visual
- Filtrar por cliente, data e status
- Ver detalhes e itens do pedido
- Expandir/colapsar linhas
"""

import customtkinter as ctk
from core.database_basico import DatabaseManager
from datetime import datetime
from typing import Optional, Dict, List
from tkinter import ttk


class TelaPedidos:
    """Classe para exibir pedidos em tabela."""
    
    def __init__(self, parent: ctk.CTkFrame, db: DatabaseManager):
        """
        Inicializa a tela de pedidos.
        
        Args:
            parent: Frame pai
            db: Gerenciador de banco de dados
        """
        self.parent = parent
        self.db = db
        self.pedidos_filtrados = []
        self.pedidos_expandidos = set()
        
        self._criar_interface()
    
    def _criar_interface(self):
        """Cria a interface de pedidos."""
        # Header
        header_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)
        
        label = ctk.CTkLabel(
            header_frame,
            text="📋 PEDIDOS",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        label.pack(side="left", anchor="w")
        
        # Filtros
        filtro_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        filtro_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Filtro por cliente
        ctk.CTkLabel(filtro_frame, text="Cliente:", font=ctk.CTkFont(size=10)).pack(side="left", padx=5)
        clientes = self.db.get_clientes()
        opcoes_clientes = ["Todos"] + [c['nome'] for c in clientes]
        self.combo_cliente = ctk.CTkComboBox(filtro_frame, values=opcoes_clientes, state="readonly", width=150)
        self.combo_cliente.set("Todos")
        self.combo_cliente.pack(side="left", padx=5)
        self.combo_cliente.configure(command=lambda *args: self._atualizar_filtro())
        
        # Filtro por status
        ctk.CTkLabel(filtro_frame, text="Status:", font=ctk.CTkFont(size=10)).pack(side="left", padx=5)
        self.combo_status = ctk.CTkComboBox(
            filtro_frame,
            values=["Todos", "Concluído", "Pendente", "Cancelado"],
            state="readonly",
            width=150
        )
        self.combo_status.set("Todos")
        self.combo_status.pack(side="left", padx=5)
        self.combo_status.configure(command=lambda *args: self._atualizar_filtro())
        
        # Botão atualizar
        btn_atualizar = ctk.CTkButton(
            filtro_frame,
            text="🔄 Atualizar",
            command=self._carregar_pedidos,
            width=100,
            font=ctk.CTkFont(size=10)
        )
        btn_atualizar.pack(side="right", padx=5)
        
        # Frame para tabela
        tabela_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        tabela_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Criar Treeview
        self.tree = ttk.Treeview(
            tabela_frame,
            columns=("id", "cliente", "data", "valor", "status", "itens"),
            height=15,
            show="headings"
        )
        
        # Definir colunas
        self.tree.column("id", width=50, minwidth=50)
        self.tree.column("cliente", width=200, minwidth=150)
        self.tree.column("data", width=100, minwidth=100)
        self.tree.column("valor", width=100, minwidth=100)
        self.tree.column("status", width=100, minwidth=100)
        self.tree.column("itens", width=100, minwidth=100)
        
        # Definir headings
        self.tree.heading("id", text="ID", anchor="w")
        self.tree.heading("cliente", text="Cliente", anchor="w")
        self.tree.heading("data", text="Data", anchor="w")
        self.tree.heading("valor", text="Valor Total", anchor="w")
        self.tree.heading("status", text="Status", anchor="w")
        self.tree.heading("itens", text="Itens", anchor="w")
        
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'Treeview',
            background="#1a1a1a",
            foreground="white",
            fieldbackground="#1a1a1a",
            borderwidth=0
        )
        style.configure('Treeview.Heading', background="#2b2b2b", foreground="white")
        style.map('Treeview', background=[('selected', '#0066cc')])
        
        # Scrollbars
        vsb = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tabela_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tabela_frame.grid_rowconfigure(0, weight=1)
        tabela_frame.grid_columnconfigure(0, weight=1)
        
        # Bind para expandir/colapsar
        self.tree.bind("<Double-1>", self._toggle_expandir)
        
        # Carregar pedidos
        self._carregar_pedidos()
    
    def _carregar_pedidos(self):
        """Carrega os pedidos do banco de dados."""
        try:
            pedidos = self.db.get_pedidos()
            self.pedidos_filtrados = pedidos
            self._atualizar_tabela()
        except Exception as e:
            print(f"[ERRO] Carregando pedidos: {e}")
    
    def _atualizar_filtro(self):
        """Atualiza a tabela com base nos filtros selecionados."""
        try:
            pedidos = self.db.get_pedidos()
            cliente_selecionado = self.combo_cliente.get()
            status_selecionado = self.combo_status.get()
            
            pedidos_filtrados = []
            
            for pedido in pedidos:
                # Filtro de cliente
                if cliente_selecionado != "Todos":
                    cliente = self.db.get_cliente(pedido['id_cliente'])
                    if cliente and cliente['nome'] != cliente_selecionado:
                        continue
                
                # Filtro de status
                if status_selecionado != "Todos":
                    if pedido.get('status', 'Concluído') != status_selecionado:
                        continue
                
                pedidos_filtrados.append(pedido)
            
            self.pedidos_filtrados = pedidos_filtrados
            self._atualizar_tabela()
        
        except Exception as e:
            print(f"[ERRO] Filtrando pedidos: {e}")
    
    def _atualizar_tabela(self):
        """Atualiza a visualização da tabela."""
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Adicionar pedidos
        for pedido in self.pedidos_filtrados:
            cliente = self.db.get_cliente(pedido['id_cliente'])
            nome_cliente = cliente['nome'] if cliente else f"Cliente {pedido['id_cliente']}"
            
            data = pedido['data_pedido']
            if isinstance(data, str):
                try:
                    data_obj = datetime.fromisoformat(data)
                    data_formatada = data_obj.strftime("%d/%m/%Y")
                except:
                    data_formatada = str(data)[:10]
            else:
                data_formatada = str(data)
            
            valor = float(pedido['valor_total'] or 0)
            status = pedido.get('status', 'Concluído')
            
            # Cor do status
            cor_status = "green" if status == "Concluído" else "orange" if status == "Pendente" else "red"
            
            # Adicionar linha
            item_id = self.tree.insert(
                "",
                "end",
                values=(
                    pedido['id_pedido'],
                    nome_cliente,
                    data_formatada,
                    f"R$ {valor:.2f}",
                    status,
                    "Clique para ver"
                )
            )
            
            # Armazenar dados do pedido
            # self.tree.set(item_id, "#0", "▶" if item_id not in self.pedidos_expandidos else "▼")
            
            # Se está expandido, mostrar itens
            if item_id in self.pedidos_expandidos:
                self._mostrar_itens_pedido(item_id, pedido['id_pedido'])
    
    def _toggle_expandir(self, event):
        """Expande ou colapsa um pedido para mostrar itens."""
        item = self.tree.identify('item', event.x, event.y)
        if not item:
            return
        
        if item in self.pedidos_expandidos:
            # Colapsar
            self.pedidos_expandidos.discard(item)
            # Remover itens filhos
            for child in self.tree.get_children(item):
                self.tree.delete(child)
        else:
            # Expandir
            self.pedidos_expandidos.add(item)
            pedido_id = int(self.tree.item(item, 'values')[0])
            self._mostrar_itens_pedido(item, pedido_id)
    
    def _mostrar_itens_pedido(self, parent_id: str, pedido_id: int):
        """Mostra os itens de um pedido como subitens."""
        try:
            itens = self.db.get_itens_pedido(pedido_id)
            
            for item in itens:
                nome = item.get('nome_produto', 'Produto')
                qtd = item.get('quantidade', 0)
                preco = item.get('preco_unitario', 0)
                subtotal = qtd * float(preco)
                
                self.tree.insert(
                    parent_id,
                    "end",
                    values=(
                        "",
                        f"  {nome}",
                        "",
                        "",
                        f"{qtd} un.",
                        f"R$ {subtotal:.2f}"
                    )
                )
        
        except Exception as e:
            print(f"[ERRO] Mostrando itens: {e}")
