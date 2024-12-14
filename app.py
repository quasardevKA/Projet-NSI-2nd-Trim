from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import uuid
import os
import base64
import hashlib
from email_utils import send_password_reset_email, send_otp_email, generate_otp
import requests
import ssl
from datetime import datetime
from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine, select
from SQLClassDB import User, Report, FriendRequest, Conversation, Contact


app = Flask(__name__)
CORS(app, resources={"/*": {"origins": "https://whatsupp.aekio.fr"}})
app.secret_key = os.urandom(24)  # Génération d'une clé secrète aléatoire
socketio = SocketIO(app, cors_allowed_origins="*")
engine = create_engine("sqlite:///db.sqlite")

@app.before_request
def before_request():
    try:
        # Essayez de lire l'en-tête de la requête
        request.headers.get('User-Agent')
    except ssl.SSLError:
        # Si une erreur SSL est détectée, renvoyer une erreur 400
        abort(400)

def get_db_connection():
    conn = sqlite3.connect('db.sqlite', timeout=10)  # Augmentez le timeout à 10 secondes
    conn.row_factory = sqlite3.Row
    return conn

def generate_session_cookie():
    return hashlib.sha256(os.urandom(24)).hexdigest()

def get_users_info(user1_id, user2_id):
    query = '''
        SELECT 
            id, 
            username, 
            first_name, 
            last_name, 
            profile_image
        FROM 
            users
        WHERE 
            id IN (?, ?)
    '''
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (user1_id, user2_id))
        users = cursor.fetchall()

    if len(users) != 2:
        return None

    user_info = {'user_requester_info': {}, 'user_contact_info': {}}
    for user in users:
        if user['id'] == user1_id:
            user_info['user_requester_info'] = dict(user)
        else:
            user_info['user_contact_info'] = dict(user)
            
    return user_info

def search_user_in_table(table, selector, variable):
    if(selector):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM ' + str(table) + ' WHERE ' + str(selector) + ' = ?', (variable,))
            result = cursor.fetchone()
            return result
    else:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM ')
            result = cursor.fetchone()
            return result
    
