import ssl

from pydantic import SecretStr

from server.config import Settings
from server.mail import send_recovery


def test_recovery_transport_requires_verified_tls(monkeypatch):
    calls = []

    class SMTP:
        def __init__(self, host, port, timeout):
            assert (host, port, timeout) == ("smtp.example.com", 587, 10)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def ehlo(self):
            calls.append("ehlo")

        def starttls(self, context):
            assert context.check_hostname
            assert context.verify_mode == ssl.CERT_REQUIRED
            calls.append("tls")

        def login(self, username, password):
            assert username == "synthetic-user"
            assert password == "synthetic-smtp-password"
            assert "tls" in calls
            calls.append("login")

        def send_message(self, message):
            assert message["To"] == "recipient@example.com"
            assert "synthetic-reset-token" in message.get_content()
            assert "login" in calls
            calls.append("send")

    monkeypatch.setattr("server.mail.smtplib.SMTP", SMTP)
    send_recovery(
        Settings(
            smtp_host="smtp.example.com",
            smtp_username="synthetic-user",
            smtp_password=SecretStr("synthetic-smtp-password"),
        ),
        "recipient@example.com",
        "synthetic-reset-token",
    )
    assert calls == ["ehlo", "tls", "ehlo", "login", "send"]
