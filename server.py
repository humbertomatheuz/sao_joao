import http.server
import socketserver
import sqlite3
import json
import os

PORT = 8080
DB_NAME = "sao_joao.db"

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def address_string(self):
        # Evita a consulta reversa de DNS (lookup), acelerando as requisições no Windows
        return self.client_address[0]

    def end_headers(self):
        # Desativa o cache do navegador para evitar o carregamento de HTML/dados obsoletos
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_OPTIONS(self):
        # Suporta pre-flight requests do CORS para o método POST
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()



    def do_GET(self):
        # Rota da API para retornar os dados do SQLite
        if self.path == '/api/shows':
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("SELECT banda, local, data FROM shows ORDER BY data ASC")
                rows = cursor.fetchall()
                conn.close()
                
                # Mapeia os dados no formato esperado pelo frontend
                shows = []
                for row in rows:
                    shows.append({
                        "Banda/Artista": row[0],
                        "Local": row[1],
                        "Data": row[2]
                    })
                
                response_bytes = json.dumps(shows, ensure_ascii=False).encode('utf-8')
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Length', str(len(response_bytes)))
                self.end_headers()
                
                self.wfile.write(response_bytes)
                
            except Exception as e:
                response_bytes = json.dumps({"error": str(e)}).encode('utf-8')
                
                self.send_response(500)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Length', str(len(response_bytes)))
                self.end_headers()
                
                self.wfile.write(response_bytes)
        else:
            # Serve os arquivos estáticos (index.html, etc)
            super().do_GET()

if __name__ == "__main__":
    # Garante que o servidor rode na pasta correta
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Configura e inicia o servidor
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"Servidor rodando em http://localhost:{PORT}")
        print("Consumindo dados diretamente do banco SQLite local.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor finalizado.")
