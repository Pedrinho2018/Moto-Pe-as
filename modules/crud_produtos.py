"""
CRUD de Produtos para MotoPeças.

Funcionalidades:
- Criar novo produto
- Editar produto existente
- Deletar produto
- Gerenciar estoque
"""

import customtkinter as ctk
from core.database_basico import DatabaseManager
from typing import Optional, Callable


class CRUDProdutos:
    """Classe para gerenciar CRUD de produtos."""
    
    def __init__(self, parent: ctk.CTkFrame, db: DatabaseManager, callback: Optional[Callable] = None):
        """
        Inicializa o CRUD de produtos.
        
        Args:
            parent: Frame pai
            db: Gerenciador de banco de dados
            callback: Função para atualizar a lista após mudanças
        """
        self.parent = parent
        self.db = db
        self.callback = callback
        
        self._criar_interface()
    
    def _criar_interface(self):
        """Cria a interface de gerenciamento de produtos."""
        # Header com botão de novo
        header_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)
        
        label = ctk.CTkLabel(
            header_frame,
            text="📦 PRODUTOS",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        label.pack(side="left", anchor="w")
        
        btn_novo = ctk.CTkButton(
            header_frame,
            text="➕ Novo Produto",
            command=self._abrir_form_novo,
            fg_color="#2d8c2d",
            hover_color="#1a5c1a",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        btn_novo.pack(side="right", padx=10)
        
        # Scroll frame com produtos
        scroll_frame = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        try:
            produtos = self.db.get_produtos()
            
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
                    card.configure(width=200, height=320)
                    
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
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color="#00cc00"
                    )
                    preco_label.pack(pady=5)
                    
                    # Estoque
                    estoque = prod['estoque_atual']
                    cor_estoque = "#00cc00" if estoque > 10 else "#ffaa00" if estoque > 0 else "#cc0000"
                    
                    estoque_label = ctk.CTkLabel(
                        card,
                        text=f"📦 {estoque} un.",
                        font=ctk.CTkFont(size=11),
                        text_color=cor_estoque
                    )
                    estoque_label.pack(pady=3)
                    
                    # Estoque mínimo
                    min_label = ctk.CTkLabel(
                        card,
                        text=f"Mín: {prod['estoque_minimo']}",
                        font=ctk.CTkFont(size=9),
                        text_color="#888888"
                    )
                    min_label.pack(pady=2)
                    
                    # Divisor
                    divisor2 = ctk.CTkFrame(card, fg_color="#444444", height=1)
                    divisor2.pack(fill="x", padx=10, pady=8)
                    
                    # Botões de ação
                    btn_frame = ctk.CTkFrame(card, fg_color="transparent")
                    btn_frame.pack(fill="x", padx=8, pady=5)
                    
                    btn_editar = ctk.CTkButton(
                        btn_frame,
                        text="✏️ Editar",
                        font=ctk.CTkFont(size=10),
                        fg_color="#0066cc",
                        hover_color="#004499",
                        command=lambda p=prod: self._abrir_form_editar(p)
                    )
                    btn_editar.pack(side="left", padx=2, fill="x", expand=True)
                    
                    btn_deletar = ctk.CTkButton(
                        btn_frame,
                        text="🗑️ Deletar",
                        font=ctk.CTkFont(size=10),
                        fg_color="#cc0000",
                        hover_color="#990000",
                        command=lambda p=prod: self._confirmar_deletar(p)
                    )
                    btn_deletar.pack(side="left", padx=2, fill="x", expand=True)
            else:
                ctk.CTkLabel(
                    scroll_frame,
                    text="Nenhum produto cadastrado",
                    font=ctk.CTkFont(size=14)
                ).pack(pady=50)
        
        except Exception as e:
            ctk.CTkLabel(
                self.parent,
                text=f"Erro ao carregar produtos: {e}",
                text_color="red",
                font=ctk.CTkFont(size=12)
            ).pack(pady=20)
    
    def _abrir_form_novo(self):
        """Abre formulário para criar novo produto."""
        FormProduto(self.parent, self.db, None, self._atualizar)
    
    def _abrir_form_editar(self, produto: dict):
        """Abre formulário para editar produto."""
        FormProduto(self.parent, self.db, produto, self._atualizar)
    
    def _confirmar_deletar(self, produto: dict):
        """Confirma deleção de produto."""
        janela = ctk.CTkToplevel(self.parent)
        janela.title("Confirmar Deleção")
        janela.geometry("400x200")
        janela.grab_set()
        
        ctk.CTkLabel(
            janela,
            text=f"Deletar produto '{produto['nome']}'?",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=20)
        
        ctk.CTkLabel(
            janela,
            text="Esta ação não pode ser desfeita.",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        ).pack(pady=5)
        
        btn_frame = ctk.CTkFrame(janela, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        def deletar():
            if self.db.deletar_produto(produto['id_produto']):
                janela.destroy()
                self._atualizar()
            else:
                ctk.CTkLabel(
                    janela,
                    text="Erro ao deletar produto",
                    text_color="red"
                ).pack()
        
        ctk.CTkButton(
            btn_frame,
            text="❌ Deletar",
            command=deletar,
            fg_color="#cc0000",
            hover_color="#990000"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="✅ Cancelar",
            command=janela.destroy,
            fg_color="#666666",
            hover_color="#555555"
        ).pack(side="left", padx=10)
    
    def _atualizar(self):
        """Atualiza a interface após mudanças."""
        for widget in self.parent.winfo_children():
            widget.destroy()
        self._criar_interface()
        if self.callback:
            self.callback()


class FormProduto(ctk.CTkToplevel):
    """Janela de formulário para criar/editar produto."""
    
    def __init__(self, parent, db: DatabaseManager, produto: Optional[dict] = None, callback: Optional[Callable] = None):
        """
        Inicializa o formulário.
        
        Args:
            parent: Janela pai
            db: Gerenciador de banco de dados
            produto: Produto a editar (None para novo)
            callback: Função a executar após salvar
        """
        super().__init__(parent)
        self.db = db
        self.produto = produto
        self.callback = callback
        self.titulo = "Editar Produto" if produto else "Novo Produto"
        
        self.title(self.titulo)
        self.geometry("500x600")
        self.grab_set()
        
        self._criar_form()
    
    def _criar_form(self):
        """Cria o formulário."""
        # Header
        ctk.CTkLabel(
            self,
            text=self.titulo,
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=15)
        
        # Scroll frame
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # SKU
        ctk.CTkLabel(scroll, text="SKU:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
        self.entry_sku = ctk.CTkEntry(scroll, placeholder_text="Ex: MOT001")
        self.entry_sku.pack(fill="x", pady=(0, 15))
        
        # Nome
        ctk.CTkLabel(scroll, text="Nome do Produto:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
        self.entry_nome = ctk.CTkEntry(scroll, placeholder_text="Ex: Óleo Motor 10W30")
        self.entry_nome.pack(fill="x", pady=(0, 15))
        
        # Categoria
        ctk.CTkLabel(scroll, text="Categoria:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
        categorias = self.db.get_categorias()
        self.combo_categoria = ctk.CTkComboBox(
            scroll,
            values=[f"{c['id_categoria']} - {c['nome']}" for c in categorias],
            state="readonly"
        )
        self.combo_categoria.pack(fill="x", pady=(0, 15))
        
        # Preço de Custo
        ctk.CTkLabel(scroll, text="Preço de Custo (R$):", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
        self.entry_custo = ctk.CTkEntry(scroll, placeholder_text="0.00")
        self.entry_custo.pack(fill="x", pady=(0, 15))
        
        # Preço de Venda
        ctk.CTkLabel(scroll, text="Preço de Venda (R$):", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
        self.entry_venda = ctk.CTkEntry(scroll, placeholder_text="0.00")
        self.entry_venda.pack(fill="x", pady=(0, 15))
        
        # Estoque Atual
        ctk.CTkLabel(scroll, text="Estoque Atual (un):", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
        self.entry_estoque = ctk.CTkEntry(scroll, placeholder_text="0")
        self.entry_estoque.pack(fill="x", pady=(0, 15))
        
        # Estoque Mínimo
        ctk.CTkLabel(scroll, text="Estoque Mínimo (un):", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
        self.entry_minimo = ctk.CTkEntry(scroll, placeholder_text="10")
        self.entry_minimo.pack(fill="x", pady=(0, 15))
        
        # Preencher dados se editando
        if self.produto:
            self.entry_sku.insert(0, self.produto['sku'])
            self.entry_nome.insert(0, self.produto['nome'])
            self.entry_custo.insert(0, str(self.produto['preco_custo']))
            self.entry_venda.insert(0, str(self.produto['preco_venda']))
            self.entry_estoque.insert(0, str(self.produto['estoque_atual']))
            self.entry_minimo.insert(0, str(self.produto['estoque_minimo']))
        
        # Botões
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Salvar",
            command=self._salvar,
            fg_color="#2d8c2d",
            hover_color="#1a5c1a",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(
            btn_frame,
            text="❌ Cancelar",
            command=self.destroy,
            fg_color="#666666",
            hover_color="#555555"
        ).pack(side="left", padx=5, fill="x", expand=True)
    
    def _salvar(self):
        """Salva os dados do produto."""
        try:
            sku = self.entry_sku.get().strip()
            nome = self.entry_nome.get().strip()
            custo = float(self.entry_custo.get())
            venda = float(self.entry_venda.get())
            estoque = int(self.entry_estoque.get())
            minimo = int(self.entry_minimo.get())
            
            categoria_str = self.combo_categoria.get()
            categoria_id = int(categoria_str.split(" - ")[0])
            
            # Validar
            if not sku or not nome:
                print("SKU e Nome são obrigatórios")
                return
            
            if self.produto:
                # Atualizar
                if self.db.atualizar_produto(
                    self.produto['id_produto'], nome=nome, sku=sku,
                    preco_custo=custo, preco_venda=venda,
                    estoque_atual=estoque, estoque_minimo=minimo,
                    id_categoria=categoria_id
                ):
                    print(f"✓ Produto '{nome}' atualizado")
                    self.destroy()
                    if self.callback:
                        self.callback()
            else:
                # Criar
                produto_id = self.db.criar_produto(
                    nome, sku, custo, venda, estoque, minimo, categoria_id
                )
                if produto_id:
                    print(f"✓ Produto '{nome}' criado (ID: {produto_id})")
                    self.destroy()
                    if self.callback:
                        self.callback()
        
        except ValueError:
            print("Erro: Valores inválidos. Verifique preços e quantidades.")
        except Exception as e:
            print(f"Erro ao salvar: {e}")
