"""Private local browser check; does not stage/upload/deploy a pending policy."""

import argparse
import json
from pathlib import Path

from scripts.prepare_privacy_pages import ROOT, SOURCE, sha256


def check(output, executable=None):
    from playwright.sync_api import sync_playwright

    source = SOURCE / "politica-privacidade.html"
    digest = sha256(source.read_bytes())
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    results = []
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch(
            headless=True, executable_path=executable, chromium_sandbox=True
        )
        try:
            for width, height in ((320, 800), (390, 844), (768, 1024), (1366, 768), (1920, 1080)):
                context = browser.new_context(
                    viewport={"width": width, "height": height}, is_mobile=width < 600
                )
                page = context.new_page()
                external = []
                errors = []
                page.on("pageerror", lambda error, errors=errors: errors.append(str(error)))

                def restrict(route, external=external):
                    if route.request.url.startswith(("http:", "https:")):
                        external.append(route.request.url)
                        route.abort()
                    else:
                        route.continue_()

                context.route("**/*", restrict)
                page.goto(source.resolve().as_uri(), wait_until="load")
                dimensions = page.evaluate("""() => ({
                    viewport: window.innerWidth,
                    document: document.documentElement.scrollWidth,
                    headings: document.querySelectorAll('h2').length,
                    internalLinks: Array.from(document.querySelectorAll('a[href]'))
                        .filter(a => !a.getAttribute('href').startsWith('https:')).length
                })""")
                if dimensions["document"] > dimensions["viewport"] or errors or external:
                    raise ValueError("Overflow, erro JavaScript ou recurso externo na política")
                if page.locator("h1").count() != 1 or not dimensions["headings"]:
                    raise ValueError("Estrutura de títulos ausente")
                page.screenshot(path=str(output / f"privacy-{width}.png"), full_page=True)
                page.locator("h2").last.scroll_into_view_if_needed()
                results.append(
                    {
                        "width": width,
                        "height": height,
                        **dimensions,
                        "errors": errors,
                        "external_requests": external,
                    }
                )
                context.close()
        finally:
            browser.close()
    if sha256(source.read_bytes()) != digest:
        raise ValueError("HTML original foi alterado durante o teste")
    report = {
        "source_sha256": digest,
        "browser": "Chromium headless, sandbox ativo",
        "cases": results,
        "public_https_verified": False,
        "real_mobile_hardware_verified": False,
        "policy_published": False,
    }
    (output / "layout.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build/privacy-layout")
    parser.add_argument("--browser", help="Caminho opcional de Chromium já instalado")
    args = parser.parse_args()
    check(args.output, args.browser)


if __name__ == "__main__":
    main()
