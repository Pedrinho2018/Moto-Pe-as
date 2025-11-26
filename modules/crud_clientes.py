"""
CRUD de Clientes para MotoPeças.

Funcionalidades:
- Criar novo cliente
- Editar cliente existente
- Deletar cliente
- Validar CPF e email
"""

import customtkinter as ctk
from core.database_basico import DatabaseManager
from typing import Optional, Callable
import re


class CRUDClientes:
    """Classe para gerenciar CRUD de clientes."""
    
    def __init__(self, parent: ctk.CTkFrame, db: DatabaseManager, callback: Optional[Callable] = None):
        """
        Inicializa o CRUD de clientes.
        
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
        """Cria a interface de gerenciamento de clientes."""
        # Header com botão de novo
        header_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)
        
        label = ctk.CTkLabel(
            header_frame,
            text="👥 CLIENTES",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        label.pack(side="left", anchor="w")
        
        btn_novo = ctk.CTkButton(
            header_frame,
            text="➕ Novo Cliente",
            command=self._abrir_form_novo,
            fg_color="#2d8c2d",
            hover_color="#1a5c1a",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        btn_novo.pack(side="right", padx=10)
        
        # Scroll frame com clientes
        scroll_frame = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        try:
            clientes = self.db.get_clientes()
            
            if clientes:
                # Configurar grid para 3 colunas
                for i in range(3):
                    scroll_frame.grid_columnconfigure(i, weight=1)
                
                for idx, cliente in enumerate(clientes):
                    row = idx // 3
                    col = idx % 3
                    
                    # Card do cliente
                    card = ctk.CTkFrame(
                        scroll_frame,
                        fg_color="#2b2b2b",
                        border_color="#444444",
                        border_width=2,
                        corner_radius=10
                    )
                    card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                    card.grid_propagate(False)
                    card.configure(width=250, height=280)
                    
                    # Nome do cliente
                    nome_label = ctk.CTkLabel(
                        card,
                        text=cliente['nome'],
                        font=ctk.CTkFont(size=13, weight="bold"),
                        wraplength=220,
                        justify="center"
                    )
                    nome_label.pack(pady=(10, 5), padx=10)
                    
                    # CPF
                    cpf_label = ctk.CTkLabel(
                        card,
                        text=f"CPF: {cliente['cpf']}",
                        font=ctk.CTkFont(size=10),
                        text_color="#888888"
                    )
                    cpf_label.pack(pady=2, padx=10)
                    
                    # Divisor
                    divisor = ctk.CTkFrame(card, fg_color="#444444", height=1)
                    divisor.pack(fill="x", padx=10, pady=8)
                    
                    # Email
                    email = cliente.get('email', 'Não informado')
                    email_display = email[:25] + "..." if len(str(email)) > 25 else email
                    
                    email_label = ctk.CTkLabel(
                        card,
                        text=f"Email: {email_display}",
                        font=ctk.CTkFont(size=9),
                        text_color="#aaaaaa",
                        wraplength=220,
                        justify="center"
                    )
                    email_label.pack(pady=3, padx=8)
                    
                    # Telefone
                    telefone = cliente.get('telefone', 'Não informado')
                    
                    tel_label = ctk.CTkLabel(
                        card,
                        text=f"Tel: {telefone}",
                        font=ctk.CTkFont(size=9),
                        text_color="#aaaaaa"
                    )
                    tel_label.pack(pady=2, padx=10)
                    
                    # Endereço
                    endereco = cliente.get('endereco', 'Não informado')
                    if endereco and len(endereco) > 30:
                        endereco_text = f"End: {endereco[:30]}..."
                    elif endereco:
                        endereco_text = f"End: {endereco}"
                    else:
                        endereco_text = "End: Não informado"
                    
                    end_label = ctk.CTkLabel(
                        card,
                        text=endereco_text,
                        font=ctk.CTkFont(size=8),
                        text_color="#666666",
                        wraplength=220,
                        justify="center"
                    )
                    end_label.pack(pady=(3, 8), padx=8)
                    
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
                        command=lambda c=cliente: self._abrir_form_editar(c)
                    )
                    btn_editar.pack(side="left", padx=2, fill="x", expand=True)
                    
                    btn_deletar = ctk.CTkButton(
                        btn_frame,
                        text="🗑️ Deletar",
                        font=ctk.CTkFont(size=10),
                        fg_color="#cc0000",
                        hover_color="#990000",
                        command=lambda c=cliente: self._confirmar_deletar(c)
                    )
                    btn_deletar.pack(side="left", padx=2, fill="x", expand=True)
            else:
                ctk.CTkLabel(
                    scroll_frame,
                    text="Nenhum cliente cadastrado",
                    font=ctk.CTkFont(size=14)
                ).pack(pady=50)
        
        except Exception as e:
            ctk.CTkLabel(
                self.parent,
                text=f"Erro ao carregar clientes: {e}",
                text_color="red",
                font=ctk.CTkFont(size=12)
            ).pack(pady=20)
    
    def _abrir_form_novo(self):
        """Abre formulário para criar novo cliente."""
        FormCliente(self.parent, self.db, None, self._atualizar)
    
    def _abrir_form_editar(self, cliente: dict):
        """Abre formulário para editar cliente."""
        FormCliente(self.parent, self.db, cliente, self._atualizar)
    
    def _confirmar_deletar(self, cliente: dict):
        """Confirma deleção de cliente."""
        janela = ctk.CTkToplevel(self.parent)
        janela.title("Confirmar Deleção")
        janela.geometry("400x200")
        janela.grab_set()
        
        ctk.CTkLabel(
            janela,
            text=f"Deletar cliente '{cliente['nome']}'?",
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
            if self.db.deletar_cliente(cliente['id_cliente']):
                janela.destroy()
                self._atualizar()
            else:
                ctk.CTkLabel(
                    janela,
                    text="Erro ao deletar cliente",
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


class FormCliente(ctk.CTkToplevel):
    """Janela de formulário para criar/editar cliente."""
    
    def __init__(self, parent, db: DatabaseManager, cliente: Optional[dict] = None, callback: Optional[Callable] = None):
        """
        Inicializa o formulário.
        
        Args:
            parent: Janela pai
            db: Gerenciador de banco de dados
            cliente: Cliente a editar (None para novo)
            callback: Função a executar após salvar
        """
        super().__init__(parent)
        self.db = db
        self.cliente = cliente
        self.callback = callback
        self.titulo = "Editar Cliente" if cliente else "Novo Cliente"
        
        self.title(self.titulo)
        self.geometry("500x500")
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
        
        # Nome
        ctk.CTkLabel(scroll, text="Nome Completo:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
        self.entry_nome = ctk.CTkEntry(scroll, placeholder_text="Ex: João Silva")
        self.entry_nome.pack(fill="x", pady=(0, 15))
        
        # CPF
        ctk.CTkLabel(scroll, text="CPF:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
        self.entry_cpf = ctk.CTkEntry(scroll, placeholder_text="Ex: 123.456.789-00")
        self.entry_cpf.pack(fill="x", pady=(0, 15))
        
        # Email
        ctk.CTkLabel(scroll, text="Email:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
        self.entry_email = ctk.CTkEntry(scroll, placeholder_text="Ex: joao@email.com")
        self.entry_email.pack(fill="x", pady=(0, 15))
        
        # Telefone
        ctk.CTkLabel(scroll, text="Telefone:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
        self.entry_telefone = ctk.CTkEntry(scroll, placeholder_text="Ex: (11) 98765-4321")
        self.entry_telefone.pack(fill="x", pady=(0, 15))
        
        # Endereço
        ctk.CTkLabel(scroll, text="Endereço:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
        self.entry_endereco = ctk.CTkEntry(scroll, placeholder_text="Ex: Rua Principal, 123")
        self.entry_endereco.pack(fill="x", pady=(0, 15))
        
        # Preencher dados se editando
        if self.cliente:
            self.entry_nome.insert(0, self.cliente['nome'])
            self.entry_cpf.insert(0, self.cliente['cpf'])
            self.entry_email.insert(0, self.cliente['email'])
            self.entry_telefone.insert(0, self.cliente['telefone'])
            self.entry_endereco.insert(0, self.cliente['endereco'])
        
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
    
    def _validar_cpf(self, cpf: str) -> bool:
        """Valida formato do CPF."""
        # Remover formatação
        cpf_limpo = cpf.replace(".", "").replace("-", "")
        # Validar se tem 11 dígitos
        return len(cpf_limpo) == 11 and cpf_limpo.isdigit()
    
    def _validar_email(self, email: str) -> bool:
        """Valida formato do email."""
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao, email) is not None
    
    def _salvar(self):
        """Salva os dados do cliente."""
        try:
            nome = self.entry_nome.get().strip()
            cpf = self.entry_cpf.get().strip()
            email = self.entry_email.get().strip()
            telefone = self.entry_telefone.get().strip()
            endereco = self.entry_endereco.get().strip()
            
            # Validações
            if not nome:
                print("Nome é obrigatório")
                return
            
            if not self._validar_cpf(cpf):
                print("CPF inválido. Use formato: 123.456.789-00")
                return
            
            if not self._validar_email(email):
                print("Email inválido")
                return
            
            if not telefone:
                print("Telefone é obrigatório")
                return
            
            if not endereco:
                print("Endereço é obrigatório")
                return
            
            if self.cliente:
                # Atualizar
                if self.db.atualizar_cliente(
                    self.cliente['id_cliente'],
                    nome=nome, cpf=cpf, email=email,
                    telefone=telefone, endereco=endereco
                ):
                    print(f"✓ Cliente '{nome}' atualizado")
                    self.destroy()
                    if self.callback:
                        self.callback()
            else:
                # Criar
                cliente_id = self.db.criar_cliente(nome, cpf, telefone, email, endereco)
                if cliente_id:
                    print(f"✓ Cliente '{nome}' criado (ID: {cliente_id})")
                    self.destroy()
                    if self.callback:
                        self.callback()
        
        except Exception as e:
            print(f"Erro ao salvar: {e}")
