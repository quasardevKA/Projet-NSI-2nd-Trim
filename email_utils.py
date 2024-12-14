import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

def send_email(subject, recipient, body):
    sender_email = "krahuel@immacjp2.fr"
    sender_password = "Leju8369"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.office365.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, msg.as_string())
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")
        return False

def generate_otp():
    return random.randint(100000, 999999)

def send_password_reset_email(recipient):
    subject = "Réinitialisation de votre mot de passe"
    body = f"Bonjour,\n\nVeuillez cliquer sur le lien suivant pour réinitialiser votre mot de passe : [Lien de réinitialisation]\n\nCordialement,\nVotre équipe."
    return send_email(subject, recipient, body)

def send_otp_email(recipient, otp):
    subject = "Code de vérification"
    body = f"Bonjour,\n\nVotre code de vérification est : {otp}\n\nCordialement,\nVotre équipe."
    return send_email(subject, recipient, body)
