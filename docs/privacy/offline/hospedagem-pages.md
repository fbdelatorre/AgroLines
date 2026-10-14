# GitHub Pages — preparado, sem ativação pública

URL esperada: **https://fbdelatorre.github.io/AgroLines/privacidade/**.
Ainda não é URL publicada/validada. O HTML jurídico do PR #12 não foi reescrito.
Existem campos pendentes de vigência, bases legais, transferências e URL; portanto
**a política não está juridicamente finalizada nem autorizada para publicação**.

Em 14/10/2026, consulta somente de leitura à API GitHub indicou Pages não ativado
(`has_pages=false`) e repositório já público. Não alteramos visibilidade, Settings,
ambientes, branch main ou configuração da Microsoft Store. O isolamento descrito
abaixo refere-se ao artefato Pages; não modifica o acesso existente ao repositório.

## Arquivos e isolamento

- `.github/workflows/privacy-pages.yml`: somente execução manual, após aprovação.
- `scripts/prepare_privacy_pages.py`: verifica o HTML e Markdown existentes,
  recusa confirmações/revisões pendentes, hash diferente do aprovado, recursos
  ativos/externos e links internos inválidos. Não renderiza nem modifica texto.
- `scripts/check_privacy_layout.py` e `.github/workflows/privacy-pages-checks.yml`:
  carregam o HTML localmente em Chrome com sandbox ativo. Testam larguras 320,
  390, 768, 1366 e 1920 pixels, rolagem, títulos, ausência de overflow/erros e
  recursos externos. Essa execução não publica nem envia capturas do rascunho.
- `tests/test_privacy_pages.py`: testes de bloqueio, isolamento, hash de revisão,
  conteúdo ativo, links e verificação HTTPS sem credenciais, com dados sintéticos.

O diretório de publicação precisa ser novo e contém **exatamente**:

```
build/privacy-site/
├── .nojekyll
└── privacidade/
    └── index.html
```

`index.html` é cópia binária do HTML aprovado em
`docs/privacy/offline/politica-privacidade.html`. Não usamos `docs/`, a raiz do
repositório ou `gh-pages` como fonte pública, nem copiamos diretórios inteiros.
Não vão no artefato código, bancos, projetos, chaves, arquivos de configuração,
minutas de participação, procedimentos, relatórios internos ou Markdown/TXT.
O checkout do Actions é utilizado para validação, não publicado como website.
A rota raiz `/AgroLines/` não possui página nesta configuração; use `/privacidade/`.

## Barreiras antes do deploy

1. Evento exclusivamente `workflow_dispatch`; não há publicação em push/PR/merge.
2. Entrada de confirmação: `PUBLICAR_POLITICA_REVISADA`.
3. Entrada SHA-256 deve corresponder aos bytes do HTML aprovado nessa revisão.
4. Campos `[CONFIRMAR]`, `[PREENCHER]`, `[DECIDIR]` e avisos `NÃO PUBLICAR` bloqueiam
   antes da criação/upload do artefato. Também são examinados texto HTML decodificado
   e Markdown; não se remove nenhum campo automaticamente para passar no teste.
5. `configure-pages` está com `enablement: false`: não habilita Pages por API.
6. Apenas o job de deploy recebe `pages: write`/`id-token: write`; os checks de
   preparação não têm permissão de publicação. Usar proteção de ambiente quando
   disponível para exigir aprovação do responsável.

O hash/execução técnica não substitui revisão jurídica ou aprovação do responsável.
Não fornecer o valor de confirmação antes de resolver o conteúdo.

## Onde clicar — somente depois de aprovação e texto completo

Não executar estas etapas agora. Elas são instruções para ativação futura autorizada.

1. Abrir `https://github.com/fbdelatorre/AgroLines` → **Settings** → **Pages**
   (menu lateral, seção **Code and automation**).
2. Em **Build and deployment** → **Source**, selecionar **GitHub Actions**.
   Não selecionar **Deploy from a branch** com `/docs` ou `/`, porque exporia
   material além da política. Salvar caso a interface apresente botão **Save**.
