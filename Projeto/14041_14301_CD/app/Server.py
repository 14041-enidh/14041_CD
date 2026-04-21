#
# Importar as bibliotecas necessárias
from flask import Flask, redirect, send_file, request, render_template, session

from flask_session import Session
from flask_mail import Mail, Message

import uuid
import logging
import json
import re
import socket


host = '0.0.0.0'
port = 12345
    
emailRegEx = "^[a-z0-9_\.\-]+@[a-z0-9\-]+\.[a-z]{2,4}$"
vatRegEx = "^[\d]{9}$"
passwordRegEx = "^[\w]{3,7}$"

#
# Flask application object (app) no contexto do módulo Python currente
#
app = Flask(__name__)
app.url_map.strict_slashes = False

app.config[ 'TEMPLATES_AUTO_RELOAD' ] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


app.config[ 'MAIL_SERVER' ]= 'smtp.gmail.com'
app.config[ 'MAIL_PORT' ] = 465
app.config[ 'MAIL_USERNAME' ] = 'aulaweb45@gmail.com'
app.config[ 'MAIL_PASSWORD' ] = 'hxprphxtmqezmjup'
app.config[ 'MAIL_USE_TLS' ] = False
app.config[ 'MAIL_USE_SSL' ] = True

Session(app)
mail = Mail(app)

#
# Ativar o nível de log para debug
#
logging.basicConfig( level=logging.DEBUG )

#
# Função auxiliar para ler dados JSON (em formato utf-8) de um ficheiro
#
def loadData(fName):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect(('db', 12345))

            # Agora com campo 'action'
            request = json.dumps({
                "action": "load",
                "file": fName
            })
            s.sendall(request.encode('utf-8'))

            response = s.recv(65536).decode('utf-8')
            data = json.loads(response)

        return data
    except Exception as e:
        logging.error(f"Erro ao carregar dados via socket: {e}")
        return {}

#
# Função auxiliar para escrever dados JSON (em formato utf-8) num ficheiro
#
def saveData(fName, data):
    try:
        # Estabelecer ligação com o servidor BS
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect(('db', 12345))  # Mesmo host e porta

            # Construir o JSON com nome do ficheiro e dados
            payload = {
                "action": "save",
                "file": fName,
                "data": data
            }
            s.sendall(json.dumps(payload).encode('utf-8'))

            # Esperar resposta de confirmação
            response = s.recv(1024).decode('utf-8')
            return json.loads(response)
    except Exception as e:
        logging.error(f"Erro ao guardar dados via socket: {e}")
        return {"status": "error", "message": str(e)}


#
# Adicionar o tratamento das rotas / e /static e /static/
#
# Redirecionar para a página de index (/static/index.html)
#
@app.route('/')
@app.route('/static')
def getRoot():
    logging.debug( f"Route / called..." )
    return redirect( "/static/index.html", code=302 )

@app.route('/favicon.ico')
def getFavicon():
    logging.debug( f"Route /favicon.ico called..." )
    return send_file( "./static/favicon.ico", as_attachment=True, max_age=1 )

@app.route('/produtos')
def getProdutos():
    return loadData("produtos.json")

@app.route('/account')
def account():
    if not session.get("MAIL"):
        return redirect('/formLogin')

    email = session['MAIL']
    data = loadData("users.json")
    for user in data['usersInfo'][0]['user']:
        if user['email'] == email:
            return render_template('account.html', user=user)

    return "Usuário não encontrado", 404

@app.route('/go-back', methods=['POST'])
def go_back():
    return render_template( 'HomePage.html')

@app.route('/account/update', methods=['GET', 'POST'])
def update_account():
    if not session.get("MAIL"):
        return redirect('/formLogin')

    if request.method == 'POST':
        email = session['MAIL']
        address = request.form.get('address')
        age = request.form.get('age')
        profile_picture = request.files.get('profile_picture')

        data = loadData("users.json")
        for user in data['usersInfo'][0]['user']:
            if user['email'] == email:
                if address:
                    user['address'] = address
                if age:
                    user['age'] = int(age)  # Salva a idade como número
                if profile_picture:
                    file_path = f'./static/images/profiles/{email}.jpg'
                    profile_picture.save(file_path)
                    user['profile_picture'] = file_path

                saveData('./private/users.json', data)
                return redirect('/account')

        return "Usuário não encontrado", 404

    return render_template('update_account.html')

@app.route('/admin')
def adminPage():
    # Renderiza a página do admin
    return render_template('admin.html') 

@app.route('/cart')
def cartPage():
    # Renderiza a página do carrinho
    return render_template('cart.html')  # Crie o arquivo cart.html

