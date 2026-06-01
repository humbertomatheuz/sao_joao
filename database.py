import sqlite3
import csv
import urllib.request
import os

DB_NAME = "sao_joao.db"
CSV_URL = "https://docs.google.com/spreadsheets/d/1R5nJqo9jHy5GR0DH3y19ogJd3gTz3VAm5AJ9tfKkNuM/gviz/tq?tqx=out:csv"

def get_connection():
    """Retorna uma conexão ativa com o banco de dados SQLite."""
    return sqlite3.connect(DB_NAME)

def init_db():
    """Cria a tabela 'shows' se ela não existir no banco."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            banda TEXT NOT NULL,
            local TEXT NOT NULL,
            data TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("Tabela 'shows' inicializada no SQLite (sem coluna de horário).")

def sync_with_sheets():
    """Baixa os dados da planilha e sincroniza/popula o banco SQLite local."""
    init_db()
    print(f"Conectando à planilha para sincronização...")
    
    try:
        req = urllib.request.Request(
            CSV_URL, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req) as response:
            csv_content = response.read().decode('utf-8').splitlines()
            
        reader = csv.reader(csv_content)
        raw_rows = list(reader)
        
        if len(raw_rows) < 4:
            print("A planilha possui linhas insuficientes.")
            return

        # Encontra o índice da linha de cabeçalho
        header_index = -1
        for idx, row in enumerate(raw_rows):
            row_str = "".join(row)
            if "Banda/Artista" in row_str:
                header_index = idx
                break
                
        if header_index == -1:
            print("Erro: Coluna 'Banda/Artista' não encontrada na planilha.")
            return

        headers = raw_rows[header_index]
        
        # Identifica a posição de cada coluna
        banda_idx = -1
        local_idx = -1
        data_idx = -1
        
        for idx, h in enumerate(headers):
            if "Banda/Artista" in h:
                banda_idx = idx
            elif "Local" in h:
                local_idx = idx
            elif "Data" in h:
                data_idx = idx

        if banda_idx == -1 or local_idx == -1 or data_idx == -1:
            print("Erro: Colunas necessárias ausentes na planilha.")
            return

        data_rows = raw_rows[header_index + 1:]
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Limpa registros antigos para sincronização limpa
        cursor.execute("DELETE FROM shows")
        
        inserted = 0
        for row in data_rows:
            if len(row) > max(banda_idx, local_idx, data_idx) and row[banda_idx].strip():
                banda = row[banda_idx].strip()
                local = row[local_idx].strip()
                data = row[data_idx].strip()
                
                cursor.execute(
                    "INSERT INTO shows (banda, local, data) VALUES (?, ?, ?)",
                    (banda, local, data)
                )
                inserted += 1
                
        conn.commit()
        conn.close()
        print(f"Sincronização concluída com sucesso! {inserted} shows importados.")
        
    except Exception as e:
        print(f"Ocorreu um erro ao sincronizar: {e}")

def list_shows():
    """Retorna a lista completa de shows ordenados por data."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, banda, local, data FROM shows ORDER BY data ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def insert_show(banda, local, data):
    """Insere manualmente um show no banco de dados SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO shows (banda, local, data) VALUES (?, ?, ?)",
        (banda, local, data)
    )
    conn.commit()
    conn.close()
    print(f"Show '{banda}' inserido localmente no SQLite.")

if __name__ == "__main__":
    # Roda a sincronização automática ao executar o script
    sync_with_sheets()
    
    # Exibe os 5 primeiros registros gravados no SQLite
    shows = list_shows()
    print("\n--- Lista de Shows (Primeiros 5 Registros) ---")
    for show in shows[:5]:
        print(f"ID: {show[0]} | Banda: {show[1]} | Local: {show[2]} | Data: {show[3]}")
