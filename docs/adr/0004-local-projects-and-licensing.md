# ADR 0004 — Projetos locais e licenciamento independente

Status: implementada a fundação; sincronização e comercialização futuras.
Complementa ADR 0001 e não altera o motor geográfico.

Um arquivo SQLite `.agrolines` representa um projeto de propriedade local.
`core.local_projects.LocalProject` não importa clientes HTTP, sessões, contas ou
PostgreSQL. A aplicação abre primeiro o espaço local; colaboração online é uma
janela separada, aberta explicitamente. Arquivos locais não são cópias autorizadas
indefinidamente de projetos compartilhados: importação/sincronização de conteúdo
remoto ainda exige desenho de autorização e revogação da ADR 0002.

SQLite foi escolhido para transações, backup consistente, portabilidade e runtime
embutido. GeoPackage será formato de intercâmbio espacial: já é importável via Fiona,
mas não é o banco interno nesta fase. Não declarar o arquivo `.agrolines` um GPKG.
SpatiaLite adicionaria uma DLL e uma nova obrigação de assinatura, sem necessidade
para persistência atual; operações continuam em GEOS/PROJ existentes.

Geometrias originais, SRC WKT, atributos, relatórios de precisão e arquivos de origem
com SHA-256 ficam no SQLite sem arredondamento. A representação WGS84 usada no mapa
é derivada; não substitui a geometria original. Edição usa VertexEditor existente.
Histórico de revisões e originais tem proteção contra UPDATE/DELETE no banco.
Uma gravação reserva a transação antes de comparar a revisão esperada; conflitos
são erros explícitos e não substituem a versão gravada. IDs UUID e eventos locais
são duráveis; esses eventos **não constituem sincronização implementada**.

Banco v1 é criado exclusivamente em arquivo novo. Projetos de versão desconhecida
são recusados sem alteração. Migrações futuras terão backup prévio, versões
incrementais e testes de restauração; migrações do PostgreSQL não foram modificadas.
Backup usa SQLite backup API, valida integridade e nunca sobrescreve arquivo.
Restauração cria outro projeto em novo caminho, preservando IDs e histórico.

Licenciamento é um contrato local separado (`LicenseVerifier`, `Entitlements`,
`Module`, catálogo provisório `Edition`). O provedor atual DevelopmentLicense
permite desenvolvimento sem licença e não comunica com servidores. Capacidade de
edição/módulo nunca concede acesso a dados de terceiros.

O futuro verificador comercial receberá apenas chaves públicas de emissores
confiáveis. `PublicSignatureVerifier` define a fronteira: verificar bytes exatos
assinados antes de interpretar claims; rejeitar chave/algoritmo desconhecidos.
Sugestão de perfil futuro: Ed25519, envelope versionado e base64 para payload e
assinatura, key_id e algoritmo explícitos, tamanhos limitados. As claims incluirão
edition/modules, tipo permanente/assinatura/avaliação, emissão/validade e eventual
escopo de instalação. A decisão final depende da auditoria de empacotamento.
Nenhuma emissão, chave privada, ativação, coleta de hardware, heartbeat remoto ou
bloqueio comercial foi implementado. Assinatura de licenças é distinta de
Authenticode/Artifact Signing do executável.

A licença offline permanente não terá vencimento artificial por ausência de rede.
Assinaturas respeitarão validade local assinada; renovação será troca do arquivo,
sem reinstalação. Proteção razoável: validação de assinatura, escopo transparente
opcional e registro local mínimo; relógio adulterado/revogação offline têm limites
que devem ser documentados, sem desativar direitos legítimos silenciosamente.
