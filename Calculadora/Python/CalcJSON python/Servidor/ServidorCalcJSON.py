import socket
import threading
import json

PORTA = 12350

# -----------------------------------------------------------------------
# Matemática dos números complexos
# -----------------------------------------------------------------------
def soma_complexa(c1, c2):
    return {"re": c1["re"] + c2["re"], "im": c1["im"] + c2["im"]}

def subtracao_complexa(c1, c2):
    return {"re": c1["re"] - c2["re"], "im": c1["im"] - c2["im"]}

def multiplicacao_complexa(c1, c2):
    re = c1["re"] * c2["re"] - c1["im"] * c2["im"]
    im = c1["re"] * c2["im"] + c1["im"] * c2["re"]
    return {"re": re, "im": im}

# -----------------------------------------------------------------------
# Enviar e receber JSON pelo socket
# -----------------------------------------------------------------------
def enviar_json(connection, dados):
    mensagem = json.dumps(dados, separators=(',', ':')) + "\n"      
    connection.sendall(mensagem.encode())     # enviar como bytes

def receber_json(leitor):
    linha = leitor.readline()                 # lê até '\n'
    if not linha:
        return None
    return json.loads(linha)                  

# -----------------------------------------------------------------------
# Thread dedicada a cada cliente
# -----------------------------------------------------------------------
def tratar_cliente(conn, addr):
    print(f"[Thread] Nova ligação de {addr}")


    leitor = conn.makefile("r", encoding="utf-8")

    try:
        while True:
            # Receber pedido
            pedido = receber_json(leitor)
            if pedido is None:
                print(f"[Thread] Cliente {addr} desligou-se.")
                break

            print(f"[Thread] Pedido recebido: {pedido}")

            tipo = pedido.get("type")
            oper = pedido.get("oper")
            op1  = pedido.get("op1")
            op2  = pedido.get("op2")

            # Calcular resultado
            if tipo == "int":
                match oper:
                    case "+": resultado = op1 + op2
                    case "-": resultado = op1 - op2
                    case "*": resultado = op1 * op2
                    case "/": resultado = round(op1 / op2)
                    case _:
                        enviar_json(conn, {"error": f"Operação '{oper}' desconhecida"})
                        continue
                enviar_json(conn, {"result": resultado})

            elif tipo == "complex":
                match oper:
                    case "+": resultado = soma_complexa(op1, op2)
                    case "-": resultado = subtracao_complexa(op1, op2)
                    case "*": resultado = multiplicacao_complexa(op1, op2)
                    case _:
                        enviar_json(conn, {"error": f"Operação '{oper}' desconhecida"})
                        continue
                if resultado["im"] == 0:
                    enviar_json(conn, {"result": int(resultado["re"])})
                else:
                    enviar_json(conn, {"result": resultado})

            else:
                enviar_json(conn, {"error": f"Tipo '{tipo}' desconhecido"})

    except Exception as e:
        print(f"[Thread] Erro: {e}")
    finally:
        conn.close()
        print(f"[Thread] Ligação com {addr} encerrada.")

# -----------------------------------------------------------------------
# Servidor principal
# -----------------------------------------------------------------------
def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(("", PORTA))
    servidor.listen(5)
    print(f"ServidorCalcJSON à escuta na porta {PORTA}...")

    while True:
        conn, addr = servidor.accept()
        t = threading.Thread(target=tratar_cliente, args=(conn, addr), daemon=True)
        t.start()

if __name__ == "__main__":
    main()