@app.route('/formLogin')
def buildFormLogin():
    logging.debug( f"Route /FormLogin called..." )

    return redirect( "/static/index.html", emailRegEx=emailRegEx, passwordRegEx=passwordRegEx )

@app.route('/cart')
def cart():
    logging.debug("Route /cart called...")
    return render_template('cart.html')

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    try:
        # Obtém o índice do produto do corpo da requisição
        data = request.get_json()
        index = int(data['index'])  # Garante que o índice seja um inteiro

        # Carrega os dados dos usuários
        users_data = loadData('users.json')
        current_user_email = session.get('MAIL')

        # Encontra o usuário atual
        current_user = None
        for user_group in users_data['usersInfo']:
            for user in user_group['user']:
                if user['email'] == current_user_email:
                    current_user = user
                    break

        if not current_user:
            return {"error": "Usuário não encontrado."}, 404

        # Verifica se o índice é válido
        if not current_user.get('produtos') or index < 0 or index >= len(current_user['produtos']):
            return {"error": "Índice inválido!"}, 400

        # Remove o produto pelo índice
        removed_product = current_user['produtos'].pop(index)
        saveData('./private/users.json', users_data)

        return {
            "message": f"Produto '{removed_product}' removido com sucesso!",
            "produtos": current_user['produtos']
        }
    except KeyError:
        return {"error": "Índice não fornecido no corpo da requisição."}, 400
    except ValueError:
        return {"error": "Índice deve ser um número válido."}, 400
    except Exception as e:
        return {"error": str(e)}, 500




@app.route('/get_session')
def get_session():
    return {
        "email": session.get("MAIL"),
        "admin": session.get("IS_ADMIN", False)
    }




@app.route('/doLogin', methods=(['POST']) ) #funcionar
def doLogin():
    logging.debug( f"Route /doLogin called..." )

    email = request.form[ 'email' ]
    logging.debug( f"email recebida: {email}" )
    
    password = request.form[ 'password' ]
    logging.debug( f"Password recebida: {password}" )

    emailCheck = re.search( passwordRegEx, email)
    logging.debug( f"Check password: {emailCheck}" )
    
    passworCheck = re.search( passwordRegEx, password)
    logging.debug( f"Check password: {passworCheck}" )

    data = loadData("users.json")

    for user in data['usersInfo'][0]['user']:
        if (user['email'] == email and user['password'] == password):
            if user['mailConfirmado'] == True:
                session['MAIL'] = email
                session['IS_ADMIN'] = user.get('admin', False)  
                return buildFormProfile()
          
        
    return render_template( 'dadosInvalidosT.html', errorMessage="E-Mail não confirmado/Nif invalido/Password errada", redirectURL=request.referrer ) 

@app.route('/doAccCreate', methods=(['POST']) ) #funcionar
def doAccCreate():
    logging.debug( f"Route /doAccCreate called..." )

    mail = request.form[ 'email' ]
    logging.debug( f"Mail recebido: {mail}" )

    password = request.form[ 'password' ]
    logging.debug( f"Password recebida: {password}" )
    
    confirmpassword = request.form[ 'confirm-password' ]
    logging.debug( f"ConfirmPassword recebida: {confirmpassword}" )

    mailCheck = re.search( emailRegEx, mail)
    logging.debug( f"Check mail: {mailCheck}" )

    passworCheck = re.search( passwordRegEx, password)
    logging.debug( f"Check password: {passworCheck}" )
    
    confirmpassworCheck = re.search( passwordRegEx, confirmpassword)
    logging.debug( f"Check password: {confirmpassworCheck}" )

    if (mailCheck==False or passworCheck==False or confirmpassworCheck==False):
        return render_template( 'dadosInvalidosT.html', errorMessage="Formato dos dados inválido", redirectURL=request.referrer ) 
    
    if(confirmpassword != password):
        return render_template( 'dadosInvalidosT.html', errorMessage="Passwords nao sao iguais!", redirectURL=request.referrer ) 
    
    data = loadData("users.json")
        
    novo_user = {
    "email": mail,
    "password": password,
    "mailConfirmado": False
    }
        
    data['usersInfo'][0]['user'].append(novo_user)
    saveData('./private/users.json', data)
        
    doSendEmail(mail)
    return redirect( "/static/index.html", code=302 ) #Mudar isto secalhar ta errado


@app.route('/formProfile')
def buildFormProfile():
    logging.debug( f"Route /buildFormProfile called..." )

    if not session.get( "MAIL" ):
        return buildFormLogin()

    
    return render_template( 'HomePage.html')
    #return render_template( 'formProfileT.html', districts=districts )


