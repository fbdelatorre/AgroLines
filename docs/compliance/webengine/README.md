# WebEngine: fechamento documental específico e limites

Complemento do PR #21, sem alterar o aplicativo, o instalador ou os candidatos
anteriores. Fontes oficiais consultadas em 15/10/2026. Não é parecer jurídico,
aprovação comercial nem homologação Windows/SAC.

## O que esta investigação resolveu

**A divergência `.225`/`.264` tem explicação documental no histórico oficial.**
Não era suficiente ler só o arquivo de resumo `CHROMIUM_VERSION` ou o script
auxiliar `version_resolver.py`. O código efetivamente compilado deve ser examinado
no gitlink do snapshot e no seu `chromium/chrome/VERSION`.

O wheel Windows x64 é `pyside6_webengine-6.12.0.140-cp310-abi3-win_amd64.whl`, SHA256
`f9b61b1d457a591ee590a6b80515f25a3e61e2576a2a0a70566380f9d9de4ab0`, publicado no
PyPI em 08/10/2026. Seu `Qt6WebEngineCore.dll` coincide com o inventário distribuído:
`54488cfc8fea4057377302cec5a1fb1100fb4bc4231cd7e60f43e4fcff28e89e`.

Uma leitura estática dos três exports x64, sem carregar o DLL, retorna:

| Export | Literal retornado pelo binário |
|---|---|
| qWebEngineVersion | 6.140.0 |
| qWebEngineChromiumVersion | 140.0.7339.225 |
| qWebEngineChromiumSecurityPatchVersion | 152.0.7977.83 |

O tag oficial **v6.140.0-rc**, commit
`d505fc23640d2bd6345e6483eb73daf4e19f5829`, aponta para o snapshot
`39352427a3245a19fb395547b3aa38be9d091ec4`: seu `chrome/VERSION` contém **225**,
enquanto o resumo do módulo contém **264**. O nível de segurança também coincide.
O tag beta2 aponta para esse mesmo snapshot. Portanto há uma fonte candidata
concreta compatível com os identificadores, mas eles não distinguem todo o build.

Isso corrige a interpretação excessiva de que todas as fontes públicas candidatas
teriam efetivamente Chromium `.264`. O candidato posterior de 14/10 e o gitlink
`96e61c53...` continuam diferentes; não foram transformados em fonte do wheel.
Históricos anteriores são preservados como registros do que havia sido consultado.

## Fontes e mecanismos públicos identificados

- [Wheel e metadados PyPI](https://pypi.org/project/PySide6-WebEngine/6.12.0.140/#files).
- [Tag RC do módulo](https://github.com/qt/qtwebengine/tree/d505fc23640d2bd6345e6483eb73daf4e19f5829).
- [VERSION efetivo do snapshot](https://github.com/qt/qtwebengine-chromium/blob/39352427a3245a19fb395547b3aa38be9d091ec4/chromium/chrome/VERSION).
- [Arquivo oficial completo de fontes RC](https://download.qt.io/development_releases/qtwebengine/6.140.0-rc/qtwebengine-everywhere-src-6.140.0-rc.tar.xz),
  com [checksum oficial](https://download.qt.io/development_releases/qtwebengine/6.140.0-rc/qtwebengine-everywhere-src-6.140.0-rc.tar.xz.sha256)
  `61257967afd9803a1db6403e86ea25c4efff8fad479bda365a9d81bfd709f621`.
- [Licenciamento oficial do módulo](https://github.com/qt/qtwebengine/blob/d505fc23640d2bd6345e6483eb73daf4e19f5829/src/core/doc/src/qwebengine-licensing.qdoc):
  partes Qt com alternativa LGPLv3; partes Chromium com licenças próprias, incluindo
  componentes LGPLv2.1. A licença Qt Commercial não elimina essas obrigações.
- [Gerador de créditos por target](https://github.com/qt/qtwebengine/blob/d505fc23640d2bd6345e6483eb73daf4e19f5829/cmake/QtGnCredits.cmake),
  com `--gn-target` e `--gn-out-dir`: um inventário de licenças de toda a árvore-fonte
  não é automaticamente o BOM dos binários QtWebEngineCore e QtPdf.

O BSD principal do Chromium exige avisos/condições na redistribuição binária;
não impõe publicar indiscriminadamente todo o código do AgroLines ou de Chromium.
As partes sob LGPL e demais termos devem ser avaliadas separadamente. AUTHORS e
README.chromium são evidências úteis; sua mera presença não quita toda obrigação.
Scripts de snapshot não são recibos do build de um wheel. Não se exige, por padrão,
reproduzir byte a byte bibliotecas permissivas nem obter permissão comercial individual.

## Verificação reproduzível e segregação

```sh
python -m pip install --require-hashes -r tools/webengine_legal/requirements.lock
python -m tools.webengine_legal.audit --directory CAMINHO_NOVO_DE_LABORATORIO
```

Os comandos são de mantenedor. Não devem ser executados no cliente para instalar
o AgroLines. O workflow `webengine-materials.yml` lê wheel e arquivo-fonte oficial,
confere hashes, extrai os literais dos exports sem executar PE, e inventaria os
avisos da árvore-fonte. Não instala Qt, não compila fontes nem gera instaladores.
Só `report.json` é disponibilizado; nem wheel, fontes completas ou runtime são
publicados. O script não é importado pelo aplicativo e não altera os locks oficiais.

O download integral local foi bloqueado pelo proxy de rede em redirecionamentos
para mirrors; isso não foi confundido com ausência de fontes. A confirmação do
arquivo integral fica na execução isolada do workflow. `--skip-archive` permite
reproduzir só a inspeção estática local, deixando essa verificação explicitamente falsa.

## O que ainda impede declarar encerramento integral

| Item | Situação e critério objetivo de fechamento |
|---|---|
| Fonte pública com Chromium `.225` | **RESOLVIDO:** gitlinks oficiais identificados e VERSION efetivo lido. |
| Nível de segurança do DLL | **RESOLVIDO:** export estático identificado como 152.0.7977.83. |
| Arquivo completo de fontes RC | URL e checksum oficiais identificados; validação integral no relatório do workflow. |
| Correspondência final desse arquivo ao wheel | **PENDENTE:** associar revisão/configuração/modificações do build ao wheel; igualdade de três versões não prova tudo. Recibo oficial de release/build, metadados de compilação ou reconstrução controlada podem fornecer evidência. |
| Avisos/codecs dos targets reais | **PENDENTE:** obter créditos gerados dos targets distribuídos ou demonstrar cobertura equivalente dos componentes realmente ligados/embutidos. Não basta copiar AUTHORS/LICENSE genéricos. |
| Entrega e direitos LGPL | **REVISÃO JURÍDICA ESPECÍFICA:** fontes/alterações aplicáveis, modalidade de entrega, EULA, mecanismo compartilhado/recombinação e informações de instalação quando exigidas. Provas Core/GEOS/bindings continuam válidas em seus escopos. |

O relatório mantém `legal_approved=false` e `distribution_approved=false` mesmo se
todas as versões coincidirem. Não há autorização para trocar o runtime, alterar
GIS, interface, assinatura, privacidade ou status jurídico das outras dependências.
Se a documentação pública não fechar os dois fatos residuais de build/créditos,
o pedido ao responsável pelo wheel deve limitar-se a eles e aos hashes acima:
não é uma solicitação de autorização genérica para uso comercial.
