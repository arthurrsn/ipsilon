from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore, storage
from werkzeug.utils import secure_filename
import os
import uuid  # Para gerar nomes únicos para os arquivos

app = Flask(__name__)
app.secret_key = 'calwdawdasnmdu23g238sdyhawdmbausd77d8u089gjkfgkjvbfvb'  # Para gerenciar as sessões

# Inicializando o Firebase
cred = credentials.Certificate('firebase_config.json')  # Arquivo JSON de chave do Firebase
firebase_admin.initialize_app(cred, {
    'storageBucket': 'forum-a3ed4.appspot.com'  # Nome correto do bucket
})
db = firestore.client()
bucket = storage.bucket()

# Função para verificar os tipos de arquivo permitidos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rota para a página de login
@app.route('/')
def login():
    return render_template('login.html')

# Rota para autenticar o login
@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form['username']
    password = request.form['password']

    # Verifica se o usuário existe no Firestore
    users_ref = db.collection('users')
    query = users_ref.where('username', '==', username).get()

    if query:
        user = query[0].to_dict()
        if user['password'] == password:
            session['username'] = username
            return redirect(url_for('forum'))
        else:
            return render_template('login.html', error="Senha incorreta")
    else:
        return render_template('login.html', error="Usuário não encontrado")

# Rota para o fórum principal
@app.route('/forum')
def forum():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Carrega todas as mensagens
    messages_ref = db.collection('messages').order_by('timestamp').get()
    messages = []
    for doc in messages_ref:
        message_data = doc.to_dict()
        message_id = doc.id

        messages.append({
            'text': message_data.get('text', 'Mensagem sem texto'),
            'topic': message_data.get('topic', 'Tópico sem título'),
            'username': '@' + message_data.get('username', 'Usuário desconhecido'),
            'image_url': message_data.get('image_url', None),
            'id': message_id
        })
    
    return render_template('forum.html', username=session['username'], messages=messages)

# Rota para enviar uma mensagem com opção de upload de imagem
@app.route('/send_message', methods=['POST'])
def send_message():
    if 'username' not in session:
        return redirect(url_for('login'))

    message_text = request.form['message']
    message_topic = request.form['topic']
    image_url = None

    # Verifica se uma imagem foi enviada
    if 'image' in request.files:
        image = request.files['image']
        if image and allowed_file(image.filename):
            # Gera um nome de arquivo único para evitar conflitos
            filename = secure_filename(image.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"

            # Faz o upload da imagem para o Firebase Storage
            blob = bucket.blob(unique_filename)
            blob.upload_from_file(image)
            blob.make_public()  # Torna a URL pública para acesso

            # Obtemos a URL pública da imagem
            image_url = blob.public_url

    # Armazena a mensagem no Firestore
    db.collection('messages').add({
        'text': message_text,
        'topic': message_topic,
        'username': session['username'],
        'image_url': image_url,
        'timestamp': firestore.SERVER_TIMESTAMP
    })

    return redirect(url_for('forum'))

# Rota para exibir a página da mensagem com seus comentários
@app.route('/post/<message_id>')
def view_post(message_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    # Carrega a mensagem principal
    message_ref = db.collection('messages').document(message_id).get()
    message_data = message_ref.to_dict()

    if not message_data:
        return "Mensagem não encontrada", 404

    # Carrega os comentários da mensagem
    comments_ref = db.collection('messages').document(message_id).collection('comments').order_by('timestamp').get()
    comments = [{'text': comment.to_dict().get('text'), 'username': '@' + comment.to_dict().get('username')} for comment in comments_ref]
    
    return render_template('post.html', message=message_data, comments=comments, message_id=message_id)

# Rota para enviar um comentário
@app.route('/send_comment/<message_id>', methods=['POST'])
def send_comment(message_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    comment_text = request.form.get('comment')

    # Armazena o comentário como uma subcoleção da mensagem
    db.collection('messages').document(message_id).collection('comments').add({
        'text': comment_text,
        'username': session['username'],
        'timestamp': firestore.SERVER_TIMESTAMP
    })

    return redirect(url_for('view_post', message_id=message_id))

# Rota para solicitar acesso
@app.route('/request_access', methods=['GET', 'POST'])
def request_access():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        # Salvar os dados no Firestore na coleção "solicitações"
        db.collection('solicitações').add({
            'name': name,
            'email': email
        })

        return redirect(url_for('login'))

    return render_template('request_access.html')

# Rota para logout
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove o usuário da sessão
    return redirect(url_for('login'))

# Iniciando o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
