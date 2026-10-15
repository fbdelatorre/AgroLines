"""HTTPS verification on by default; no redirects, proxies or arbitrary destinations."""

import json
import ssl
import urllib.error
import urllib.request

from core.license_network import licensing_connection, validate_origin


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise OSError("Redirecionamento do serviço de licenças recusado.")


def tls_context(lab_ca_pem=None, *, test_profile=False):
    if lab_ca_pem is None:
        return ssl.create_default_context()
    if not test_profile:
        raise ValueError("Laboratory TLS trust is forbidden in production")
    # Trust only this public laboratory CA in this process. Never change Windows roots.
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_verify_locations(cadata=lab_ca_pem)
    return context


class LicenseTransport:
    def __init__(self, origin, timeout=5, *, lab_ca_pem=None, test_profile=False):
        self.origin = validate_origin(origin)
        self.timeout = timeout
        self.opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            NoRedirect(),
            urllib.request.HTTPSHandler(context=tls_context(lab_ca_pem, test_profile=test_profile)),
        )

    def post(self, operation, value):
        if operation not in ("activate", "check", "deactivate"):
            raise ValueError("Operação de licenciamento inválida.")
        data = json.dumps(value, allow_nan=False).encode()
        if len(data) > 12000:
            raise ValueError("Dados de ativação excedem o limite.")
        request = urllib.request.Request(
            self.origin + "/v1/" + operation,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        try:
            with (
                licensing_connection(self.origin),
                self.opener.open(request, timeout=self.timeout) as reply,
            ):
                if reply.url != request.full_url:
                    raise OSError("Origem da resposta divergente.")
                data = reply.read(32769)
                if len(data) > 32768:
                    raise OSError("Resposta do serviço excede o limite.")
                result = json.loads(data)
                if not isinstance(result, dict):
                    raise ValueError("Resposta inválida.")
                return result
        except urllib.error.HTTPError as exc:
            # Never reflect arbitrary server/proxy HTML or include submitted credentials in logs.
            messages = {
                403: "Chave inválida, titular divergente ou assinatura vencida.",
                409: "Vaga já utilizada. Solicite a substituição do computador.",
                429: "Muitas tentativas. Aguarde antes de tentar novamente.",
            }
            raise OSError(messages.get(exc.code, "Serviço de licenciamento indisponível.")) from exc
