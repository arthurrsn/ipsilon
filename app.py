from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore, storage

app = Flask(__name__)
app.secret_key = 'calwdawdasnmdu23g238sdyhawdmbausd77d8u089gjkfgkjvbfvb'  # Para gerenciar as sessões

# Inicializando o Firebase
cred = credentials.Certificate('firebase_config.json')  # Arquivo JSON de chave do Firebase
firebase_admin.initialize_app(cred, {
    'storageBucket': 'seu-projeto.appspot.com'  # Substitua pelo nome do seu bucket
})
db = firestore.client()
bucket = storage.bucket()

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
            # Verifica se o usuário já aceitou os termos
            if user.get('accepted_terms', 'no') == 'no':
                return redirect(url_for('accept_terms'))
            return redirect(url_for('forum'))
        else:
            return render_template('login.html', error="Senha incorreta")
    else:
        return render_template('login.html', error="Usuário não encontrado")

# Rota para aceitar os termos
@app.route('/accept_terms', methods=['GET', 'POST'])
def accept_terms():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Atualiza o status do usuário para "termos aceitos"
        username = session['username']
        users_ref = db.collection('users')
        query = users_ref.where('username', '==', username).get()

        if query:
            user_id = query[0].id
            users_ref.document(user_id).update({'accepted_terms': 'yes'})
            return redirect(url_for('forum'))

    return render_template('accept_terms.html')

# Rota para o fórum principal
@app.route('/forum')
def forum():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Carrega todas as mensagens (em ordem decrescente, mais recente primeiro)
    messages_ref = db.collection('messages').order_by('timestamp', direction=firestore.Query.DESCENDING).get()
    messages = []
    for doc in messages_ref:
        message_data = doc.to_dict()
        message_id = doc.id

        messages.append({
            'text': message_data.get('text', 'Mensagem sem texto'),
            'topic': message_data.get('topic', 'Tópico sem título'),
            'username': '@' + message_data.get('username', 'Usuário desconhecido'),
            'id': message_id,
            'image_url': message_data.get('image_url')  # Exibe a imagem, se existir
        })

    return render_template('forum.html', username=session['username'], messages=messages)

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

# Rota para enviar uma mensagem
@app.route('/send_message', methods=['POST'])
def send_message():
    if 'username' not in session:
        return redirect(url_for('login'))

    message_text = request.form['message']
    message_topic = request.form['topic']  # Obtemos o tópico

    # Armazena a mensagem no Firestore
    db.collection('messages').add({
        'text': message_text,
        'topic': message_topic,  # Adicionamos o tópico
        'username': session['username'],
        'timestamp': firestore.SERVER_TIMESTAMP
    })

    return redirect(url_for('forum'))

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

@app.route('/request_access', methods=['GET', 'POST'])
def request_access():
    if request.method == 'POST':
        # Obter os dados do formulário
        name = request.form['name']
        email = request.form['email']

        # Salvar os dados no Firestore na coleção "solicitações"
        db.collection('solicitações').add({
            'name': name,
            'email': email
        })

        # Redirecionar para a página de login
        return redirect(url_for('login'))  # Altere para o endpoint que você deseja

    # Para método GET, retorna o formulário de solicitação de acesso
    return render_template('request_access.html')

# Rota para logout
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove o usuário da sessão
    return redirect(url_for('login'))

# Iniciando o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
