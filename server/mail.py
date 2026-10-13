import smtplib
import ssl
from email.message import EmailMessage


def send_recovery(settings, email: str, token: str):
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = email
    message["Subject"] = "AgroLines — recuperação de senha"
    message.set_content(
        "Use este código na tela Recuperar senha do AgroLines. Válido por 15 minutos.\n"
        f"{token}\nSe não solicitou, ignore esta mensagem."
    )
    # TLS required, certificate and hostname validation remain enabled.
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
        smtp.ehlo()
        smtp.starttls(context=ssl.create_default_context())
        smtp.ehlo()
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_password.get_secret_value())
        smtp.send_message(message)
