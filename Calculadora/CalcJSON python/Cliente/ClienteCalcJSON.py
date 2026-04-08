import json
import socket

PORTA = 12350
HOST  = "localhost"

def enviar_pedido(sock, leitor, dados):
    mensagem = json.dumps(dados, separators=(',', ':')) + "\n"
    sock.sendall(mensagem.encode())
    return json.loads(leitor.readline())

def formatar_resultado(resposta):
    r = resposta["result"]
    if isinstance(r, dict):
        sinal = "+" if r["im"] >= 0 else ""
        return f"{r['re']}{sinal}{r['im']}i"
    return str(r)

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORTA))
    leitor = sock.makefile("r", encoding="utf-8")
    print(f"Ligado ao servidor em {HOST}:{PORTA}\n")

    # --- Inteiros --- type="int", operadores normais
    print("=== Operações com inteiros ===")
    for oper in ["+", "-", "*", "/"]:
        resposta = enviar_pedido(sock, leitor,
            {"type": "int", "op1": 5, "op2": 2, "oper": oper})
        print(f"  5 {oper} 2 = {formatar_resultado(resposta)}")

    # --- Complexos --- type="complex", mesmos operadores!
    print("\n=== Operações com complexos ===")
    c1 = {"re": 2, "im": 3}
    c2 = {"re": 1, "im": 4}
    for oper in ["+", "-", "*"]:
        resposta = enviar_pedido(sock, leitor,
            {"type": "complex", "op1": c1, "op2": c2, "oper": oper})
        print(f"  (2+3i) {oper} (1+4i) = {formatar_resultado(resposta)}")

    sock.close()
    print("\nLigação encerrada.")

if __name__ == "__main__":
    main()





