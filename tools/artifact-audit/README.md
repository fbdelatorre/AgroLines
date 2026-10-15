# Auditoria estática da cópia c3ffdb

Ferramentas do auditor, não requisitos do cliente. Não importam/carregam PE, não
instalam MSIX/certificados, não assinam nem modificam projetos ou proteções.
Dependência de análise: Python 3.12 e defusedxml; testes usam pytest e uma integração
com o esquema local no ambiente de desenvolvimento já preparado. Sem instalação de
Python/pip no Windows clean de homologação.

Obter o ZIP pelo [artefato histórico](https://github.com/fbdelatorre/AgroLines/actions/runs/38657579756/artifacts/11938080390)
com acesso autorizado; retenção GitHub pode expirar. Não substituir silenciosamente
por build novo se indisponível. O checkout deve ter o objeto c3ffdb local; `git fetch
origin c3ffdb68302a0c46e640e68dc0b561acce250e6d` só obtém o objeto, não faz merge.

```bash
python tools/artifact-audit/audit.py /caminho/privado/agrolines-signing-validation-NOT-FOR-SUBMISSION.zip --repo . --output /caminho/novo/resultado
python -m pytest -q tools/artifact-audit
python tools/artifact-audit/project_snapshot.py /caminho/privado/sintetico.agrolines
```

O auditor exige SHA-256 exato do ZIP/MSIX e recusa saídas existentes. Não extrai arquivos.
Confere 768 hashes de payload, 802 arquivos do mapa de blocos, PE32+/tabela de
certificado e relatórios históricos. Cert table presente não é verificação de
assinatura; SignTool/X509 referem-se à execução Windows histórica, não à plataforma
atual. A classificação só aceita expiração isolada quando timestamp e SignTool exit0
estão registrados. Não aprova confiança atual, licença ou instalação automaticamente.

O snapshot SQLite requer projeto sintético fechado, sem WAL/SHM/journal, esquema v1
conhecido; apenas mode=ro/query_only e verificações de integridade. Saída contém hashes
e contagens, não conteúdo de linhas. Usar cópias privadas na máquina do auditor e
não enviar diagnósticos automaticamente. Não representa migração/backup nem controla
um aplicativo concorrente; fechar o app é pré-requisito manual.

`compare_containers(first,second)` compara bytes integrais, hashes das entradas,
ordem e parte dos metadados de dois ZIPs. Os testes de ZIPs sintéticos ilustram a
diferença conteúdo/envelope; não houve segundo MSIX real nesta auditoria.

Resultados e limitações: [relatório](../../docs/artifact-audit/c3ffdb68302a/README.md).
