USE motopecas_db;

-- =============================================
-- CRUD PRODUTOS
-- =============================================

-- CREATE (cadastrar produto)
INSERT INTO tb_produto
(sku, nome, descricao, id_categoria, preco_custo, preco_venda, estoque_atual, estoque_minimo, ativo)
VALUES
('TEST-001', 'Produto Teste', 'Produto usado em testes', 1, 10.00, 20.00, 5, 1, 1);

-- READ (listar todos)
SELECT * FROM tb_produto;

-- READ (buscar por SKU)
SELECT * FROM tb_produto WHERE sku = 'MT-0001';

-- READ (buscar por nome - LIKE)
SELECT * FROM tb_produto
WHERE nome LIKE '%freio%';

-- READ (buscar por categoria)
SELECT p.*
FROM tb_produto p
JOIN tb_categoria c ON c.id_categoria = p.id_categoria
WHERE c.nome = 'Freios';

-- UPDATE (editar produto)
UPDATE tb_produto
SET nome = 'Produto Teste EDITADO',
    preco_venda = 25.00
WHERE id_produto = 1;  -- ajustar ID conforme sua tabela

-- DELETE (soft delete: desativar produto)
UPDATE tb_produto
SET ativo = 0
WHERE id_produto = 1;


-- =============================================
-- CRUD FORNECEDORES
-- =============================================

-- CREATE
INSERT INTO tb_fornecedor
(nome_fantasia, razao_social, cnpj, telefone, email, endereco, ativo)
VALUES
('Fornecedor Teste', 'Fornecedor Teste LTDA', '99999999000199',
 '(65) 90000-0000', 'fornecedor.teste@teste.com', 'Rua Teste, 123', 1);

-- READ (todos)
SELECT * FROM tb_fornecedor;

-- READ (por nome)
SELECT * FROM tb_fornecedor
WHERE nome_fantasia LIKE '%Moto%';

-- UPDATE
UPDATE tb_fornecedor
SET telefone = '(65) 95555-0000'
WHERE id_fornecedor = 1;

-- DELETE (soft delete)
UPDATE tb_fornecedor
SET ativo = 0
WHERE id_fornecedor = 1;


-- =============================================
-- CRUD CLIENTES
-- =============================================

-- CREATE
INSERT INTO tb_cliente
(nome, cpf, telefone, email, endereco, ativo)
VALUES
('Cliente Teste', '12312312399', '(65) 91111-1111',
 'cliente.teste@teste.com', 'Rua do Cliente Teste, 10', 1);

-- READ (todos)
SELECT * FROM tb_cliente;

-- READ (por nome)
SELECT * FROM tb_cliente
WHERE nome LIKE '%Silva%';

-- UPDATE
UPDATE tb_cliente
SET telefone = '(65) 92222-2222'
WHERE id_cliente = 1;

-- DELETE (soft delete)
UPDATE tb_cliente
SET ativo = 0
WHERE id_cliente = 1;


-- =============================================
-- CRUD FUNCIONÁRIOS
-- =============================================

-- CREATE
INSERT INTO tb_funcionario
(nome, cpf, cargo, email, telefone, senha_hash, ativo)
VALUES
('Funcionario Teste', '98798798799', 'Vendedor',
 'func.teste@lojamoto.com', '(65) 93333-3333',
 'hash_senha_qualquer', 1);

-- READ (todos)
SELECT * FROM tb_funcionario;

-- READ (por cargo)
SELECT * FROM tb_funcionario
WHERE cargo = 'Vendedor';

-- UPDATE
UPDATE tb_funcionario
SET cargo = 'Supervisor de Vendas'
WHERE id_funcionario = 1;

-- DELETE (soft delete)
UPDATE tb_funcionario
SET ativo = 0
WHERE id_funcionario = 1;


-- =============================================
-- CRUD PEDIDOS (usando procedures já criadas)
-- =============================================

-- CREATE: feito via procedure sp_registrar_venda
SET @itens_venda_ex = JSON_ARRAY(
  JSON_OBJECT('id_produto', 1, 'quantidade', 1),
  JSON_OBJECT('id_produto', 2, 'quantidade', 2)
);
CALL sp_registrar_venda(1, 1, @itens_venda_ex);

-- READ: listar pedidos
SELECT * FROM tb_pedido;

-- READ: pedidos + cliente
SELECT p.id_pedido, p.data_pedido, p.valor_total, p.status,
       c.nome AS cliente
FROM tb_pedido p
JOIN tb_cliente c ON c.id_cliente = p.id_cliente;

-- READ: itens de um pedido específico
SELECT ip.*, pr.nome AS produto
FROM tb_item_pedido ip
JOIN tb_produto pr ON pr.id_produto = ip.id_produto
WHERE ip.id_pedido = 1;

-- UPDATE: editar quantidade de um item de pedido (exemplo simples)
UPDATE tb_item_pedido
SET quantidade = 5
WHERE id_item_pedido = 1;

-- DELETE / CANCELAMENTO: cancelar pedido (status)
UPDATE tb_pedido
SET status = 'CANCELADO'
WHERE id_pedido = 1;