def update_var_in_table(table, selector, selector_var, updated, updated_var):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE ' + str(table) + ' SET ' + str(updated) + ' = ? WHERE ' + str(selector) + ' = ?', (updated_var, selector_var))
        conn.commit()


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form['password-confirm']

        if password != password_confirm:
            error_message = "Les mots de passe ne correspondent pas."
            return render_template('register/signup.html', error=error_message)

        hashed_password = generate_password_hash(password)
        otp = generate_otp()  # Génération d'un code OTP

        try:
            user_id = str(uuid.uuid4())  # Génération d'un UUID
            session_cookie = generate_session_cookie()  # Génération d'un cookie de session
            image_url = 'https://ui-avatars.com/api/?size=1000&name='+str(first_name)
            # Récupérer l'image depuis l'URL
            response = requests.get(image_url)
            image_base64 = ""
            # Vérifier si la requête a réussi
            if response.status_code == 200:
                # Encoder l'image en base64
                image_base64 = base64.b64encode(response.content).decode('utf-8')
            else:
                raise Exception(f"Erreur lors de la récupération de l'image: {response.status_code}")

            # URL de l'imag

            # Appeler la fonction et afficher le résultat

            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (id, first_name, last_name, username, email, password_hash, otp, admin, session_cookie, profile_image)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
                ''', (user_id, first_name, last_name, username, email, hashed_password, otp, session_cookie, image_base64))
                conn.commit()
            send_otp_email(email, otp) 

            response = make_response(redirect(url_for('dashboard')))
            response.set_cookie('session_cookie', session_cookie)
            session['user_id'] = user_id
            session['admin'] = False
            return response
        except sqlite3.IntegrityError:
            error_message = "Ce nom d'utilisateur ou cette adresse e-mail est déjà utilisé."
            return render_template('register/signup.html', error=error_message)
        except sqlite3.OperationalError as e:
            error_message = f"Erreur de base de données : {str(e)}"
            return render_template('register/signup.html', error=error_message)

    return render_template('register/signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    session_cookie = request.cookies.get('session_cookie')

    if session_cookie:
        user = search_user_in_table('users', 'session_cookie', session_cookie)

        if user:
            return redirect(url_for('dashboard'))
        else:
            response = make_response(redirect(url_for('login')))
            response.set_cookie('session_cookie', '', expires=0)
            return response

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = search_user_in_table('users', 'username', username)

        if user and check_password_hash(user['password_hash'], password):
            session_cookie = generate_session_cookie()

            update_var_in_table("users", "id", user['id'], "session_cookie", session_cookie)
            
            response = make_response(redirect(url_for('dashboard')))
            response.set_cookie('session_cookie', session_cookie)
            session['user_id'] = user['id']
            session['admin'] = user['admin']
            return response
        else:
            error_message = "Nom d'utilisateur ou mot de passe incorrect."
            return render_template('login/login.html', error=error_message)

    return render_template('login/login.html')


@app.route('/dashboard/', defaults={'contact_id': None})
@app.route('/dashboard/<contact_id>/')
def dashboard(contact_id):
    session_cookie = request.cookies.get('session_cookie')

    if not session_cookie:
        app.logger.error('Session cookie is not present.')
        return redirect(url_for('login'))

    user = search_user_in_table('users', 'session_cookie', session_cookie)

    if not user:
        app.logger.error('User with the given session cookie not found.')
        response = make_response(redirect(url_for('login')))
        response.set_cookie('session_cookie', '', expires=0)
        return response

    user_content = dict(user)
    is_user_admin = user_content.get('admin')

    # Vérifier si l'utilisateur a des contacts
    user_contacts = search_user_in_table('contacts', 'user_id', user_content['id'])

    if user_contacts and not contact_id:
        # Si l'utilisateur a des contacts et qu'aucun contact_id n'est fourni, rediriger vers le premier contact
        first_contact_id = user_contacts[0]['contact_id']
        return redirect(url_for('dashboard', contact_id=first_contact_id))

    contact_user_dict = None

    if contact_id:
        contact_user = search_user_in_table('users', 'id', contact_id)

        if not contact_user:
            app.logger.error('Contact user not found.')
            return render_template('page_not_found/404.html'), 404

        contact_user_dict = dict(contact_user)

    user_list_contacts = [dict(contact) for contact in user_contacts]
    has_contacts = bool(user_list_contacts)

    return render_template('dashboard/dashboard.html', user=user_content, user_conv=contact_user_dict, user_list_contacts=user_list_contacts, message="Vous êtes connecté", has_contacts=has_contacts, is_admin=is_user_admin)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']

        user = search_user_in_table('users', 'email', email)

        if user:
            send_password_reset_email(email)  # Envoi de l'email de réinitialisation
            flash("Un e-mail de réinitialisation de mot de passe a été envoyé.", "info")
            return redirect(url_for('login'))
        else:
            error_message = "Aucun utilisateur trouvé avec cette adresse e-mail."
            return render_template('reset_password/index.html', error=error_message)

    return render_template('mdp_oublier/index.html')

@app.route('/admin', methods=['GET'])
def admin():
    session_cookie = request.cookies.get('session_cookie')

    if not session_cookie:
        return redirect(url_for('login'))

    user = search_user_in_table('users', 'session_cookie', session_cookie)
        

    if not user or not user['admin']:
        return redirect(url_for('login'))
    
    users = search_user_in_table('users')
    return render_template('admin/index.html', users=users)


@app.route('/reports', methods=['GET'])
def reports():
    session_cookie = request.cookies.get('session_cookie')

    if not session_cookie:
        return redirect(url_for('login'))

    user = search_user_in_table('users', 'session_cookie', session_cookie)

    users_not = search_user_in_table('users', 'session_cookie', session_cookie)
    users = users_list = [dict(user) for user in users_not]

    if not user or not user['admin']:
        return redirect(url_for('login'))
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT reports.*, u1.first_name AS reported_first_name, u1.last_name AS reported_last_name, 
                   u2.first_name AS reporter_first_name, u2.last_name AS reporter_last_name 
            FROM reports
            JOIN users u1 ON reports.reported_user_id = u1.id
            JOIN users u2 ON reports.reporter_user_id = u2.id
        ''')
        reports = cursor.fetchall()
    
    reports_list = [dict(report) for report in reports]
    
    return render_template('gestion_signalement/gestion_signalement.html', users=reports_list)


