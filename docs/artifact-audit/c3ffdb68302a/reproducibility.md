# Por que payload=true e MSIX=false

No commit auditado, `scripts/signing_pipeline.py`, função `reproducibility`, calcula
`first["files"] == manifest(root)["files"]`, mas escreve literalmente
**`"msix_bytes_reproduced": False`**. Portanto:

- `payload_bytes_reproduced=true` comprova a comparação histórica de 768 caminhos
  e hashes em duas compilações no mesmo builder, caminho e epoch. Esta auditoria
  também confrontou o manifesto do primeiro build com os arquivos efetivos do MSIX.
- `msix_bytes_reproduced=false` significa **não testado/não demonstrado**, não prova
  que dois MSIX foram produzidos e divergiram. Não houve segunda embalagem para
  comparação nesse workflow.

A sequência em `.github/workflows/windows-msix.yml` é: build do payload → manifesto
primeiro → segundo build do payload → comparação → manifesto final → **uma chamada**
Build-MSIX/MakeAppx → unpack/verify → observações de runtime → renomeação/binding.
O hash do plano em input-binding usa JSON canônico (`sort_keys`, separadores sem
espaços), não os bytes formatados de plan.json; ambos foram diferenciados na auditoria.

## Limites de cobertura

O manifesto do payload omite arquivos com basename payload-manifest.json; na cópia
inspecionada há somente o manifesto autorreferencial esperado. Ele é congelado após
a comparação. A comparação também não cobre Assets de raiz, AppxManifest de raiz,
AppxBlockMap, Content_Types, layout/ordem/compressão/timestamps do ZIP MSIX nem o ZIP
de artefato GitHub. Não é rebuild independente em máquina limpa.

O MSIX observado tem timestamps de entradas entre 00:07:56 e 00:08:22 de 15/10/2026.
O staging usa cópias e gera arquivos novos, sem normalizar explicitamente todos os
mtimes antes do MakeAppx. Timestamps/ordem/compressão/versão SDK **podem** afetar uma
comparação futura; não foram demonstrados como causa de divergência de dois MSIX
reais aqui. Este MSIX não tem assinatura, portanto timestamp de assinatura de pacote
não explica o resultado atual.

## Correção proposta para build futuro — não aplicada ao candidato

Usar `msix_bytes_reproduced=null`, `msix_comparison_status="not_run"` e número de
pacotes comparados; preservar o campo histórico falso no relatório original.
Para prova nova: dois builds/packagings independentes em diretórios separados,
mesmos lock/commit/SDK/arte/imagens/epoch, hash integral de ambos, e comparação dos
caminhos/hashes descomprimidos e metadados. Reproduzir payload e reproduzir envelope
são gates diferentes. Se não houver igualdade integral, localizar a diferença e
registrar o escopo; não afrouxar o gate nem substituir o hash de referência.

`compare_containers` na ferramenta nova demonstra a distinção em ZIPs **sintéticos**:
conteúdo igual + timestamp diferente → container diferente. É um teste do comparador,
não uma conclusão sobre uma segunda cópia AgroLines inexistente. Nenhum novo MSIX
foi gerado para mascarar ou repetir o resultado.
