"""
PDV - Ponto de Venda para MotoPeças.

Módulo de vendas com carrinho de compras, cálculo de total e integração com banco de dados.
"""

import customtkinter as ctk  # type: ignore
from tkinter import messagebox, ttk
from core.database_basico import DatabaseManager
from datetime import datetime


class PontoDeVenda(ctk.CTkToplevel):
    """Janela de Ponto de Venda para realizar vendas."""
    
    def __init__(self, parent, funcionario_id, funcionario_nome):
        super().__init__(parent)
        self.title("MotoPeças - Ponto de Venda")
        self.geometry("1000x700")
        self.funcionario_id = funcionario_id
        self.funcionario_nome = funcionario_nome
        self.db = DatabaseManager()
        self.carrinho = []  # Lista de itens no carrinho
        
        self._criar_interface()
        self._carregar_produtos()
        self._carregar_clientes()
    
    def _criar_interface(self):
        """Cria a interface do PDV."""
        
        # ========== SEÇÃO ESQUERDA: PRODUTOS ==========
        esquerda_frame = ctk.CTkFrame(self)
        esquerda_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo = ctk.CTkLabel(
            esquerda_frame,
            text="📦 PRODUTOS",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        titulo.pack(pady=10)
        
        # Filtro de categoria
        filtro_frame = ctk.CTkFrame(esquerda_frame)
        filtro_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(filtro_frame, text="Categoria:").pack(side="left", padx=5)
        self.combo_categoria = ctk.CTkComboBox(
            filtro_frame,
            values=["Todas"],
            state="readonly",
            command=self._filtrar_produtos
        )
        self.combo_categoria.pack(side="left", padx=5, fill="x", expand=True)
        self.combo_categoria.set("Todas")
        
        # Lista de produtos
        self.lista_produtos = ctk.CTkScrollableFrame(esquerda_frame)
        self.lista_produtos.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ========== SEÇÃO DIREITA: CARRINHO ==========
        direita_frame = ctk.CTkFrame(self)
        direita_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo_carrinho = ctk.CTkLabel(
            direita_frame,
            text="🛒 CARRINHO DE COMPRAS",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        titulo_carrinho.pack(pady=10)
        
        # Cliente
        cliente_frame = ctk.CTkFrame(direita_frame)
        cliente_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(cliente_frame, text="Cliente:").pack(side="left", padx=5)
        self.combo_cliente = ctk.CTkComboBox(
            cliente_frame,
            values=[],
            state="readonly"
        )
        self.combo_cliente.pack(side="left", padx=5, fill="x", expand=True)
        
        # Carrinho (Treeview)
        self.tree_carrinho = ttk.Treeview(
            direita_frame,
            columns=("Produto", "Quantidade", "Preço", "Subtotal"),
            height=12
        )
        
        self.tree_carrinho.column("#0", width=0, stretch=False)
        self.tree_carrinho.column("Produto", anchor="w", width=200)
        self.tree_carrinho.column("Quantidade", anchor="center", width=80)
        self.tree_carrinho.column("Preço", anchor="e", width=80)
        self.tree_carrinho.column("Subtotal", anchor="e", width=80)
        
        self.tree_carrinho.heading("#0", text="", anchor="w")
        self.tree_carrinho.heading("Produto", text="Produto", anchor="w")
        self.tree_carrinho.heading("Quantidade", text="Qtd", anchor="center")
        self.tree_carrinho.heading("Preço", text="Preço", anchor="e")
        self.tree_carrinho.heading("Subtotal", text="Subtotal", anchor="e")
        
        self.tree_carrinho.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Botão remover item
        btn_remover = ctk.CTkButton(
            direita_frame,
            text="❌ Remover Item",
            fg_color="#d32f2f",
            command=self._remover_item_carrinho
        )
        btn_remover.pack(fill="x", padx=5, pady=5)
        
        # Total
        total_frame = ctk.CTkFrame(direita_frame)
        total_frame.pack(fill="x", padx=5, pady=10)
        
        ctk.CTkLabel(
            total_frame,
            text="Total:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=5)
        
        self.label_total = ctk.CTkLabel(
            total_frame,
            text="R$ 0.00",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00AA00"
        )
        self.label_total.pack(side="left", padx=5)
        
        # Botões de ação
        botoes_frame = ctk.CTkFrame(direita_frame)
        botoes_frame.pack(fill="x", padx=5, pady=10)
        
        btn_finalizar = ctk.CTkButton(
            botoes_frame,
            text="✅ Finalizar Venda",
            fg_color="#00AA00",
            hover_color="#008800",
            command=self._finalizar_venda
        )
        btn_finalizar.pack(fill="x", pady=5)
        
        btn_cancelar = ctk.CTkButton(
            botoes_frame,
            text="❌ Cancelar",
            fg_color="#666666",
            command=self.destroy
        )
        btn_cancelar.pack(fill="x")
    
    def _carregar_produtos(self):
        """Carrega produtos da base de dados."""
        try:
            # Carregar categorias
            categorias = self.db.get_categorias()
            cat_names = ["Todas"] + [f"[{c['id_categoria']}] {c['nome']}" for c in categorias]
            self.combo_categoria.configure(values=cat_names)
            
            # Carregar e exibir todos os produtos
            produtos = self.db.get_produtos()
            self._exibir_produtos(produtos)
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar produtos: {e}")
    
    def _exibir_produtos(self, produtos):
        """Exibe produtos como botões no frame."""
        # Limpar frame
        for widget in self.lista_produtos.winfo_children():
            widget.destroy()
        
        if not produtos:
            ctk.CTkLabel(
                self.lista_produtos,
                text="Nenhum produto encontrado",
                text_color="gray"
            ).pack(pady=20)
            return
        
        for prod in produtos:
            # Frame para cada produto
            prod_frame = ctk.CTkFrame(
                self.lista_produtos,
                fg_color="#2a2a2a",
                corner_radius=5
            )
            prod_frame.pack(fill="x", pady=5)
            
            # Info do produto
            info_text = f"{prod['nome']} | R$ {prod['preco_venda']:.2f}"
            ctk.CTkLabel(
                prod_frame,
                text=info_text,
                font=ctk.CTkFont(size=11)
            ).pack(anchor="w", padx=10, pady=5)
            
            # Controle de quantidade
            controle_frame = ctk.CTkFrame(prod_frame, fg_color="transparent")
            controle_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(controle_frame, text="Qtd:").pack(side="left", padx=5)
            
            spinbox = ctk.CTkEntry(
                controle_frame,
                width=50,
                placeholder_text="1"
            )
            spinbox.pack(side="left", padx=5)
            spinbox.insert(0, "1")
            
            btn_adicionar = ctk.CTkButton(
                controle_frame,
                text="➕ Adicionar",
                width=100,
                command=lambda p=prod, s=spinbox: self._adicionar_carrinho(p, s)
            )
            btn_adicionar.pack(side="left", padx=5)
    
    def _carregar_clientes(self):
        """Carrega clientes da base de dados."""
        try:
            clientes = self.db.get_clientes()
            opcoes = [f"[{c['id_cliente']}] {c['nome']}" for c in clientes]
            self.combo_cliente.configure(values=opcoes)
            if opcoes:
                self.combo_cliente.set(opcoes[0])
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar clientes: {e}")
    
    def _filtrar_produtos(self):
        """Filtra produtos por categoria."""
        try:
            # Obter categoria selecionada do combobox
            categoria_selecionada = self.combo_categoria.get()
            
            if categoria_selecionada == "Todas":
                produtos = self.db.get_produtos()
            else:
                # Extrair ID da categoria
                cat_id = int(categoria_selecionada.split("[")[1].split("]")[0])
                produtos = self.db.get_produtos(categoria_id=cat_id)
            
            self._exibir_produtos(produtos)
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao filtrar: {e}")
    
    def _adicionar_carrinho(self, produto, spinbox):
        """Adiciona produto ao carrinho."""
        try:
            quantidade = int(spinbox.get())
            
            if quantidade <= 0:
                messagebox.showwarning("Aviso", "Quantidade deve ser maior que 0")
                return
            
            if quantidade > produto['estoque_atual']:
                messagebox.showwarning("Aviso", f"Estoque insuficiente! Disponível: {produto['estoque_atual']}")
                return
            
            # Verificar se produto já está no carrinho
            item_existente = None
            for item in self.carrinho:
                if item['id_produto'] == produto['id_produto']:
                    item_existente = item
                    break
            
            if item_existente:
                # Atualizar quantidade
                nova_qtd = item_existente['quantidade'] + quantidade
                if nova_qtd > produto['estoque_atual']:
                    messagebox.showwarning("Aviso", f"Estoque insuficiente! Disponível: {produto['estoque_atual']}")
                    return
                item_existente['quantidade'] = nova_qtd
            else:
                # Adicionar novo item
                self.carrinho.append({
                    'id_produto': produto['id_produto'],
                    'nome': produto['nome'],
                    'preco': produto['preco_venda'],
                    'quantidade': quantidade,
                    'subtotal': float(produto['preco_venda']) * quantidade
                })
            
            self._atualizar_carrinho_ui()
            spinbox.delete(0, "end")
            spinbox.insert(0, "1")
        
        except ValueError:
            messagebox.showerror("Erro", "Digite uma quantidade válida")
    
    def _atualizar_carrinho_ui(self):
        """Atualiza visualização do carrinho."""
        # Limpar Treeview
        for item in self.tree_carrinho.get_children():
            self.tree_carrinho.delete(item)
        
        # Adicionar itens
        total = 0
        for item in self.carrinho:
            self.tree_carrinho.insert(
                "",
                "end",
                values=(
                    item['nome'],
                    f"{item['quantidade']}",
                    f"R$ {item['preco']:.2f}",
                    f"R$ {item['subtotal']:.2f}"
                )
            )
            total += float(item['subtotal'])
        
        # Atualizar total
        self.label_total.configure(text=f"R$ {total:.2f}")
    
    def _remover_item_carrinho(self):
        """Remove item selecionado do carrinho."""
        selecionado = self.tree_carrinho.selection()
        
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um item para remover")
            return
        
        indice = self.tree_carrinho.index(selecionado[0])
        self.carrinho.pop(indice)
        self._atualizar_carrinho_ui()
    
    def _finalizar_venda(self):
        """Finaliza a venda e salva no banco de dados."""
        if not self.carrinho:
            messagebox.showwarning("Aviso", "Carrinho vazio!")
            return
        
        try:
            # Obter cliente
            cliente_sel = self.combo_cliente.get()
            if not cliente_sel:
                messagebox.showwarning("Aviso", "Selecione um cliente")
                return
            
            cliente_id = int(cliente_sel.split("[")[1].split("]")[0])
            
            # Calcular total
            total = sum(float(item['subtotal']) for item in self.carrinho)
            
            # Criar pedido
            pedido_id = self.db.criar_pedido(cliente_id, total, status="concluído")
            
            if not pedido_id:
                messagebox.showerror("Erro", "Falha ao criar pedido")
                return
            
            # Adicionar itens ao pedido
            for item in self.carrinho:
                self.db.adicionar_item_pedido(
                    pedido_id,
                    item['id_produto'],
                    item['quantidade'],
                    item['preco']
                )
                # Atualizar estoque após adicionar item
                self.db.atualizar_estoque(item['id_produto'], item['quantidade'])
            
            # Mensagem de sucesso
            messagebox.showinfo(
                "✓ VENDA CONCLUÍDA",
                f"Pedido #{pedido_id} finalizado com sucesso!\n\n"
                f"Cliente: {cliente_sel}\n"
                f"Total: R$ {total:.2f}"
            )
            
            # Limpar carrinho
            self.carrinho = []
            self._atualizar_carrinho_ui()
            
            # Fechar a janela automaticamente após 2 segundos
            self.after(2000, self.destroy)
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao finalizar venda: {e}")