@app.route('/get_messages/<contact_id>', methods=['GET'])
def get_messages(contact_id):
    session_cookie = request.cookies.get('session_cookie')

    if not session_cookie:
        return jsonify({'error': 'Session non valide'}), 401

    user = search_user_in_table('users', 'session_cookie', session_cookie)

    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404

    user_id = user['id']

    messages = get_messages_between_users(user_id, contact_id)
    users_info = get_users_info(user_id, contact_id)

    if not users_info:
        return jsonify({'error': 'Un ou les deux utilisateurs sont introuvables'}), 404

    return jsonify({'messages': messages, 'users_info': users_info})


def get_messages_between_users(user1_id, user2_id):
    query = '''
        SELECT 
            id, 
            user_id AS sender_id, 
            last_message AS message, 
            publish_at AS send_time,
            contact_id AS recipient_id
        FROM 
            conversations
        WHERE 
            (user_id = ? AND contact_id = ?)
            OR 
            (user_id = ? AND contact_id = ?)
        ORDER BY 
            publish_at ASC
        LIMIT 50;
    '''
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (user1_id, user2_id, user2_id, user1_id))
        messages = cursor.fetchall()

    messages_list = [dict(message) for message in messages]
    return messages_list


@app.route('/update_user/<user_id>', methods=['POST'])
def update_user(user_id):
    session_cookie = request.cookies.get('session_cookie')

    if not session_cookie:
        return redirect(url_for('login'))

    user = search_user_in_table('users', 'session_cookie', session_cookie)

    if not user or not user['admin']:
        return redirect(url_for('login'))

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    username = request.form['username']
    email = request.form['email']
    admin = bool(int(request.form['admin']))

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users 
            SET first_name = ?, last_name = ?, username = ?, email = ?, admin = ?
            WHERE id = ?
        ''', (first_name, last_name, username, email, admin, user_id))
        conn.commit()

    return redirect(url_for('admin'))

@app.route('/delete_user/<user_id>', methods=['POST'])
def delete_user(user_id):
    session_cookie = request.cookies.get('session_cookie')

    if not session_cookie:
        return redirect(url_for('login'))

    user = search_user_in_table('users', 'session_cookie', session_cookie)

    if not user or not user['admin']:
        return redirect(url_for('login'))

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()

    return redirect(url_for('admin'))

@app.route('/new_user_conv', methods=['POST'])
def search_user():
    data = request.get_json()
    username = data.get('username')

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

    if user:
        return jsonify({'uuid': user['id']})
    else:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    


@app.route('/search_users', methods=['GET'])
def search_users():
    session_cookie = request.cookies.get('session_cookie')

    if not session_cookie:
        return jsonify({'error': 'Session non valide'}), 401

    query = request.args.get('query', '')

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE session_cookie = ?', (session_cookie,))
        user = cursor.fetchone()

    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404

    user_id = user['id']

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, first_name, last_name, profile_image 
            FROM users
            WHERE username LIKE ? AND id != ?
            LIMIT 10
        ''', (query + '%', user_id))
        users = cursor.fetchall()

    user_list = [
        {
            'id': user['id'],
            'username': user['username'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'profile_image': user['profile_image']
        }
        for user in users
    ]
    return jsonify(user_list)


@app.route('/send_friend_request', methods=['POST'])
def send_friend_request():
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    session_cookie = request.cookies.get('session_cookie')

    if not session_cookie:
        return jsonify({'error': 'Session non valide'}), 401

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, first_name, last_name, profile_image FROM users WHERE session_cookie = ?', (session_cookie,))
        requester = cursor.fetchone()

        if not requester:
            return jsonify({'error': 'Utilisateur demandeur introuvable'}), 404

        requester_id = requester['id']
        requester_username = requester['username']
        requester_first_name = requester['first_name']
        requester_last_name = requester['last_name']
        profile_image = requester['profile_image']

        # Vérifier s'il existe déjà une demande d'ami
        cursor.execute('''
            SELECT * FROM friend_requests
            WHERE requester_id = ? AND receiver_id = ?
        ''', (requester_id, receiver_id))
        existing_request = cursor.fetchone()

        if existing_request:
            return jsonify({'error': 'Une demande d\'ami existe déjà'}), 409

        cursor.execute('''
            INSERT INTO friend_requests (requester_id, receiver_id, requester_first_name, requester_last_name)
            VALUES (?, ?, ?, ?)
        ''', (requester_id, receiver_id, requester_first_name, requester_last_name))
        conn.commit()

        cursor.execute('''
            SELECT * FROM friend_requests
            WHERE requester_id = ? AND receiver_id = ?
        ''', (requester_id, receiver_id))
        get_id_request = cursor.fetchone()
        request_id = get_id_request['request_id']

        # Notifie l'utilisateur cible via WebSocket
        socketio.emit('friend_request', {'requester_id': requester_id, 'receiver_id': receiver_id,'requester_username': requester_username,'profile_image': profile_image, 'requester_first_name': requester_first_name, 'request_id': request_id, 'requester_last_name': requester_last_name}, room=receiver_id)

    return jsonify({'message': 'Demande d\'ami envoyée avec succès'}), 201




@app.route('/friend_requests')
def friend_requests():
    session_cookie = request.cookies.get('session_cookie')

    if not session_cookie:
        return redirect(url_for('login'))

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE session_cookie = ?', (session_cookie,))
        user = cursor.fetchone()

    if not user:
        return redirect(url_for('login'))

    user_id = user['id']

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT request_id, requester_id, requester_first_name, requester_last_name, profile_image
            FROM friend_requests
            JOIN users ON friend_requests.requester_id = users.id
            WHERE receiver_id = ?
        ''', (user_id,))
        friend_requests = cursor.fetchall()
        rows_as_dicts = [dict(row) for row in friend_requests] # Afficher le dictionnaire complet 

    requests_list = [dict(request) for request in friend_requests]
    return jsonify(requests_list)


@app.route('/accept_friend_request', methods=['POST'])
def accept_friend_request():
    data = request.get_json()
    request_id = data.get('request_id')
    session_cookie = request.cookies.get('session_cookie')

    if not session_cookie:
        return jsonify({'error': 'Session non valide'}), 401

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE session_cookie = ?', (session_cookie,))
        user = cursor.fetchone()

    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404

    user_id = user['id']

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM friend_requests WHERE request_id = ?', (request_id,))
        friend_request = cursor.fetchone()

    if not friend_request or friend_request['receiver_id'] != user_id:
        return jsonify({'error': 'Demande d\'ami introuvable ou non autorisée'}), 404

    requester_id = friend_request['requester_id']

    # Insérer les amis dans la table contacts
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO contacts (user_id, contact_id, last_message, last_message_date, unread_messages_count) VALUES (?, ?, ?, ?, ?)', 
                       (user_id, requester_id, None, None, 0))
        cursor.execute('INSERT INTO contacts (user_id, contact_id, last_message, last_message_date, unread_messages_count) VALUES (?, ?, ?, ?, ?)', 
                       (requester_id, user_id, None, None, 0))

        # Supprimer la demande d'ami acceptée
        cursor.execute('DELETE FROM friend_requests WHERE request_id = ?', (request_id,))
        conn.commit()

    # Supprimer la demande d'ami de la liste d'ajout des amis
    socketio.emit('remove_friend_request', {'request_id': request_id}, room=user_id)

    return jsonify({'message': 'Demande d\'ami acceptée et ajoutée aux contacts'}), 201


@app.route('/user_contacts', methods=['GET'])
def user_contacts():
    session_cookie = request.cookies.get('session_cookie')

    if not session_cookie:
        return jsonify({'error': 'Session non valide'}), 401

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE session_cookie = ?', (session_cookie,))
        user = cursor.fetchone()

    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404

    user_id = user['id']

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT contacts.*, users.first_name, users.last_name, users.profile_image 
            FROM contacts
            JOIN users ON contacts.contact_id = users.id
            WHERE contacts.user_id = ?
        ''', (user_id,))
        contacts = cursor.fetchall()

    contacts_list = [dict(contact) for contact in contacts]
    return jsonify(contacts_list)