3. Em **Settings** → **Environments** → **github-pages** (criar esse ambiente se
   necessário e autorizado), configurar **Required reviewers** com o responsável,
   se disponível. Habilitar **Prevent self-review** quando houver outro revisor
   autorizado. Salvar as regras. Não adicionar segredos de licenças/banco/Store.
4. O workflow precisa estar disponível na branch padrão para aparecer e receber
   `workflow_dispatch`. Como os PRs dependentes não foram mesclados, poderá não
   aparecer ainda em Actions. O responsável deverá aprovar a integração da cadeia
   de PRs em outra ação; esta tarefa não realiza merge nem altera main.
5. Após revisão jurídica, preencher data/URL e campos restantes em uma revisão
   aprovada. Revisar o HTML final do PR #12 e atualizar suas cópias de forma coerente;
   a tarefa Pages não reescreve nem considera resolvidas essas informações.
6. Abrir **Actions** → **Privacy policy Pages (manual, reviewed text only)** →
   **Run workflow**. Escolher a revisão aprovada, preencher a confirmação acima e
   `approved_html_sha256` com o hash **do HTML final aprovado**, então executar.
   Esse hash pode ser calculado por `sha256sum docs/privacy/offline/politica-privacidade.html`
   ou consultado no campo `source_sha256` do log de **Privacy Pages preparation
   checks (no publication)** da mesma revisão. Não usar o hash antigo do rascunho.
7. Aprovar o ambiente **github-pages** em **Review deployments**, se configurado,
   conferindo revisão/hash antes de autorizar. Isso publica somente a política.
8. Em **Settings** → **Pages**, conferir a URL e **Enforce HTTPS**, quando exibido.
   Não configurar domínio customizado nesta preparação. Com project site padrão,
   o endereço será `https://fbdelatorre.github.io/AgroLines/privacidade/`.

Se Pages não estiver disponível, conferir permissões administrativas e plano da
conta. Não mudar visibilidade nem adquirir plano automaticamente. Não foram
configurados cobrança, publicação/certificação do aplicativo ou envio de e-mails.

## Verificações após ativação autorizada

O deploy faz GET anônimo à URL HTTPS exata, usando a validação TLS padrão do Python:
sem cookies, token ou Authorization. Exige HTTP 200, Content-Type HTML e SHA-256 igual
à cópia aprovada; recusa endereço final diferente, pendências e links internos
inválidos. Faz tentativas limitadas para propagação. Não desliga validação de certificado.
Se falhar após o deploy, investigar o resultado e não informar homologação bem-sucedida.

Também conferir manualmente:

- Janela anônima sem login, computador e celular: política completa, acentos,
  texto legível e rolagem, sem cortes horizontais.
- HTTPS válido no navegador e mesma URL/cópia em outro acesso de rede.
- Links internos/âncoras, se forem adicionados após revisão; o HTML do PR #12
  não possui elementos `<a>` nem referências locais que precisem de navegação.
  URLs de fornecedores aparecem como texto, não links clicáveis. Não os alteramos.
- Nenhum caminho público para minutas, relatório, projeto, banco ou código.
  Guardar data, URL, revisão e resultado fora do site público.

Teste local em larguras emuladas não substitui celular físico; HTTPS e acesso público
sem login **não foram homologados** enquanto Pages está desativado. O Chromium local
recusou execução com sandbox neste ambiente; não reduzimos sua proteção. O workflow
Windows de checks oferece verificação em Chrome assinado com sandbox ativo; consultar
seu resultado no PR. Não envia rascunho/capturas para Pages nem publica artefatos do teste.

A Store exige URL de privacidade (política 10.5.1); TXT não a substitui. Após publicação
aprovada e verificada, o responsável poderá inserir a URL no Partner Center em ação
separada. Essa configuração e a publicação do aplicativo não estão autorizadas aqui.
