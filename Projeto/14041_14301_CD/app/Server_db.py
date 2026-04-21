import socket
import json
import logging
import os

HOST = '0.0.0.0'
PORT = 12345
DATA_DIR = './private'

logging.basicConfig(level=logging.DEBUG)

def handle_request(data):
    try:
        payload = json.loads(data)
        action = payload.get('action')
        filename = payload.get('file')

        # Garante que o caminho é sempre dentro de DATA_DIR
        filepath = os.path.join(DATA_DIR, os.path.basename(filename))

        if action == 'load':
            with open(filepath, 'r', encoding='utf-8') as f:
                content = json.load(f)
            return json.dumps(content)

        elif action == 'save':
            file_data = payload.get('data')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(file_data, f, ensure_ascii=False, indent=2)
            return json.dumps({"status": "ok"})

        else:
            return json.dumps({"status": "error", "message": "Ação desconhecida"})

    except Exception as e:
        logging.error(f"Erro: {e}")
        return json.dumps({"status": "error", "message": str(e)})


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)
        logging.info(f"Servidor DB à escuta em {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            with conn:
                logging.debug(f"Ligação de {addr}")
                data = conn.recv(65536)
                response = handle_request(data.decode('utf-8'))
                conn.sendall(response.encode('utf-8'))

if __name__ == '__main__':
    main()