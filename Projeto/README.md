Este README serve como relatório para o projeto da cadeira de Computação Distribuida.
Introdução:
____________________

O resultado foi o conjunto das seguintes fases:

Fase 1:
Nesta primeira fase do projeto de Computação Distribuida foram-nos pedidos diferentes objetivos, os quais com a aprendizagem dos laboratórios, fomos capazes de cumprir. A ideia principal desta fase era adaptar o trabalho prático desenvolvido na Unidade Curricular de Programação Web para um ambiente de contentores de acordo com os seguintes objetivos:

  Objetivo 1: Separar a persistência de dados do backend Web
    Antes, o nosso "Server.py" lia e escrevia ficheiros JSON diretamente no disco com "open()". Agora essa responsabilidade passou para um servidor a parte "db".
    Mudamos as seguintes funções:
    - loadData(fName), em vez de open(fName): 
        Esta função abre uma ligação TCP ao servidor db na porta "12345", envia um JSON com "{"action": "load", "file": fName}" e recebe a resposta JSON com os dados.
    - saveData(fName, data), em vez de open(fName, 'w'):
        Abre uma ligação TCP ao servidor db na porta "12345" e enva um JSON com "{"action": "save", "file": fName, "data": data}" e recebe a confirmação de resposta.

    
