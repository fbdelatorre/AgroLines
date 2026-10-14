"""Stage only approved static privacy HTML; never regenerate the legal text."""

import argparse
import hashlib
import re
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "docs/privacy/offline"
PUBLIC_URL = "https://fbdelatorre.github.io/AgroLines/privacidade/"
PUBLIC_FILES = {".nojekyll", "privacidade/index.html"}


def sha256(content):
    return hashlib.sha256(content).hexdigest()


def reject_pending(text):
    normalized = unicodedata.normalize("NFC", text).upper()
    compact = re.sub(r"\s+", "", normalized)
    if any(
        marker in compact
        for marker in (
            "[CONFIRMAR",
            "[PREENCHER",
            "[DECIDIR",
            "NÃOPUBLICAR",
            "NAOPUBLICAR",
        )
    ):
        raise ValueError("Política incompleta: confirmação/revisão pendente; publicação bloqueada")


class StaticPolicy(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.ids = set()
        self.links = []
        self.viewport = False
        self.portuguese = False
        self.in_style = False

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag in {"script", "iframe", "object", "embed", "form", "link", "base", "img"}:
            raise ValueError("A política pública deve ser HTML estático sem recursos adicionais")
        if any(name.startswith("on") or name in {"src", "srcset"} for name in attrs):
            raise ValueError("Recursos ou eventos ativos não são permitidos")
        if tag == "meta" and "http-equiv" in attrs:
            raise ValueError("Redirecionamento ou comportamento ativo não permitido")
        if "style" in attrs:
            self.check_css(attrs["style"])
        if tag == "html":
            self.portuguese = attrs.get("lang", "").lower() == "pt-br"
        if tag == "meta" and attrs.get("name") == "viewport":
            self.viewport = "width=device-width" in attrs.get("content", "")
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])
        if tag == "style":
            self.in_style = True

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False

    @staticmethod
    def check_css(css):
        if re.search(r"url\s*\(|@import|\\", css, flags=re.I):
            raise ValueError("CSS não pode carregar recursos externos")

    def handle_data(self, data):
        if self.in_style:
            self.check_css(data)
        else:
            self.text.append(data)

    def validate(self):
        reject_pending("".join(self.text))
        if not self.portuguese or not self.viewport:
            raise ValueError("HTML deve declarar pt-BR e viewport responsivo")
        for link in self.links:
            target = urlsplit(urljoin(PUBLIC_URL, link))
            if target.scheme != "https" or target.username or target.password:
                raise ValueError("Links web devem usar HTTPS sem credenciais")
            if target.hostname == urlsplit(PUBLIC_URL).hostname:
                if target.path not in {
                    urlsplit(PUBLIC_URL).path,
                    urlsplit(PUBLIC_URL).path + "index.html",
                }:
                    raise ValueError("Link interno aponta para arquivo fora da política pública")
                if target.fragment and unquote(target.fragment) not in self.ids:
                    raise ValueError("Âncora interna não existe no HTML")


def approved_html(source, expected_sha256):
    source = Path(source)
    html_path = source / "politica-privacidade.html"
    markdown = source / "politica-privacidade.md"
    if html_path.is_symlink() or markdown.is_symlink():
        raise ValueError("Arquivos de política não podem ser links simbólicos")
    content = html_path.read_bytes()
    reject_pending(markdown.read_text(encoding="utf-8"))
    text = content.decode("utf-8")
    reject_pending(text)
    page = StaticPolicy()
    page.feed(text)
    page.close()
    page.validate()
    if not re.fullmatch(r"[a-fA-F0-9]{64}", expected_sha256):
        raise ValueError("Informe o SHA-256 do HTML efetivamente revisado e aprovado")
    if sha256(content) != expected_sha256.lower():
        raise ValueError("O HTML difere da revisão aprovada; publicação bloqueada")
    return content


def stage(source, output, expected_sha256):
    content = approved_html(source, expected_sha256)
    output = Path(output)
    # Never reuse a directory that could contain stale code, data or internal documents.
    output.mkdir(parents=True, exist_ok=False)
    (output / "privacidade").mkdir()
    (output / "privacidade/index.html").write_bytes(content)
    (output / ".nojekyll").touch()
    actual = {p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file()}
    if actual != PUBLIC_FILES or any(p.is_symlink() for p in output.rglob("*")):
        raise ValueError("Artefato público contém arquivos não autorizados")
    return sha256(content)


def verify_public(expected_sha256):
    # Default TLS certificate/hostname verification; no account, cookies or tokens.
    request = Request(PUBLIC_URL, headers={"Cache-Control": "no-cache"})
    with urlopen(request, timeout=30) as response:
        if response.status != 200 or response.geturl() != PUBLIC_URL:
            raise ValueError("URL pública não respondeu HTTP 200 no endereço HTTPS esperado")
        if "text/html" not in response.headers.get("Content-Type", ""):
            raise ValueError("Resposta pública não é HTML")
        content = response.read(2_000_001)
    if len(content) > 2_000_000 or sha256(content) != expected_sha256.lower():
        raise ValueError("Página pública não corresponde ao HTML aprovado")
    parser = StaticPolicy()
    parser.feed(content.decode("utf-8"))
    parser.close()
    parser.validate()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build/privacy-site")
    parser.add_argument("--approved-sha256", required=True)
    parser.add_argument("--verify-public", action="store_true")
    args = parser.parse_args()
    if args.verify_public:
        approved_html(SOURCE, args.approved_sha256)
        verify_public(args.approved_sha256)
        print("HTTPS/HTTP 200/sem login/HTML aprovado/links internos: verificados")
    else:
        digest = stage(SOURCE, args.output, args.approved_sha256)
        print(f"Somente privacidade/index.html e .nojekyll; SHA-256: {digest}")


if __name__ == "__main__":
    main()
