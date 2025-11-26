"""
Dashboard com gráficos e estatísticas para MotoPeças.

O Dashboard é a "tela inicial" da aplicação.
Mostra um resumo completo das operações do dia/mês/período.

Exibe:
- Total de vendas (em R$)
- Quantidade de pedidos
- Quantidade de clientes
- Ticket médio
- Seção de PRODUTOS A REPOR (usando VIEW vw_produtos_a_repor)
  * Alerta visual: CRÍTICO (vermelho), BAIXO (amarelo), OK (verde)
- Seção de HISTÓRICO DE CLIENTES (usando VIEW vw_historico_vendas_por_cliente)
  * Exibe clientes com maior histórico de compras
- Gráfico de vendas por dia (últimos 7 dias)
- Gráfico de produtos mais vendidos
- Gráfico de top 5 clientes
- Botão para atualizar dados

Funcionalidades técnicas:
- Carrega dados em tempo real do banco (Views incluídas)
- Usa Matplotlib para gerar gráficos
- Auto-atualiza ao clicar no botão "Atualizar"
- Trata dados faltantes com valores padrão
- Integração com Views do banco de dados (vw_produtos_a_repor, vw_historico_vendas_por_cliente)
"""

import customtkinter as ctk
from core.database_basico import DatabaseManager
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from typing import Dict, List


