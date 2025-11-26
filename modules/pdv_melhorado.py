"""
PDV Melhorado - Ponto de Venda Versão Melhorada.

PDV = Ponto De Venda (a "caixa" onde são feitas as vendas)

Esta janela é onde o vendedor:
1. Busca produtos por nome ou categoria
2. Adiciona itens ao carrinho
3. Define quantidade e desconto
4. Seleciona cliente
5. Finaliza a venda

Funcionalidades principais:
- Busca rápida de produtos com filtro em tempo real
- Filtro por categoria
- Carrinho interativo (adiciona/remove itens)
- Cálculo automático de total com desconto
- Seleção de cliente para pedido
- Recibo de venda
- Auto-fechamento após venda com sucesso
- Atualização automática de estoque

Interface:
- ESQUERDA: Lista de produtos para selecionar
- DIREITA (SUPERIOR): Carrinho e cliente
- DIREITA (INFERIOR): Botões de ação e total

Este é um dos módulos mais críticos do sistema!
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from core.database_basico import DatabaseManager
from datetime import datetime


class PontoDeVendaMelhorado(ctk.CTkFrame):
    """
    Frame de Ponto de Venda com funcionalidades melhoradas.
    
    Herda de CTkFrame = Integrado na interface principal
    Isso permite que PDV seja exibido como uma aba normal
    
    Atributos:
    - self.carrinho: Lista de dicts com {id_produto, nome, quantidade, preco, subtotal}
    - self.cliente_selecionado: Dict com dados do cliente da venda
    - self.db: Conexão com banco de dados
    """
    
    def __init__(self, parent, funcionario_id, funcionario_nome):
        """
        Inicializa frame do PDV.
        
        Args:
            parent: Frame pai que conterá o PDV
            funcionario_id: ID do vendedor
            funcionario_nome: Nome do vendedor (para exibir e auditoria)
        """
        super().__init__(parent)
        self.pack(fill="both", expand=True)  # ← IMPORTANTE: preencher o espaço do pai
        self.title = None  # CTkFrame não tem title
        
        # Guardar dados do funcionário que está vendendo
        self.funcionario_id = funcionario_id
        self.funcionario_nome = funcionario_nome
        
        # Conectar ao banco para operações
        self.db = DatabaseManager()
        
        # Inicializar estruturas de dados
        self.carrinho = []                    # Lista de itens a vender
        self.desconto_percentual = 0          # Desconto aplicado (em %)
        self.cliente_selecionado = None       # Cliente do pedido
        
        # Criar a interface visual
        self._criar_interface()
        
        # Carregar dados do banco (produtos, clientes, categorias)
        self._carregar_dados()
    
    def _criar_interface(self):
        """
        Cria toda a interface visual do PDV.
        
        Layout em 2 partes:
        - ESQUERDA (40%): Lista de produtos com busca e filtro
        - DIREITA (60%): Carrinho, cliente, totais
        """
        # Frame principal que conterá tudo
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ========== ESQUERDA: LISTA DE PRODUTOS ==========
        esquerda = ctk.CTkFrame(main_frame)
        esquerda.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Título da seção
        ctk.CTkLabel(
            esquerda,
            text="📦 PRODUTOS",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        # Busca de produtos
        busca_frame = ctk.CTkFrame(esquerda)
        busca_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(busca_frame, text="Buscar:", font=ctk.CTkFont(size=10)).pack(side="left", padx=5)
        self.entry_busca = ctk.CTkEntry(busca_frame, placeholder_text="Nome ou SKU...")
        self.entry_busca.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_busca.bind("<KeyRelease>", lambda e: self._filtrar_produtos())
        
        # Categoria
        categoria_frame = ctk.CTkFrame(esquerda)
        categoria_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(categoria_frame, text="Categoria:", font=ctk.CTkFont(size=10)).pack(side="left", padx=5)
        self.combo_categoria = ctk.CTkComboBox(categoria_frame, state="readonly")
        self.combo_categoria.pack(side="left", fill="x", expand=True, padx=5)
        self.combo_categoria.configure(command=lambda *args: self._filtrar_produtos())
        
        # Lista de produtos com scrollbar
        lista_frame = ctk.CTkFrame(esquerda)
        lista_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = ctk.CTkScrollbar(lista_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.tree_produtos = ttk.Treeview(
            lista_frame,
            columns=("nome", "preco", "estoque", "qtd"),
            height=15,
            yscrollcommand=scrollbar.set
        )
        scrollbar.configure(command=self.tree_produtos.yview)
        
        self.tree_produtos.column("#0", width=30)
        self.tree_produtos.column("nome", width=200)
        self.tree_produtos.column("preco", width=80)
        self.tree_produtos.column("estoque", width=70)
        self.tree_produtos.column("qtd", width=60)
        
        self.tree_produtos.heading("#0", text="ID", anchor="w")
        self.tree_produtos.heading("nome", text="Nome", anchor="w")
        self.tree_produtos.heading("preco", text="Preço", anchor="w")
        self.tree_produtos.heading("estoque", text="Estoque", anchor="w")
        self.tree_produtos.heading("qtd", text="Qtd", anchor="w")
        
        # Estilo
        style = ttk.Style()
        style.configure('Treeview', background="#1a1a1a", foreground="white", fieldbackground="#1a1a1a")
        
        self.tree_produtos.pack(fill="both", expand=True)
        self.tree_produtos.bind("<Double-1>", self._adicionar_do_duplo_clique)
        
        # ========== DIREITA: CARRINHO E CLIENTE ==========
        direita = ctk.CTkFrame(main_frame)
        direita.pack(side="right", fill="both", expand=True)
        
        # ---- Seleção de Cliente ----
        cliente_frame = ctk.CTkFrame(direita)
        cliente_frame.pack(fill="x", padx=5, pady=10)
        
        ctk.CTkLabel(
            cliente_frame,
            text="👤 CLIENTE",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=5, pady=(5, 10))
        
        self.combo_cliente = ctk.CTkComboBox(cliente_frame, state="readonly")
        self.combo_cliente.pack(fill="x", padx=5, pady=5)
        self.combo_cliente.configure(command=lambda *args: self._selecionar_cliente())
        
        # ---- Carrinho ----
        carrinho_label = ctk.CTkLabel(
            direita,
            text="🛒 CARRINHO",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        carrinho_label.pack(anchor="w", padx=5, pady=(15, 10))
        
        # Treeview do carrinho
        cart_frame = ctk.CTkFrame(direita)
        cart_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        scrollbar_cart = ctk.CTkScrollbar(cart_frame)
        scrollbar_cart.pack(side="right", fill="y")
        
        self.tree_carrinho = ttk.Treeview(
            cart_frame,
            columns=("preco", "qtd", "subtotal"),
            height=10,
            yscrollcommand=scrollbar_cart.set
        )
        scrollbar_cart.configure(command=self.tree_carrinho.yview)
        
        self.tree_carrinho.column("#0", width=180)
        self.tree_carrinho.column("preco", width=80)
        self.tree_carrinho.column("qtd", width=60)
        self.tree_carrinho.column("subtotal", width=80)
        
        self.tree_carrinho.heading("#0", text="Produto", anchor="w")
        self.tree_carrinho.heading("preco", text="Preco", anchor="w")
        self.tree_carrinho.heading("qtd", text="Qtd", anchor="w")
        self.tree_carrinho.heading("subtotal", text="Subtotal", anchor="w")
        
        self.tree_carrinho.pack(fill="both", expand=True)
        
        # Binding para duplo clique - editar quantidade
        self.tree_carrinho.bind("<Double-1>", self._editar_quantidade_carrinho)
        
        # ---- Totalizadores ----
        total_frame = ctk.CTkFrame(direita, fg_color="#2b2b2b", corner_radius=10)
        total_frame.pack(fill="x", padx=5, pady=10)
        
        # Subtotal
        ctk.CTkLabel(
            total_frame,
            text="Subtotal:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 0))
        self.label_subtotal = ctk.CTkLabel(
            total_frame,
            text="R$ 0.00",
            font=ctk.CTkFont(size=11),
            text_color="#00cc00"
        )
        self.label_subtotal.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Desconto
        desc_frame = ctk.CTkFrame(total_frame, fg_color="transparent")
        desc_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(desc_frame, text="Desconto %:").pack(side="left")
        self.entry_desconto = ctk.CTkEntry(desc_frame, width=80)
        self.entry_desconto.pack(side="left", padx=5)
        self.entry_desconto.insert(0, "0")
        self.entry_desconto.bind("<KeyRelease>", lambda e: self._atualizar_total())
        
        # Total
        ctk.CTkLabel(
            total_frame,
            text="TOTAL:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 0))
        self.label_total = ctk.CTkLabel(
            total_frame,
            text="R$ 0.00",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00ff00"
        )
        self.label_total.pack(anchor="w", padx=10, pady=(0, 10))
        
        # ---- Botões de Ação ----
        botoes_frame = ctk.CTkFrame(direita)
        botoes_frame.pack(fill="x", padx=5, pady=10)
        
        btn_remover = ctk.CTkButton(
            botoes_frame,
            text="❌ Remover Item",
            command=self._remover_item,
            fg_color="#cc0000",
            hover_color="#990000"
        )
        btn_remover.pack(side="left", fill="x", expand=True, padx=5)
        
        btn_limpar = ctk.CTkButton(
            botoes_frame,
            text="🔄 Limpar",
            command=self._limpar_carrinho,
            fg_color="#666666",
            hover_color="#555555"
        )
        btn_limpar.pack(side="left", fill="x", expand=True, padx=5)
        
        btn_finalizar = ctk.CTkButton(
            botoes_frame,
            text="✅ FINALIZAR VENDA",
            command=self._finalizar_venda,
            fg_color="#2d8c2d",
            hover_color="#1a5c1a",
            font=ctk.CTkFont(weight="bold")
        )
        btn_finalizar.pack(fill="x", padx=5, pady=10)
    
    def _carregar_dados(self):
        """Carrega produtos e clientes."""
        try:
            # Categorias
            categorias = self.db.get_categorias()
            opcoes_cat = ["Todas"] + [c['nome'] for c in categorias]
            self.combo_categoria.configure(values=opcoes_cat)
            self.combo_categoria.set("Todas")
            
            # Clientes
            clientes = self.db.get_clientes()
            opcoes_cli = ["Selecione um cliente"] + [c['nome'] for c in clientes]
            self.combo_cliente.configure(values=opcoes_cli)
            self.combo_cliente.set("Selecione um cliente")
            
            # Produtos
            self._filtrar_produtos()
        except Exception as e:
            print(f"[ERRO] Carregando dados: {e}")
    
    def _filtrar_produtos(self):
        """Filtra produtos por busca e categoria."""
        try:
            # Limpar tabela
            for item in self.tree_produtos.get_children():
                self.tree_produtos.delete(item)
            
            produtos = self.db.get_produtos()
            
            # Filtrar por categoria
            categoria_selecionada = self.combo_categoria.get()
            if categoria_selecionada != "Todas":
                categorias = self.db.get_categorias()
                cat_id = next((c['id_categoria'] for c in categorias if c['nome'] == categoria_selecionada), None)
                produtos = [p for p in produtos if p['id_categoria'] == cat_id]
            
            # Filtrar por busca
            busca = self.entry_busca.get().lower()
            if busca:
                produtos = [p for p in produtos if busca in p['nome'].lower() or busca in p['sku'].lower()]
            
            # Adicionar à tabela
            for prod in produtos:
                self.tree_produtos.insert(
                    "",
                    "end",
                    text=prod['id_produto'],
                    values=(
                        prod['nome'],
                        f"R$ {prod['preco_venda']:.2f}",
                        f"{prod['estoque_atual']}",
                        ""
                    )
                )
        
        except Exception as e:
            print(f"[ERRO] Filtrando produtos: {e}")
    
    def _adicionar_do_duplo_clique(self, event):
        """Abre diálogo para selecionar quantidade ao duplo clique."""
        item = self.tree_produtos.selection()
        if not item:
            return
        
        item_id = self.tree_produtos.item(item[0], 'text')
        try:
            produto = self.db.get_produto(int(item_id))
            if not produto or produto['estoque_atual'] <= 0:
                messagebox.showerror("Erro", "Produto sem estoque!")
                return
            
            # Criar janela modal para escolher quantidade
            qtd_window = ctk.CTkToplevel(self)
            qtd_window.title("Adicionar ao Carrinho")
            qtd_window.geometry("350x180")
            qtd_window.resizable(False, False)
            
            # Tornar modal
            qtd_window.transient(self)
            qtd_window.grab_set()
            
            # Label do produto
            ctk.CTkLabel(
                qtd_window,
                text=f"Produto: {produto['nome']}",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(pady=15)
            
            # Label de estoque
            ctk.CTkLabel(
                qtd_window,
                text=f"Estoque disponível: {produto['estoque_atual']} un.",
                font=ctk.CTkFont(size=10),
                text_color="#aaaaaa"
            ).pack(pady=5)
            
            # Frame para entrada
            entrada_frame = ctk.CTkFrame(qtd_window, fg_color="transparent")
            entrada_frame.pack(pady=10)
            
            ctk.CTkLabel(
                entrada_frame,
                text="Quantidade:"
            ).pack(side="left", padx=5)
            
            entrada = ctk.CTkEntry(
                entrada_frame,
                width=80,
                placeholder_text="1"
            )
            entrada.pack(side="left", padx=5)
            entrada.insert(0, "1")
            entrada.select_range(0, 1)
            entrada.focus()
            
            # Frame para botões
            botoes_frame = ctk.CTkFrame(qtd_window, fg_color="transparent")
            botoes_frame.pack(pady=15)
            
            def adicionar():
                try:
                    qtd = int(entrada.get())
                    if qtd <= 0:
                        messagebox.showerror("Erro", "Quantidade deve ser maior que 0!")
                        return
                    if qtd > produto['estoque_atual']:
                        messagebox.showerror("Erro", f"Estoque disponível: {produto['estoque_atual']} un.")
                        return
                    
                    self._adicionar_ao_carrinho(produto, qtd)
                    qtd_window.destroy()
                except ValueError:
                    messagebox.showerror("Erro", "Digite um número válido!")
            
            def cancelar():
                qtd_window.destroy()
            
            ctk.CTkButton(
                botoes_frame,
                text="✅ Adicionar",
                command=adicionar,
                fg_color="#00cc00",
                hover_color="#00aa00",
                width=100
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                botoes_frame,
                text="❌ Cancelar",
                command=cancelar,
                fg_color="#cc0000",
                hover_color="#990000",
                width=100
            ).pack(side="left", padx=5)
            
            # Permitir adicionar com Enter
            entrada.bind("<Return>", lambda e: adicionar())
            
        except Exception as e:
            print(f"[ERRO] Adicionando produto: {e}")
            messagebox.showerror("Erro", "Erro ao adicionar produto!")
    
    def _adicionar_ao_carrinho(self, produto: dict, quantidade: int):
        """Adiciona produto ao carrinho."""
        if quantidade <= 0 or quantidade > produto['estoque_atual']:
            messagebox.showerror("Erro", f"Quantidade inválida. Estoque: {produto['estoque_atual']}")
            return
        
        # Verificar se já existe
        for item in self.carrinho:
            if item['id_produto'] == produto['id_produto']:
                item['quantidade'] += quantidade
                self._atualizar_carrinho_ui()
                return
        
        # Adicionar novo
        self.carrinho.append({
            'id_produto': produto['id_produto'],
            'nome': produto['nome'],
            'preco': produto['preco_venda'],
            'quantidade': quantidade,
            'subtotal': produto['preco_venda'] * quantidade
        })
        self._atualizar_carrinho_ui()
    
    def _atualizar_carrinho_ui(self):
        """Atualiza a visualização do carrinho."""
        # Limpar
        for item in self.tree_carrinho.get_children():
            self.tree_carrinho.delete(item)
        
        # Adicionar itens
        for item in self.carrinho:
            self.tree_carrinho.insert(
                "",
                "end",
                text=item['nome'],
                values=(
                    f"R$ {item['preco']:.2f}",
                    item['quantidade'],
                    f"R$ {item['subtotal']:.2f}"
                )
            )
        
        self._atualizar_total()
    
    def _atualizar_total(self):
        """Atualiza o total com desconto."""
        subtotal = sum(float(item['subtotal']) for item in self.carrinho)
        
        try:
            desconto_pct = float(self.entry_desconto.get() or 0) / 100
            desconto_valor = subtotal * desconto_pct
            total = subtotal - desconto_valor
        except:
            desconto_valor = 0
            total = subtotal
        
        self.label_subtotal.configure(text=f"R$ {subtotal:.2f}")
        self.label_total.configure(text=f"R$ {total:.2f}")
    
    def _selecionar_cliente(self):
        """Seleciona cliente."""
        selecionado = self.combo_cliente.get()
        if selecionado == "Selecione um cliente":
            self.cliente_selecionado = None
        else:
            clientes = self.db.get_clientes()
            self.cliente_selecionado = next(
                (c for c in clientes if c['nome'] == selecionado),
                None
            )
    
    def _remover_item(self):
        """Remove item do carrinho."""
        selecionado = self.tree_carrinho.selection()
        if selecionado:
            idx = self.tree_carrinho.index(selecionado[0])
            self.carrinho.pop(idx)
            self._atualizar_carrinho_ui()
    
    def _editar_quantidade_carrinho(self, event):
        """Abre janela para editar quantidade do item do carrinho com duplo clique."""
        selecionado = self.tree_carrinho.selection()
        if not selecionado:
            return
        
        idx = self.tree_carrinho.index(selecionado[0])
        item = self.carrinho[idx]
        
        # Criar janela modal
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Editar Quantidade")
        edit_window.geometry("300x150")
        edit_window.resizable(False, False)
        
        # Tornar modal
        edit_window.transient(self)
        edit_window.grab_set()
        
        # Label do produto
        ctk.CTkLabel(
            edit_window,
            text=f"Produto: {item['nome']}",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=20)
        
        # Frame para entrada
        entrada_frame = ctk.CTkFrame(edit_window, fg_color="transparent")
        entrada_frame.pack(pady=10)
        
        ctk.CTkLabel(
            entrada_frame,
            text="Nova Quantidade:"
        ).pack(side="left", padx=5)
        
        entrada = ctk.CTkEntry(
            entrada_frame,
            width=80,
            placeholder_text="1"
        )
        entrada.pack(side="left", padx=5)
        entrada.insert(0, str(item['quantidade']))
        entrada.select_range(0, len(str(item['quantidade'])))
        entrada.focus()
        
        # Frame para botões
        botoes_frame = ctk.CTkFrame(edit_window, fg_color="transparent")
        botoes_frame.pack(pady=15)
        
        def salvar():
            try:
                nova_qtd = int(entrada.get())
                if nova_qtd <= 0:
                    messagebox.showerror("Erro", "Quantidade deve ser maior que 0!")
                    return
                
                # Atualizar item no carrinho
                self.carrinho[idx]['quantidade'] = nova_qtd
                self.carrinho[idx]['subtotal'] = nova_qtd * self.carrinho[idx]['preco']
                
                # Atualizar UI
                self._atualizar_carrinho_ui()
                
                edit_window.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Digite um número válido!")
        
        def cancelar():
            edit_window.destroy()
        
        ctk.CTkButton(
            botoes_frame,
            text="✅ Salvar",
            command=salvar,
            fg_color="#00cc00",
            hover_color="#00aa00",
            width=80
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            botoes_frame,
            text="❌ Cancelar",
            command=cancelar,
            fg_color="#cc0000",
            hover_color="#990000",
            width=80
        ).pack(side="left", padx=5)
        
        # Permitir salvar com Enter
        entrada.bind("<Return>", lambda e: salvar())
    
    def _limpar_carrinho(self):
        """Limpa o carrinho."""
        if messagebox.askyesno("Confirmar", "Limpar o carrinho?"):
            self.carrinho = []
            self._atualizar_carrinho_ui()
    
    def _finalizar_venda(self):
        """
        Finaliza a venda e salva TUDO no banco de dados.
        
        Este é o método MAIS IMPORTANTE do PDV!
        Aqui acontecem todas as operações críticas:
        
        FLUXO:
        1. Validar se tem itens no carrinho
        2. Validar se cliente foi selecionado
        3. Calcular total com desconto
        4. CRIAR PEDIDO no banco
        5. PARA CADA ITEM:
           a. Adicionar item ao pedido
           b. ATUALIZAR ESTOQUE (diminuir quantidade)
        6. Mostrar recibo
        7. Limpar tudo (carrinho, cliente, desconto)
        8. Fechar a janela automaticamente
        
        Após executar este método com sucesso:
        - Novo pedido é criado no banco
        - Estoque de produtos diminui
        - Vendedor vê mensagem de sucesso
        - Janela fecha automaticamente
        
        Se algo der errado, exibe mensagem de erro.
        """
        # VALIDAÇÃO 1: Verificar se tem itens no carrinho
        if not self.carrinho:
            messagebox.showerror("Erro", "Carrinho vazio!")
            return
        
        # VALIDAÇÃO 2: Verificar se cliente foi selecionado
        if not self.cliente_selecionado:
            messagebox.showerror("Erro", "Selecione um cliente!")
            return
        
        try:
            # === CÁLCULO DO TOTAL ===
            # Somar todos os subtotais dos itens
            subtotal = sum(float(item['subtotal']) for item in self.carrinho)
            
            # Ler desconto da entrada (em %)
            desconto_pct = float(self.entry_desconto.get() or 0) / 100
            
            # Aplicar desconto: total = subtotal * (1 - desconto%)
            total = subtotal * (1 - desconto_pct)
            
            # === CRIAR PEDIDO NO BANCO ===
            # Inserir novo pedido na tb_pedido
            pedido_id = self.db.criar_pedido(
                self.cliente_selecionado['id_cliente'],
                total,
                "concluído"  # Status já é concluído na hora da venda
            )
            
            # Verificar se pedido foi criado com sucesso
            if pedido_id:
                # === ADICIONAR ITENS AO PEDIDO ===
                # Para cada produto no carrinho
                for item in self.carrinho:
                    # Inserir item na tb_item_pedido
                    self.db.adicionar_item_pedido(
                        pedido_id,
                        item['id_produto'],
                        item['quantidade'],
                        item['preco']
                    )
                    
                    # === ATUALIZAR ESTOQUE ===
                    # CRÍTICO: Diminuir o estoque do produto
                    # Isso evita sobrevenda e mantém controle de inventário
                    self.db.atualizar_estoque(item['id_produto'], item['quantidade'])
                
                # === GUARDAR NOME DO CLIENTE ANTES DE LIMPAR ===
                # Importante: Guardar o nome ANTES de limpar self.cliente_selecionado
                # porque vamos exibir no messagebox depois
                nome_cliente = self.cliente_selecionado['nome']
                
                # === MOSTRAR RECIBO ===
                # Exibir recibo na tela (imprime também no console)
                self._mostrar_recibo(pedido_id, total)
                
                # === LIMPAR TUDO PARA PRÓXIMA VENDA ===
                self.carrinho = []                      # Limpar itens
                self.cliente_selecionado = None         # Desselecionar cliente
                self.entry_desconto.delete(0, "end")   # Limpar campo de desconto
                self.entry_desconto.insert(0, "0")     # Resetar para 0%
                self.combo_cliente.set("Selecione um cliente")  # Resetar combo
                self._atualizar_carrinho_ui()           # Atualizar tela
                
                # === MOSTRAR MENSAGEM DE SUCESSO ===
                messagebox.showinfo(
                    "✓ VENDA CONCLUÍDA",
                    f"Pedido #{pedido_id} finalizado com sucesso!\n\n"
                    f"Cliente: {nome_cliente}\n"
                    f"Total: R$ {total:.2f}"
                )
        
        except Exception as e:
            # Se algo deu errado, mostrar erro
            messagebox.showerror("Erro", f"Erro ao finalizar venda: {e}")
    
    def _mostrar_recibo(self, pedido_id: int, total: float):
        """Mostra o recibo da venda."""
        recibo = f"""
        ╔══════════════════════════════════╗
        ║      MOTOPECAS - RECIBO        ║
        ╠══════════════════════════════════╣
        ║ Pedido: #{pedido_id}
        ║ Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        ║ Funcionário: {self.funcionario_nome}
        ║ Cliente: {self.cliente_selecionado['nome']}
        ╠══════════════════════════════════╣
        """
        
        for item in self.carrinho:
            recibo += f"║ {item['nome'][:28]:28}\n"
            recibo += f"║ {item['quantidade']} x R$ {item['preco']:.2f} = R$ {item['subtotal']:.2f}\n"
        
        recibo += f"""╠══════════════════════════════════╣
        ║ TOTAL: R$ {total:.2f}
        ╚══════════════════════════════════╝
        """
        
        print(recibo)
