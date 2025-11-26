#!/usr/bin/env python3
"""
Script de Migração: Converter Senhas Antigas para Bcrypt

IMPORTANTE:
Este script converte todas as senhas em texto plano no banco de dados
para hashes seguros usando bcrypt.

COMO USAR:
python scripts/migrar_senhas_bcrypt.py

O que faz:
1. Conecta ao banco de dados
2. Lê todas as senhas em texto plano
3. Gera hashes bcrypt para cada uma
4. Atualiza o banco de dados
5. Valida se a migração funcionou

AVISO:
- Execute uma única vez!
- Faça backup do banco ANTES de executar
- Não rode novamente ou terá erros
"""

import sys
import os

# Adicionar o diretório pai ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database_basico import DatabaseManager
import bcrypt


def migrar_senhas():
    """
    Executa a migração de senhas antigas para bcrypt.
    """
    print("\n" + "="*60)
    print("🔐 MIGRAÇÃO DE SENHAS PARA BCRYPT")
    print("="*60)
    
    db = DatabaseManager()
    
    try:
        # Conectar ao banco
        with db.get_db_cursor(dictionary=True) as (conn, cur):
            print("\n[1/4] Lendo senhas do banco de dados...")
            
            # Buscar todos os funcionários com senhas
            sql = "SELECT id_funcionario, nome, senha_hash FROM tb_funcionario WHERE ativo = 1"
            cur.execute(sql)
            funcionarios = cur.fetchall()
            
            print(f"    ✓ {len(funcionarios)} funcionário(s) encontrado(s)")
            
            if not funcionarios:
                print("    ⚠ Nenhum funcionário encontrado!")
                return
            
            print("\n[2/4] Gerando hashes bcrypt...")
            
            hashes_novos = {}
            for func in funcionarios:
                id_func = func['id_funcionario']
                nome = func['nome']
                senha_antiga = func['senha_hash']
                
                if not senha_antiga:
                    print(f"    ⚠ {nome} (ID: {id_func}) - SEM SENHA, pulando...")
                    continue
                
                # Gerar hash bcrypt para a senha antiga
                try:
                    senha_bytes = senha_antiga.encode('utf-8')
                    salt = bcrypt.gensalt(rounds=12)
                    hash_novo = bcrypt.hashpw(senha_bytes, salt).decode('utf-8')
                    hashes_novos[id_func] = hash_novo
                    print(f"    ✓ {nome} (ID: {id_func}) - Hash gerado")
                except Exception as e:
                    print(f"    ✗ {nome} (ID: {id_func}) - Erro: {e}")
                    continue
            
            print(f"\n[3/4] Atualizando {len(hashes_novos)} senha(s) no banco...")
            
            # Atualizar cada funcionário com o novo hash
            atualizados = 0
            for id_func, hash_novo in hashes_novos.items():
                try:
                    sql_update = "UPDATE tb_funcionario SET senha_hash = %s WHERE id_funcionario = %s"
                    cur.execute(sql_update, (hash_novo, id_func))
                    atualizados += 1
                except Exception as e:
                    print(f"    ✗ Erro atualizando funcionário {id_func}: {e}")
            
            # Fazer commit
            conn.commit()
            print(f"    ✓ {atualizados} senha(s) atualizada(s)")
            
            print("\n[4/4] Validando migração...")
            
            # Validar: testar se uma senha antiga ainda funciona
            if len(hashes_novos) > 0:
                id_teste = list(hashes_novos.keys())[0]
                func_teste = next(f for f in funcionarios if f['id_funcionario'] == id_teste)
                senha_original = func_teste['senha_hash']
                
                # Tentar login com a senha antiga
                senha_hash_novo = hashes_novos[id_teste]
                try:
                    senha_bytes = senha_original.encode('utf-8')
                    hash_bytes = senha_hash_novo.encode('utf-8')
                    resultado = bcrypt.checkpw(senha_bytes, hash_bytes)
                    
                    if resultado:
                        print(f"    ✓ Validação OK - Senha antiga ainda funciona com hash novo!")
                    else:
                        print(f"    ✗ Validação FALHOU - Senha antiga não funciona!")
                except Exception as e:
                    print(f"    ✗ Erro na validação: {e}")
            
            print("\n" + "="*60)
            print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("="*60)
            print("\nPróximas ações:")
            print("1. Teste o login com um funcionário")
            print("2. Use a MESMA senha anterior (agora criptografada)")
            print("3. Se funcionar, a migração foi bem-sucedida")
            print("\n")
    
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("\nVerifique:")
        print("- Conexão com o banco de dados")
        print("- Arquivo .env com credenciais corretas")
        print("- Permissões no banco de dados")
        sys.exit(1)


if __name__ == "__main__":
    migrar_senhas()
