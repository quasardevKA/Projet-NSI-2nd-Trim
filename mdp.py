from flask import Flask, render_template, request
from flask_mail import Mail, Message
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'

mail = Mail(app)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reset_password', methods=['POST'])
def reset_password():
    return render_template('index.html')

@socketio.on('send_email')
def handle_send_email(data):
    email = data['email']
    msg = Message('Réinitialisation de votre mot de passe', sender='your-email@example.com', recipients=[email])
    msg.body = 'Cliquez sur le lien pour réinitialiser votre mot de passe : http://example.com/reset'
    mail.send(msg)
    socketio.emit('email_sent', {'status': f'Email envoyé à {email}'})

if __name__ == '__main__':
    socketio.run(app)
