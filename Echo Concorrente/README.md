Este README serve como relatório para o laboratório AulaPratica-01-Sockets.pdf

1- Introdução:

O laboratório tinha o objetivo de estudar e implementar o modelo de comunicação cliente/servidor utilizando sockets e fazer com que o servidor em python fosse concorrente, usando as linguas de programação Python e Java.

2- Sockets:

Um socket é uma interface de programação que permite a comunicação entre dois processos através de uma rede de computadores. Um programa escreve dados num socket e outro programa lê esses dados. Neste peojeto usámos as linguas Python e Java e devido à utilização de sockets conseguímos fazer corretamente a comunicação entre cliente e servidor em diferentes linguagens alternadamente (Python com Java e vice-versa)

3- Modelo Cliente/Servidor:

O modelo cliente/servidor é um paradigma de comunicação em que: 
• O servidor fica à escuta numa porta, à espera de ligações de clientes. 
• O cliente inicia a ligação ao servidor e envia os pedidos. 
• O servidor processa os pedidos e devolve a resposta ao cliente.

4- Tipos de servidor:

Um servidor iterativo atende um cliente de cada vez, enquanto trata um cliente, os restantes ficam em espera, no entanto, neste laboratório trocamos de servidor iterativo a servidor concorrente o qual cria uma thread dedicada para cada cliente, permitindo atender múltiplos clientes em simultâneo.

5- Conclusão:

Este laboratório serviu-nos bastante para estudar e aprender a implementar os conceitos estudados nas aulas, tais como Sockets e modelos de comunicação, o que nos vai ajudar futuramente na implementação destes conceitos no nosso projeto final.
