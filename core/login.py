"""
Módulo de Login - Tela de autenticação para MotoPeças.

Esta é a PRIMEIRA tela que o usuário vê ao abrir o programa.
Aqui ele seleciona o funcionário e digita a senha.

Fluxo:
1. Carregar lista de funcionários do banco
2. Usuário seleciona qual funcionário é
3. Digita a senha
4. Clica em LOGIN
5. Sistema valida a senha
6. Se correto, abre a aplicação principal
7. Se errado, mostra erro

A tela de login é CRÍTICA para segurança:
- Impede acesso não autorizado
- Registra qual funcionário está usando o sistema
- Permite auditoria de ações
"""

import customtkinter as ctk  # type: ignore
from tkinter import messagebox
try:
    from .database_basico import DatabaseManager
except ImportError:
    from core.database_basico import DatabaseManager
from mysql.connector import Error as MySQLError


class LoginWindow(ctk.CTk):
    """
    Janela de Login para autenticação de funcionários.
    
    Funcionalidades:
    - Combobox com lista de funcionários ativos
    - Campo de entrada para senha
    - Botão LOGIN e SAIR
    - Validação de credenciais no banco
    """

    def __init__(self):
        """
        Inicializa a janela de login.
        
        Na inicialização:
        1. Cria a janela
        2. Posiciona no centro da tela
        3. Cria interface (layout)
        4. Carrega funcionários do banco
        """
        super().__init__()
        self.title("MotoPeças - Login")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # === CENTRALIZAR JANELA ===
        # Cálculo para colocar a janela no meio da tela
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (400 // 2)      # Centralizar em X
        y = (screen_height // 2) - (500 // 2)     # Centralizar em Y
        self.geometry(f"+{x}+{y}")
        
        # Configurar tema dark/azul
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # === ATRIBUTOS ===
        # Guardar dados do login para usar depois
        self.usuario_selecionado = None           # Nome do funcionário selecionado
        self.funcionario_id = None                # ID do funcionário (chave primária)
        self.funcionarios_dados = []              # Lista de funcionários carregados
        self.combo_usuario = None                 # Widget do combobox
        self.entry_senha = None                   # Widget do campo de senha
        
        # Conectar ao banco
        self.db_manager = DatabaseManager()
        
        # Criar a interface visual
        self._criar_interface()
        
        # Carregar funcionários do banco para popular combobox
        self._carregar_funcionarios()

    def _criar_interface(self):
        """
        Cria a interface visual da tela de login.
        
        Layout:
        - Fundo escuro
        - Container centralizado
        - Logo e título
        - ComboBox para selecionar funcionário
        - Campo para digitar senha
        - Botões LOGIN e SAIR
        """
        # Frame principal com fundo escuro
        main_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        main_frame.pack(fill="both", expand=True)

        # Frame centralizado (container)
        center_frame = ctk.CTkFrame(main_frame, fg_color="transparent", width=320, height=380)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # ========== LOGO ==========
        # Logo com emoji de moto
        logo_label = ctk.CTkLabel(
            center_frame,
            text="🏍️ MOTOPEÇAS",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#1f6aa5",  # Azul característico
        )
        logo_label.pack(pady=(0, 30))

        # ========== SUBTÍTULO ==========
        subtitle_label = ctk.CTkLabel(
            center_frame,
            text="Sistema de Vendas",
            font=ctk.CTkFont(size=12),
            text_color="#999999",  # Cinza discreto
        )
        subtitle_label.pack(pady=(0, 30))

        # ========== SELEÇÃO DE FUNCIONÁRIO ==========
        # Label
        usuario_label = ctk.CTkLabel(
            center_frame,
            text="Funcionário:",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        usuario_label.pack(anchor="w", pady=(0, 5))

        # ComboBox para selecionar funcionário
        # Será populado depois por _carregar_funcionarios()
        self.combo_usuario = ctk.CTkComboBox(
            center_frame,
            values=[],  # Preenchido depois
            state="readonly",  # Só pode selecionar, não digitar
            height=40,
            font=ctk.CTkFont(size=12),
        )
        self.combo_usuario.pack(fill="x", pady=(0, 15))
        self.combo_usuario.set("Selecione um funcionário...")

        # ========== CAMPO DE SENHA ==========
        # Label
        senha_label = ctk.CTkLabel(
            center_frame,
            text="Senha:",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        senha_label.pack(anchor="w", pady=(0, 5))

        self.entry_senha = ctk.CTkEntry(
            center_frame,
            placeholder_text="Digite sua senha",
            show="*",
            height=40,
            font=ctk.CTkFont(size=12),
        )
        self.entry_senha.pack(fill="x", pady=(0, 30))
        
        # Suporte a Enter na entrada de senha
        self.entry_senha.bind("<Return>", lambda e: self._fazer_login())

        # ========== BOTÃO ENTRAR ==========
        self.btn_entrar = ctk.CTkButton(
            center_frame,
            text="ENTRAR",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=50,
            fg_color="#1f6aa5",
            hover_color="#0d3f7f",
            text_color="white",
            command=self._fazer_login,
        )
        self.btn_entrar.pack(fill="x", pady=(0, 15))

        # ========== INFORMAÇÕES ==========
        info_label = ctk.CTkLabel(
            center_frame,
            text="Use suas credenciais de funcionário. Senhas criptografadas com bcrypt.",
            font=ctk.CTkFont(size=10),
            text_color="#666666",
            wraplength=280,
            justify="center",
        )
        info_label.pack(pady=(20, 0))

    def _carregar_funcionarios(self):
        """
        Carrega lista de funcionários ativos do banco de dados.
        Usa DatabaseManager para obter dados de tb_funcionario.
        """
        try:
            # Usar DatabaseManager para obter funcionários
            funcionarios = self.db_manager.get_funcionarios()
            
            if funcionarios:
                # Armazenar dados dos funcionários
                self.funcionarios_dados = funcionarios
                
                # Formatar como "ID - Nome" para exibição no ComboBox
                opcoes = [f"{f['id_funcionario']} - {f['nome']}" for f in funcionarios]
                
                # Atualizar ComboBox com os funcionários carregados
                self.combo_usuario.configure(values=opcoes)
                
                print(f"[OK] {len(funcionarios)} funcionário(s) carregado(s) com sucesso!")
            else:
                messagebox.showwarning(
                    "Aviso",
                    "Nenhum funcionário ativo encontrado no banco de dados."
                )
        
        except MySQLError as e:
            # Erro de conexão ou banco de dados
            messagebox.showerror(
                "Erro de Banco de Dados",
                f"Erro ao carregar funcionários:\n\n{str(e)}\n\n"
                f"Verifique as configurações de conexão."
            )
            print(f"[ERRO] Banco de dados: {e}")
        
        except Exception as e:
            # Erro inesperado
            messagebox.showerror(
                "Erro Inesperado",
                f"Erro inesperado ao carregar funcionários:\n\n{str(e)}"
            )
            print(f"[ERRO] {e}")

    def _fazer_login(self):
        """Realiza validação de login com segurança."""
        # Obter seleções
        usuario = self.combo_usuario.get()
        senha = self.entry_senha.get()

        # Validar campos
        if "Selecione" in usuario or usuario == "":
            messagebox.showwarning("Aviso", "Selecione um funcionário!")
            return

        if not senha or len(senha) == 0:
            messagebox.showwarning("Aviso", "Digite a senha!")
            return

        # Extrair ID do funcionário
        try:
            id_func = int(usuario.split(" - ")[0])
        except (ValueError, IndexError):
            messagebox.showerror("Erro", "Formato de funcionário inválido!")
            return

        # ========== VERIFICAR SENHA (SEGURO COM BCRYPT) ==========
        # Usar o método verificar_senha que agora usa bcrypt
        if self.db_manager.verificar_senha(id_func, senha):
            # LOGIN BEM-SUCEDIDO
            self.funcionario_id = id_func
            self.usuario_selecionado = usuario
            messagebox.showinfo("Sucesso", f"Bem-vindo, {usuario.split(' - ')[1]}!")
            self.destroy()  # Fecha janela de login
        else:
            # LOGIN FALHOU
            messagebox.showerror("Erro", "Funcionário ou senha incorretos!")
            self.entry_senha.delete(0, "end")
            self.entry_senha.focus()

    def obter_funcionario_id(self):
        """Retorna o ID do funcionário logado."""
        return self.funcionario_id

    def obter_usuario_nome(self):
        """Retorna o nome do funcionário logado."""
        if self.usuario_selecionado:
            return self.usuario_selecionado.split(" - ")[1]
        return None
