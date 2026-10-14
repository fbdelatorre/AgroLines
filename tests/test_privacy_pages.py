import pytest

from scripts.prepare_privacy_pages import PUBLIC_FILES, SOURCE, approved_html, sha256, stage


def fixture_source(tmp_path, body='<h1 id="politica">Política sintética de teste</h1>'):
    source = tmp_path / "source"
    source.mkdir()
    source.joinpath("politica-privacidade.md").write_text(
        "Texto sintético aprovado", encoding="utf-8"
    )
    html = (
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "</head><body>" + body + "</body></html>"
    ).encode()
    source.joinpath("politica-privacidade.html").write_bytes(html)
    return source, html


def test_repository_html_with_pending_marker_cannot_create_public_artifact(tmp_path):
    content = (SOURCE / "politica-privacidade.html").read_bytes()
    content += b"<!-- [CONFIRMAR: synthetic release blocker] -->"
    source = tmp_path / "source"
    source.mkdir()
    (source / "politica-privacidade.html").write_bytes(content)
    (source / "politica-privacidade.md").write_bytes(
        (SOURCE / "politica-privacidade.md").read_bytes()
    )
    with pytest.raises(ValueError, match="incompleta"):
        stage(source, tmp_path / "site", sha256(content))
    assert not (tmp_path / "site").exists()


def test_artifact_contains_only_unchanged_approved_html(tmp_path):
    source, content = fixture_source(tmp_path)
    # Documents, databases, source, keys and stale generated files must never be copied.
    for name in ("secret.key", "private.sqlite", "internal.md", "client.py", "farm.agrolines"):
        source.joinpath(name).write_text("synthetic excluded fixture")
    before = {p.name: p.read_bytes() for p in source.iterdir()}
    output = tmp_path / "site"
    stage(source, output, sha256(content))
    assert {
        p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file()
    } == PUBLIC_FILES
    assert output.joinpath("privacidade/index.html").read_bytes() == content
    assert before == {p.name: p.read_bytes() for p in source.iterdir()}


@pytest.mark.parametrize(
    "body",
    [
        "<p>[CONFIRMAR: revisão]</p>",
        "<p>[con<span>firmar</span>: revisão]</p>",
        "<p>&#91;CONFIRMAR: revisão]</p>",
        "<p>NÃO PUBLICAR</p>",
        "<p>[PREENCHER: data]</p>",
        '<script>alert("active")</script>',
        '<img src="https://example.com/pixel">',
        '<p onclick="alert(1)">active</p>',
        "<style>body{background:url(https://example.com/pixel)}</style>",
        '<a href="#missing">âncora ausente</a>',
        '<a href="../private.md">documento interno</a>',
        '<a href="http://example.com">HTTP</a>',
    ],
)
def test_pending_active_content_and_broken_links_block_upload(tmp_path, body):
    source, content = fixture_source(tmp_path, body)
    with pytest.raises(ValueError):
        stage(source, tmp_path / "site", sha256(content))
    assert not (tmp_path / "site").exists()


def test_review_hash_is_bound_to_bytes_and_stale_directory_is_rejected(tmp_path):
    source, content = fixture_source(tmp_path)
    with pytest.raises(ValueError, match="difere"):
        approved_html(source, "0" * 64)
    output = tmp_path / "site"
    output.mkdir()
    stale = output / "private.key"
    stale.write_text("synthetic stale fixture")
    with pytest.raises(FileExistsError):
        stage(source, output, sha256(content))
    assert stale.exists()


def test_internal_anchor_and_https_links_are_valid(tmp_path):
    source, content = fixture_source(
        tmp_path,
        '<h1 id="politica">Política</h1>'
        '<a href="#politica">Início</a>'
        '<a href="https://example.com/privacy">Fonte externa</a>',
    )
    assert approved_html(source, sha256(content)) == content


def test_public_verification_uses_anonymous_tls_request(monkeypatch, tmp_path):
    from scripts import prepare_privacy_pages as pages

    source, content = fixture_source(tmp_path)

    class Response:
        status = 200
        headers = {"Content-Type": "text/html; charset=utf-8"}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def geturl(self):
            return pages.PUBLIC_URL

        def read(self, size):
            return content[:size]

    def open_public(request, timeout):
        assert request.full_url == pages.PUBLIC_URL
        assert request.full_url.startswith("https://")
        assert not request.has_header("Authorization") and not request.has_header("Cookie")
        assert timeout == 30
        return Response()

    monkeypatch.setattr(pages, "urlopen", open_public)
    pages.verify_public(sha256(content))
    with pytest.raises(ValueError, match="não corresponde"):
        pages.verify_public("0" * 64)