@socketio.on('connect')
def handle_connect():
    session_cookie = request.cookies.get('session_cookie')

    if session_cookie:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE session_cookie = ?', (session_cookie,))
            user = cursor.fetchone()

        if user:
            user_id = user['id']
            join_room(user_id)

@app.route('/user_conversations', methods=['GET'])
def user_conversations():
    session_cookie = request.cookies.get('session_cookie')

    if not session_cookie:
        return jsonify({'error': 'Session non valide'}), 401

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE session_cookie = ?', (session_cookie,))
        user = cursor.fetchone()

    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404

    user_id = user['id']

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT conversations.*, users.first_name, users.last_name 
            FROM conversations
            JOIN users ON conversations.contact_id = users.id
            WHERE conversations.user_id = ?
        ''', (user_id,))
        conversations = cursor.fetchall()

    conversations_list = [dict(conversation) for conversation in conversations]
    return jsonify(conversations_list)

@app.route('/report_user', methods=['POST'])
def report_user():
    data = request.get_json()
    reported_user_id = data.get('reported_user_id')
    reason = data.get('reason')
    session_cookie = request.cookies.get('session_cookie')

    if not session_cookie:
        return jsonify({'error': 'Session non valide'}), 401

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE session_cookie = ?', (session_cookie,))
        user = cursor.fetchone()

    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404

    reporter_user_id = user['id']
    cursor.execute('INSERT INTO reports (reported_user_id, reporter_user_id, reason) VALUES (?, ?, ?)', 
                   (reported_user_id, reporter_user_id, reason))
    conn.commit()

    return jsonify({'message': 'Utilisateur signalé avec succès'})

@app.route('/logout', methods=['POST'])
def logout():
    response = make_response(redirect(url_for('login')))
    response.set_cookie('session_cookie', '', expires=0)
    return response

@app.route('/send_message', methods=['POST'])
def send_message():
    session_cookie = request.cookies.get('session_cookie')
    data = request.get_json()
    contact_id = data.get('contact_id')
    message_content = data.get('message')

    if not session_cookie:
        return jsonify({'error': 'Session non valide'}), 401

    if not contact_id or not message_content:
        return jsonify({'error': 'Contact ID et message requis'}), 400

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE session_cookie = ?', (session_cookie,))
        user = cursor.fetchone()

    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404

    user_id = user['id']

    # Insérer le message dans la table conversations
    from datetime import datetime

    # datetime object containing current date and time
    now = datetime.now()
    
    print("now =", now)

    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print("date and time =", dt_string)
    message_id = str(uuid.uuid4())  # Générer un identifiant unique pour le message
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (id, user_id, contact_id, last_message, publish_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (message_id, user_id, contact_id, message_content, dt_string))
        conn.commit()

    # Envoyer le message via WebSocket
    socketio.emit('receive_message', {
        'id': message_id,
        'sender_id': user_id,
        'message': message_content,
        'send_time': datetime.utcnow().isoformat() + 'Z',
        'to': contact_id
    }, room=contact_id)

    return jsonify({'success': True, 'message_id': message_id})

@socketio.on('send_message')
def handle_send_message(data):
    socketio.emit('receive_message', data, room=data['contact_id'])

@socketio.on('typing')
def handle_typing(data):
    socketio.emit('typing', data, room=data['to'])

@socketio.on('stop_typing')
def handle_stop_typing(data):
    socketio.emit('stop_typing', data, room=data['to'])

@app.route('/get_user_id', methods=['GET'])
def get_user_id():
    session_cookie = request.cookies.get('session_cookie')

    if not session_cookie:
        return jsonify({'error': 'Session non valide'}), 401

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE session_cookie = ?', (session_cookie,))
        user = cursor.fetchone()

    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404

    return jsonify({'user_id': user['id']})


@app.errorhandler(404)
def page_not_found(e):
    return render_template('page_not_found/404.html'), 404

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8098, debug=True)