@app.route("/doLogout")
def doLogout():
    logging.debug( f"Route /doLogout called..." )

    session[ 'MAIL' ] = None
    
    return redirect( "/static/index.html" )


def doSendEmail(mailEnviar): #funcionar
    logging.debug(f"Route /doSendEmail called...")

    _subject = 'Hello from the other side!'
    _senderName = 'Pg Web Semester 24/25'
    _senderEmail = 'aulaweb45@gmail.com'

    # identificador único para a solicitação
    confirmation_id = str(uuid.uuid4())

    # Salvar o ID e o e-mail associado no arquivo JSON
    data = loadData("email_confirmations.json")
    data['confirmations'][confirmation_id] = mailEnviar
    saveData('./private/email_confirmations.json', data)

    confirmation_link = f"http://localhost/confirm_email?id={confirmation_id}"
    _msgContent = f"""
    Olá!
    Clique no link abaixo para confirmar o e-mail:
    {confirmation_link}
    """

    msg = Message(
        subject=_subject,
        sender=(_senderName, _senderEmail),
        recipients=[mailEnviar]
    )

    msg.body = _msgContent

    mail.send(msg)

    return "Message sent!"

@app.route('/confirm_email') #funcionar
def confirm_email():
    confirmation_id = request.args.get('id')

    if not confirmation_id:
        return render_template('dadosInvalidosT.html', errorMessage="Erro: Parâmetro de confirmação não encontrado", redirectURL=request.referrer)

    # Carregar os dados das confirmações
    data = loadData("email_confirmations.json")

    # Verificar se o ID de confirmação existe
    if confirmation_id not in data['confirmations']:
        return render_template('dadosInvalidosT.html', errorMessage="Erro: ID de confirmação inválido", redirectURL=request.referrer)

    email = data['confirmations'][confirmation_id]
    logging.debug( f"{email}" )
    # Atualizar o status do e-mail no arquivo de usuários
    user_data = loadData("users.json")
    for user in user_data['usersInfo'][0]['user']:
        if user['email'] == email:
            user['mailConfirmado'] = True
            saveData('./private/users.json', user_data)
            logging.debug(f"E-mail confirmado para {email}")

            # Remover o ID de confirmação usado
            del data['confirmations'][confirmation_id]
            saveData('./private/email_confirmations.json', data)

            return redirect("/static/mailConfirmado.html")

    return render_template('dadosInvalidosT.html', errorMessage="Erro: Usuário não encontrado.", redirectURL=request.referrer)



@app.route('/product/<int:product_id>')
def product_detail(product_id):
    products = loadData("produtos.json")
    if 0 <= product_id < len(products):
        product = products[product_id]
        # Adicione uma descrição fictícia caso ela não exista no JSON
        product['description'] = product.get('description', 'Informações detalhadas do produto ainda não estão disponíveis.')
        return render_template('product.html', product=product)
    else:
        return "Produto não encontrado", 404
    
    
    
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if not session.get("MAIL"):
        return {"error": "Usuário não autenticado"}, 401

    email = session['MAIL']
    product_name = request.json.get('product_name')  # Recebe o nome do produto enviado pelo cliente

    if not product_name:
        return {"error": "Nome do produto não fornecido"}, 400

    data = loadData("users.json")
    for user in data['usersInfo'][0]['user']:
        if user['email'] == email:
            if "produtos" not in user:
                user["produtos"] = []
            user["produtos"].append(product_name)  # Adiciona o produto ao carrinho
            saveData('./private/users.json', data)
            return {"message": f'Produto "{product_name}" adicionado ao carrinho'}, 200

    return {"error": "Usuário não encontrado"}, 404


@app.route('/get_cart')
def get_cart():
    logging.debug("Route /get_cart called...")

    # Carregar dados do usuário
    users_data = loadData("users.json")
    current_user_email = session.get('MAIL')

    logging.debug(f"Current user email: {current_user_email}")

    # Encontrar o usuário atual
    current_user = None
    for user_group in users_data['usersInfo']:
        for user in user_group['user']:
            if user['email'] == current_user_email:
                current_user = user
                break

    if not current_user or not current_user.get('produtos'):
        logging.debug("No products found for the current user.")
        return {"produtos": []}

    logging.debug(f"Products in cart: {current_user['produtos']}")

    # Carregar dados dos produtos
    products_data = loadData("produtos.json")

    # Mapear produtos do carrinho com detalhes completos
    cart_products = []
    for product_name in current_user['produtos']:
        product_detail = next((prod for prod in products_data if prod['name'] == product_name), None)
        if product_detail:
            cart_products.append(product_detail)

    return {"produtos": cart_products}


if __name__ == '__main__':
        app.run(host='0.0.0.0', port=80)
