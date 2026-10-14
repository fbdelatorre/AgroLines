# Evidência inicial do processo permanente

Execução concluída do novo processo:
[38630529440](https://github.com/fbdelatorre/AgroLines/actions/runs/38630529440),
[artefato de diagnóstico](https://github.com/fbdelatorre/AgroLines/actions/runs/38630529440/artifacts/11926536469).
Head de revisão `e494df6ec3b5d0ca1ccea5cb7f3673d12622320a`; build de PR usa o merge
commit GitHub `98fa608b036648744bb77edcfb0f82e2590bbc39`, registrado no binding.
A execução final das guardas posteriores será apontada no PR; não atribuir essas
mudanças posteriores ao build acima.

| Medida | Baseline original | Novo build validado | Após esta execução |
|---|---:|---:|---:|
| PE nativos | 453 | 453 | 453 |
| Authenticode/SignTool aceitos | 375 | 375 | 375 |
| Sem assinatura embutida | 78 | 78 | 78 |
| Assinaturas novas realizadas | — | 0 | 0 |
| Arquivos novos/removidos perante política | — | 0 / 0 | 0 / 0 |
| SAC homologado | não | não | não |

**Não houve redução de unsigned, assinatura simulada ou aquisição de certificado.**
A recorrência passa a ser controlada por política e gates reutilizáveis: entradas
não conhecidas/alteradas são bloqueadas, originais válidas são preservadas e a
assinatura futura é aplicada apenas a arquivos autorizados. Hoje são 1 EXE próprio
com caminho de assinatura preparado, 77 unsigned de terceiros bloqueados por
aprovação de direitos e 375 assinaturas originais preservadas, incluindo 46 casos
cujo dossiê de origem ainda precisa ser fechado.

Resultado efetivo:

- Duas compilações do mesmo commit/inputs/epoch no mesmo builder produziram
  **payloads byte a byte idênticos**. Não é prova de builds independentes ou de
  identidade binária do envelope MSIX entre SDKs/máquinas.
- Inventário, assinaturas, SignTool, política e guardas PowerShell passaram.
  Status `ASSINATURA PENDENTE`, ready_for_authorized_signing false, nenhuma violação
  de política ou drift; a etapa com chave foi **skipped**, não executada.
- SDK/schema/pack-unpack, 32 assets Store/6 frames ICO, identidade oficial,
  runtime congelado e cinco formatos GIS locais passaram. UI/QtWebEngine sob
  identidade instalada, rede fisicamente desconectada e SAC real continuam pendentes.
- Windows: **178 testes passaram, 2 skips**; Linux: **179 passaram, 1 skip** no CI
  de qualidade do mesmo head, precisão **22/22**. Local: **54 focados passaram**,
  precisão 22/22, Ruff check/format 104 arquivos; aviso Starlette/httpx conhecido.
  Não instalar/iniciar PostgreSQL para esta frente.

Arquivo efetivamente publicado no ZIP de **diagnóstico**, após rename sem alterar bytes:
`dist/msix/AgroLines-1.0.0.0-x64-DIAGNOSTICO-ASSINATURA-PENDENTE.msix`.
Versão 1.0.0.0 x64, Windows Desktop mínimo 10.0.22000.0/MaxTested 10.0.26100.0.
SHA-256 desse MSIX: `7c9bcd93a74695ecd048f6d78056b9e1893513845a4a0ea2161ccfac8a372ed0`.
Tamanho: 284.435.376 bytes. Não confundir com SHA do ZIP ou com o MSIX original
`22286add...`. Nenhum dos dois foi instalado ou enviado à Microsoft nesta tarefa.

A política original e as evidências de cargas (incluindo 67 unsigned carregados)
permanecem em docs/native-store-audit, sem repetir a investigação de origem do zero.
A nova amostra GeoJSON de diagnóstico recebeu EPSG:4326 **explícito** após o CI
rejeitar sua ausência; o comportamento correto do importador foi preservado.
Não houve mudança de dependências, drivers, algoritmos, licença, visibilidade,
classificação etária, política de privacidade ou configuração da Store/Pages.

O código oferece duas rotas posteriores, ambas desabilitadas e sem submissão:
assinatura própria CSP/KSP após certificado/direitos/ambiente; ou preparação
controlada para homologação privada Store sem exigir certificado próprio, após
procedência/revisão/autorização. Nenhuma rota aprova automaticamente licenciamento
Qt/LGPL, distribuição final ou SAC. As compras e a bancada real são externas ao CI.