class Dashboard:
    """
    Classe para exibir dashboard com gráficos e estatísticas.
    
    Responsabilidades:
    - Carregar dados do banco
    - Calcular métricas (KPIs)
    - Gerar gráficos com Matplotlib
    - Atualizar tela com informações
    """
    
    def __init__(self, parent: ctk.CTkFrame, db: DatabaseManager, funcionario_id: int):
        """
        Inicializa o dashboard.
        
        Args:
            parent: Frame pai que conterá o dashboard
            db: Gerenciador de banco de dados
            funcionario_id: ID do funcionário logado (para auditoria)
        """
        self.parent = parent
        self.db = db
        self.funcionario_id = funcionario_id
        
        # Criar a interface
        self._criar_dashboard()
    
    def _criar_dashboard(self):
        """
        Cria a interface completa do dashboard.
        
        Estrutura:
        1. Header com título e botão de atualizar
        2. Área de métricas (cards com números)
        3. Gráfico de vendas por dia (largura completa, compacto)
        4. Dois gráficos lado a lado (Produtos + Clientes)
        5. Tabela de alertas de estoque (compacta)
        6. Histórico de clientes
        """
        # Limpar widgets antigos (importante para atualização)
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Usar ScrollableFrame para melhor layout
        scroll_frame = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        try:
            # === HEADER ===
            header_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            header_frame.pack(fill="x", pady=15)
            
            label = ctk.CTkLabel(
                header_frame,
                text="📊 DASHBOARD",
                font=ctk.CTkFont(size=22, weight="bold")
            )
            label.pack(side="left", anchor="w")
            
            btn_atualizar = ctk.CTkButton(
                header_frame,
                text="🔄 Atualizar",
                command=self._criar_dashboard,
                fg_color="#3B8ED0",
                hover_color="#1f6aa5",
                width=120
            )
            btn_atualizar.pack(side="right", anchor="e", padx=10)
            
            # === KPIs ===
            self._criar_kpis(scroll_frame)
            
            # === GRÁFICO VENDAS POR DIA ===
            pedidos = self.db.get_pedidos()
            if pedidos:
                hoje = datetime.now()
                inicio_mes = datetime(hoje.year, hoje.month, 1)
                self._grafico_vendas_dia(scroll_frame, pedidos, inicio_mes)
            
            # === DOIS GRÁFICOS LADO A LADO ===
            graficos_row = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            graficos_row.pack(fill="both", expand=True, pady=10)
            
            # Gráfico Produtos Vendidos (esquerda)
            produtos_frame = ctk.CTkFrame(graficos_row, fg_color="transparent")
            produtos_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
            
            if pedidos:
                self._grafico_produtos_vendidos(produtos_frame, pedidos, inicio_mes)
            
            # Gráfico Top Clientes (direita)
            clientes_frame = ctk.CTkFrame(graficos_row, fg_color="transparent")
            clientes_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
            
            if pedidos:
                self._grafico_top_clientes(clientes_frame, pedidos, inicio_mes)
            
            # === TABELA DE ALERTAS ===
            self._criar_produtos_repor(scroll_frame)
            
            # === HISTÓRICO DE CLIENTES ===
            self._criar_historico_clientes(scroll_frame)
            
        except Exception as e:
            print(f"[ERRO] Criando dashboard: {e}")
            import traceback
            traceback.print_exc()
    
    def _criar_kpis(self, parent):
        """Cria cards com KPIs (Total de vendas, etc)."""
        kpi_frame = ctk.CTkFrame(parent, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=15)
        
        # Calcular data do início do mês
        hoje = datetime.now()
        inicio_mes = datetime(hoje.year, hoje.month, 1)
        
        try:
            # Total de vendas do mês
            pedidos = self.db.get_pedidos()
            total_vendas = 0
            total_items = 0
            
            for pedido in pedidos:
                data_pedido = datetime.fromisoformat(str(pedido['data_pedido']))
                if data_pedido >= inicio_mes:
                    total_vendas += float(pedido['valor_total'] or 0)
                    # Contar itens
                    items = self.db.get_itens_pedido(pedido['id_pedido'])
                    total_items += len(items)
            
            # KPI Card 1: Total de Vendas
            card1 = ctk.CTkFrame(
                kpi_frame,
                fg_color="#1a5c1a",
                corner_radius=10,
                border_width=2,
                border_color="#2d8c2d"
            )
            card1.pack(side="left", padx=10, fill="both", expand=True)
            card1.configure(height=100)
            
            ctk.CTkLabel(
                card1,
                text="💰 Total de Vendas",
                font=ctk.CTkFont(size=11),
                text_color="#aaaaaa"
            ).pack(pady=(10, 0))
            
            ctk.CTkLabel(
                card1,
                text=f"R$ {total_vendas:,.2f}",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#00ff00"
            ).pack(pady=(0, 10))
            
            # KPI Card 2: Quantidade de Pedidos
            card2 = ctk.CTkFrame(
                kpi_frame,
                fg_color="#1a3a5c",
                corner_radius=10,
                border_width=2,
                border_color="#2d5c8c"
            )
            card2.pack(side="left", padx=10, fill="both", expand=True)
            card2.configure(height=100)
            
            ctk.CTkLabel(
                card2,
                text="📦 Pedidos",
                font=ctk.CTkFont(size=11),
                text_color="#aaaaaa"
            ).pack(pady=(10, 0))
            
            ctk.CTkLabel(
                card2,
                text=str(len([p for p in pedidos if datetime.fromisoformat(str(p['data_pedido'])) >= inicio_mes])),
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#00aaff"
            ).pack(pady=(0, 10))
            
            # KPI Card 3: Itens Vendidos
            card3 = ctk.CTkFrame(
                kpi_frame,
                fg_color="#5c1a3a",
                corner_radius=10,
                border_width=2,
                border_color="#8c2d5c"
            )
            card3.pack(side="left", padx=10, fill="both", expand=True)
            card3.configure(height=100)
            
            ctk.CTkLabel(
                card3,
                text="🛒 Itens Vendidos",
                font=ctk.CTkFont(size=11),
                text_color="#aaaaaa"
            ).pack(pady=(10, 0))
            
            ctk.CTkLabel(
                card3,
                text=str(total_items),
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#ff00aa"
            ).pack(pady=(0, 10))
        
        except Exception as e:
            print(f"[ERRO] Calculando KPIs: {e}")
    
    def _criar_produtos_repor(self, parent):
        """
        Cria seção de produtos que precisam reposição.
        
        Usa a VIEW vw_produtos_a_repor do banco de dados para exibir
        produtos com estoque abaixo do mínimo.
        
        Codificação de alerta:
        - CRÍTICO: Vermelho vivo (#ff3333) - Estoque zerado
        - BAIXO: Amarelo (#ffaa00) - Estoque baixo
        - OK: Verde (#00cc00) - Estoque normal
        """
        try:
            # Buscar dados da VIEW
            produtos = self.db.get_produtos_a_repor()
            
            if not produtos:
                # Nenhum produto a repor - mostrar mensagem positiva
                info_frame = ctk.CTkFrame(parent, fg_color="#2d5a2d", corner_radius=8, border_width=1, border_color="#00aa00")
                info_frame.pack(fill="x", pady=10)
                
                ctk.CTkLabel(
                    info_frame,
                    text="✅ Todos os produtos têm estoque adequado!",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#00ff00"
                ).pack(pady=10)
                return
            
            # Header da seção
            header = ctk.CTkFrame(parent, fg_color="transparent")
            header.pack(fill="x", pady=(15, 5))
            
            ctk.CTkLabel(
                header,
                text="⚠️ PRODUTOS A REPOR",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#ffaa00"
            ).pack(side="left", anchor="w")
            
            ctk.CTkLabel(
                header,
                text=f"({len(produtos)} produto{'s' if len(produtos) > 1 else ''})",
                font=ctk.CTkFont(size=11),
                text_color="#aaaaaa"
            ).pack(side="left", anchor="w", padx=10)
            
            # Frame para a tabela (compacta)
            table_frame = ctk.CTkFrame(parent, fg_color="#1a1a1a", corner_radius=8, border_width=1, border_color="#444444")
            table_frame.pack(fill="both", expand=True, pady=(0, 15))
            
            # Header da tabela
            header_table = ctk.CTkFrame(table_frame, fg_color="#2b2b2b", corner_radius=0)
            header_table.pack(fill="x")
            
            cols = [
                ("SKU", 0.12),
                ("Produto", 0.35),
                ("Custo", 0.10),
                ("Est. Atual", 0.12),
                ("Est. Mínimo", 0.12),
                ("Necessário", 0.12),
                ("Status", 0.07)
            ]
            
            for col_name, width in cols:
                ctk.CTkLabel(
                    header_table,
                    text=col_name,
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color="#00aaff"
                ).place(relx=sum([w for _, w in cols[:cols.index((col_name, width))]]), relwidth=width, relheight=1)
            
            # Adicionar altura ao header
            header_table.configure(height=30)
            
            # Linhas de produtos (ordenado por status crítico primeiro)
            produtos_sorted = sorted(produtos, key=lambda x: {"CRÍTICO": 0, "BAIXO": 1, "OK": 2}.get(x.get('status_estoque', 'OK'), 2))
            
            for idx, produto in enumerate(produtos_sorted):
                # Definir cores baseadas no status
                status = produto.get('status_estoque', 'OK')
                if status == 'CRÍTICO':
                    bg_color = "#3d1a1a"
                    border_color = "#ff3333"
                    status_color = "#ff3333"
                    status_emoji = "🔴"
                elif status == 'BAIXO':
                    bg_color = "#3d3d1a"
                    border_color = "#ffaa00"
                    status_color = "#ffaa00"
                    status_emoji = "🟡"
                else:
                    bg_color = "#1a3d1a"
                    border_color = "#00aa00"
                    status_color = "#00aa00"
                    status_emoji = "🟢"
                
                row_frame = ctk.CTkFrame(
                    table_frame,
                    fg_color=bg_color,
                    border_width=1,
                    border_color=border_color,
                    corner_radius=0
                )
                row_frame.pack(fill="x")
                row_frame.configure(height=35)
                
                # Dados do produto
                dados = [
                    produto.get('sku', '-')[:10],
                    produto.get('nome', '-')[:30],
                    f"R$ {float(produto.get('preco_custo', 0)):.2f}",
                    f"{produto.get('estoque_atual', 0)} un",
                    f"{produto.get('estoque_minimo', 0)} un",
                    f"{produto.get('quantidade_necessaria', 0)} un",
                    f"{status_emoji} {status}"
                ]
                
                for col_idx, (col_name, width) in enumerate(cols):
                    col_x = sum([w for _, w in cols[:col_idx]])
                    
                    # Cor diferente para status
                    if col_idx == len(cols) - 1:
                        fg_color = status_color
                        weight = "bold"
                    else:
                        fg_color = "#ffffff"
                        weight = "normal"
                    
                    ctk.CTkLabel(
                        row_frame,
                        text=dados[col_idx],
                        font=ctk.CTkFont(size=9, weight=weight),
                        text_color=fg_color
                    ).place(relx=col_x, relwidth=width, relheight=1)
        
        except Exception as e:
            print(f"[ERRO] Criando seção de produtos a repor: {e}")
    
    def _criar_historico_clientes(self, parent):
        """
        Cria seção com histórico de vendas por cliente.
        
        Usa a VIEW vw_historico_vendas_por_cliente do banco de dados
        para exibir:
        - Nome do cliente
        - Total de pedidos
        - Total gasto
        - Última compra
        - Ticket médio
        """
        try:
            # Buscar dados da VIEW
            clientes_historico = self.db.get_historico_vendas_por_cliente()
            
            if not clientes_historico:
                # Nenhum cliente com histórico
                return
            
            # Header da seção
            header = ctk.CTkFrame(parent, fg_color="transparent")
            header.pack(fill="x", pady=(15, 5))
            
            ctk.CTkLabel(
                header,
                text="👥 HISTÓRICO DE CLIENTES",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#00aaff"
            ).pack(side="left", anchor="w")
            
            ctk.CTkLabel(
                header,
                text=f"({len(clientes_historico)} cliente{'s' if len(clientes_historico) > 1 else ''})",
                font=ctk.CTkFont(size=11),
                text_color="#aaaaaa"
            ).pack(side="left", anchor="w", padx=10)
            
            # Frame para a tabela (compacta)
            table_frame = ctk.CTkFrame(parent, fg_color="#1a1a1a", corner_radius=8, border_width=1, border_color="#444444")
            table_frame.pack(fill="both", expand=True, pady=(0, 15))
            
            # Header da tabela
            header_table = ctk.CTkFrame(table_frame, fg_color="#2b2b2b", corner_radius=0)
            header_table.pack(fill="x")
            
            cols = [
                ("Cliente", 0.25),
                ("Pedidos", 0.12),
                ("Total Gasto", 0.18),
                ("Última Compra", 0.20),
                ("Ticket Médio", 0.15),
                ("Ativo", 0.10)
            ]
            
            for col_name, width in cols:
                ctk.CTkLabel(
                    header_table,
                    text=col_name,
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color="#00aaff"
                ).place(relx=sum([w for _, w in cols[:cols.index((col_name, width))]]), relwidth=width, relheight=1)
            
            # Adicionar altura ao header
            header_table.configure(height=30)
            
            # Linhas de clientes (ordenado por total gasto)
            clientes_sorted = sorted(
                clientes_historico,
                key=lambda x: float(x.get('total_gasto', 0)),
                reverse=True
            )
            
            for idx, cliente in enumerate(clientes_sorted):
                row_frame = ctk.CTkFrame(
                    table_frame,
                    fg_color="#1f1f1f" if idx % 2 == 0 else "#2a2a2a",
                    border_width=0,
                    corner_radius=0
                )
                row_frame.pack(fill="x")
                row_frame.configure(height=35)
                
                # Formatar dados
                ultima_compra = cliente.get('ultima_compra', '-')
                if ultima_compra and ultima_compra != '-':
                    try:
                        from datetime import datetime as dt
                        data_obj = dt.fromisoformat(str(ultima_compra))
                        ultima_compra = data_obj.strftime("%d/%m/%Y")
                    except:
                        pass
                
                dados = [
                    cliente.get('cliente_nome', '-')[:40],
                    f"{cliente.get('total_pedidos', 0)}",
                    f"R$ {float(cliente.get('total_gasto', 0)):.2f}",
                    str(ultima_compra),
                    f"R$ {float(cliente.get('ticket_medio', 0)):.2f}",
                    "✅" if cliente.get('total_pedidos', 0) > 0 else "❌"
                ]
                
                for col_idx, (col_name, width) in enumerate(cols):
                    col_x = sum([w for _, w in cols[:col_idx]])
                    
                    # Cor para valores numéricos importantes
                    if col_idx == 2:  # Total gasto
                        fg_color = "#00ff00"
                    else:
                        fg_color = "#ffffff"
                    
                    ctk.CTkLabel(
                        row_frame,
                        text=dados[col_idx],
                        font=ctk.CTkFont(size=9),
                        text_color=fg_color
                    ).place(relx=col_x, relwidth=width, relheight=1)
        
        except Exception as e:
            print(f"[ERRO] Criando seção de histórico de clientes: {e}")
    
    
    def _grafico_vendas_dia(self, parent, pedidos: List[Dict], inicio_mes):
        """Gráfico de vendas por dia do mês."""
        try:
            # Dados por dia
            vendas_por_dia = {}
            
            for pedido in pedidos:
                data = datetime.fromisoformat(str(pedido['data_pedido']))
                if data >= inicio_mes:
                    dia = data.day
                    valor = float(pedido['valor_total'] or 0)
                    vendas_por_dia[dia] = vendas_por_dia.get(dia, 0) + valor
            
            if not vendas_por_dia:
                return
            
            # Criar figura (tamanho bem reduzido)
            fig = Figure(figsize=(12, 2), dpi=80, facecolor="#2b2b2b")
            ax = fig.add_subplot(111)
            ax.set_facecolor("#1a1a1a")
            
            dias = sorted(vendas_por_dia.keys())
            valores = [vendas_por_dia[d] for d in dias]
            
            ax.bar(dias, valores, color="#00cc00", edgecolor="#00ff00", linewidth=1.5)
            ax.set_xlabel("Dia do Mês", color="white", fontsize=9)
            ax.set_ylabel("Vendas (R$)", color="white", fontsize=9)
            ax.set_title("Vendas por Dia", color="white", fontsize=11, weight="bold", pad=10)
            ax.tick_params(colors="white", labelsize=8)
            ax.grid(True, alpha=0.2, color="white")
            
            # Canvas (sem expandir muito)
            canvas_frame = ctk.CTkFrame(parent, fg_color="transparent")
            canvas_frame.pack(fill="x", pady=5)
            
            canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="x")
        
        except Exception as e:
            print(f"[ERRO] Gráfico vendas por dia: {e}")
    
    def _grafico_produtos_vendidos(self, parent, pedidos: List[Dict], inicio_mes):
        """Gráfico dos produtos mais vendidos."""
        try:
            produtos_vendidos = {}
            
            for pedido in pedidos:
                data = datetime.fromisoformat(str(pedido['data_pedido']))
                if data >= inicio_mes:
                    items = self.db.get_itens_pedido(pedido['id_pedido'])
                    for item in items:
                        nome = item.get('nome_produto', 'Produto')
                        qtd = item.get('quantidade', 0)
                        produtos_vendidos[nome] = produtos_vendidos.get(nome, 0) + qtd
            
            if not produtos_vendidos:
                return
            
            # Top 5
            top_produtos = dict(sorted(produtos_vendidos.items(), key=lambda x: x[1], reverse=True)[:5])
            
            fig = Figure(figsize=(6, 3), dpi=80, facecolor="#2b2b2b")
            ax = fig.add_subplot(111)
            ax.set_facecolor("#1a1a1a")
            
            nomes = list(top_produtos.keys())
            quantidades = list(top_produtos.values())
            
            ax.barh(nomes, quantidades, color="#0088ff", edgecolor="#00aaff", linewidth=1.5)
            ax.set_xlabel("Quantidade Vendida", color="white", fontsize=9)
            ax.set_title("Produtos Mais Vendidos (Top 5)", color="white", fontsize=11, weight="bold", pad=10)
            ax.tick_params(colors="white", labelsize=8)
            ax.grid(True, alpha=0.2, color="white", axis="x")
            
            canvas_frame = ctk.CTkFrame(parent, fg_color="transparent")
            canvas_frame.pack(fill="both", expand=True, pady=5)
            
            canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        
        except Exception as e:
            print(f"[ERRO] Gráfico produtos: {e}")
    
    def _grafico_top_clientes(self, parent, pedidos: List[Dict], inicio_mes):
        """Gráfico dos clientes que mais compraram."""
        try:
            clientes_vendas = {}
            
            for pedido in pedidos:
                data = datetime.fromisoformat(str(pedido['data_pedido']))
                if data >= inicio_mes:
                    cliente_id = pedido['id_cliente']
                    valor = float(pedido['valor_total'] or 0)
                    
                    # Buscar nome do cliente
                    cliente = self.db.get_cliente(cliente_id)
                    nome = cliente['nome'] if cliente else f"Cliente {cliente_id}"
                    
                    clientes_vendas[nome] = clientes_vendas.get(nome, 0) + valor
            
            if not clientes_vendas:
                return
            
            # Top 5
            top_clientes = dict(sorted(clientes_vendas.items(), key=lambda x: x[1], reverse=True)[:5])
            
            fig = Figure(figsize=(6, 3), dpi=80, facecolor="#2b2b2b")
            ax = fig.add_subplot(111)
            ax.set_facecolor("#1a1a1a")
            
            nomes = list(top_clientes.keys())
            valores = list(top_clientes.values())
            
            cores = ["#ff6b6b", "#ffa500", "#ffd700", "#98fb98", "#87ceeb"]
            ax.barh(nomes, valores, color=cores[:len(nomes)], edgecolor="white", linewidth=1.5)
            ax.set_xlabel("Total Gasto (R$)", color="white", fontsize=9)
            ax.set_title("Top 5 Clientes", color="white", fontsize=11, weight="bold", pad=10)
            ax.tick_params(colors="white", labelsize=8)
            ax.grid(True, alpha=0.2, color="white", axis="x")
            
            canvas_frame = ctk.CTkFrame(parent, fg_color="transparent")
            canvas_frame.pack(fill="both", expand=True, pady=5)
            
            canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        
        except Exception as e:
            print(f"[ERRO] Gráfico top clientes: {e}")
