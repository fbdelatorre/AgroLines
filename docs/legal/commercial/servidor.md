# Implantação do serviço de licenças — preparação, não implantação realizada

Servidor separado do instalador Windows; reutiliza FastAPI, SQLAlchemy, Argon2 e
PostgreSQL do projeto. As tabelas license_* são novas; a migração0006 é aditiva,
não apaga contas ou geometrias. A instância atual de colaboração não ganha rotas
administrativas por importar os modelos. O cliente não instala PostgreSQL, Docker,
Python, pip ou serviços locais. A licença comercial é um perfil compilado separado.

## Preparação pelo operador

1. Definir domínioHTTPS, hospedagem/região, responsável operacional, acesso e backups.
   Não há servidor real, domínio ou provedor contratado/configurado neste PR.
2. No servidor, Python3.12 e `pip install '.[licensing]'`, ou construir
   `infra/Dockerfile.licensing`. Não executar esses comandos no cliente Windows.
   Restringir rede do banco; somente APIHTTPS deve ser alcançável por clientes.
3. Configurar `AGROLINES_DATABASE_URL` apontando PostgreSQL sob controle do operador.
   Em instância do esquema AgroLines, fazer backup testado e `alembic upgrade head`.
   A primeira migração necessita PostGIS se for usada a cadeia completa existente.
   O serviço de licenças não consulta geometrias. Usar banco isolado para ele é
   recomendável; não compartilhar credenciais administrativas com colaboração.
4. Criar dois arquivos de32bytes fora do repositório/imagem, com acesso exclusivo
   ao usuário de serviço, usando `python -m server.license_admin_cli keys --kid ID
   --signing-file CAMINHO_PRIVADO --wrapping-file OUTRO_CAMINHO_PRIVADO`.
   O primeiro emite Ed25519; o segundo cifra segredosTOTP comAESGCM. Fazer backup
   cifrado e ensaiar restauração. Não enviar esses arquivos ao aplicativo, Actions,
   logs, Git, suporte ou serviços de terceiros sem finalidade e autorização.
5. Exportar SOMENTE chave pública com a mesmaCLI, ação`public` e `--public-file`.
   A chave pública não é certificadoWindows. Conservar IDs para rotação e antigas
   chaves públicas até encerrar a validade das licenças já emitidas.
6. Criar administrador interativamente com ação`admin`, confirmação de senha
   exclusiva12+ e cadastro/verificaçãoTOTP. Nenhum segredo aparece na linha de
   comando; a semente do autenticador é exibida só no terminal de inscrição.
   Não capturar/gravar esse terminal. Senhas sãoArgon2; TOTP cifrado; códigos não
   são registrados. Recuperação/perda do autenticador exige procedimento privilegiado
   revisado, nova inscrição e revogação de sessões; não há bypass por e-mail.
7. Configurar `AGROLINES_LICENSE_KID`, `AGROLINES_LICENSE_SIGNING_FILE` e
   `AGROLINES_LICENSE_WRAPPING_FILE` no processo servidor. EmLinux, permissões0600;
   emWindows, restringirACL equivalente antes de iniciar. As chaves NÃO são env vars.
8. Executar `uvicorn server.license_runtime:application --factory` na rede privada.
   Colocar reverseproxy com certificadoTLS público válido, renovação monitorada,
   limite de corpo16KiB, sem registro de corpos/Authorization, semCORS aberto e
   sem cache. A API recusaURLHTTP. Configurar proxy-headers apenas para os IPs exatos
   do proxy; nunca confiarX-Forwarded-Proto de qualquer origem pública. O exemplo
   Docker só confia127.0.0.1; adaptar conscientemente à topologia real.
9. Restringir `/admin` e `/admin/*` porVPN/rede administrativa quando possível,
   mantendo autenticação/senha+TOTP no serviço. Tokens administrativos só emmemória
   do navegador, expiram10min, logout invalida, perfilviewer não escreve.
   Administradoresmanager/owner podem operar todas as assinaturas. Não há
   provisionamento público desses privilégios nem cadastro de cliente no desktop.
10. Ensaiar o fluxo sintético e concorrência no banco de homologação, restore,
    revogação de administrador, limitação de tentativas e indisponibilidade doTLS.
    Fixar política operacional para auditoria/logs/limitadores/assinaturas expiradas
    e atendimento a titulares antes de receber dados reais. Rotinas de limpeza
    comercial ainda não estão configuradas; não apagar registros automaticamente
    sem decisão sobre conservação, backups e defesa de direitos.

## Administração funcional

Em`https://DOMINIO/admin`: senha+TOTP, criar usuário mínimo, criar assinatura mensal
ou anual, receber duas chaves uma única vez, consultar vagas, renovar, suspender,
retomar, revogar definitivamente ou substituir vaga. A substituição gira a chave
anterior e revoga a ativação antiga. Correções são novas operações auditadas, não
edição silenciosa do histórico. Usuário continua com a mesma assinatura nas duas
vagas. Não há cobrança nem comprovação de pagamento; registrar essa decisão fora
da integração de pagamentos até adotar fornecedor e contratos próprios.

O limite é imposto no banco por duas posições e na ativação por bloqueio de linha
e atualização condicional. Chaves/credenciais têm256bits aleatórios e sóhash no
banco. Identificador de instalaçãoUUID aleatório é protegido comDPAPI, não é
atestado de hardware: administrador local pode adulterar software/perfil. Não
prometemosDRM inviolável. Clonagem, fraude e controle de conta exigem resposta
proporcional do operador. Uma máquina offline não conhece revogação nova até
conectar ou vencer sua licença. Não acrescentamos prazo obrigatório7/15/30dias.

## Compilar o cliente

Usar os locks Windows do perfilcommercial, as mesmas exclusõesQt e a infraestrutura
PyInstalleronedir/Inno existente. `distribution.build --commercial` exige
`--license-origin https://DOMINIO` e `--public-keys EXPORT_PUBLICO.json`.
A origem e chaves públicas são incorporadas aoPYZ; nenhum arquivo de configuração
do usuário reativa colaboração ou muda a origem. O build de laboratório usa
`--experimental-licensing` e origem`.test`; não é versão comercial utilizável.
Uma origem ou chave privada não pode ser inferida/validada só pelo tamanho de32bytes:
use exclusivamente a exportação pública daCLI, nunca cole material secreto.

A atualização exige candidato novo e confiançaWindows, assinatura legítima,
revisão jurídica e testes físicos. O cliente tem rede somente dentro do transporte
HTTPS limitado à origem; WebEngine/GDAL/PROJ permanecem sem acesso remoto.
A restrição é de arquitetura, não contenção de um administrador que substitua o
programa. Validação de certificado e hostnameTLS permanece obrigatória, semproxy
do ambiente ou redirects. Não há chaves privadas em nenhum pacote de cliente.

## Limites antes de produção

TestClient comURLHTTPS demonstra regras e fluxo, não handshakeTLS implantado nem
segurança do provedor. DPAPI/GUI congelados são ensaiados emWindowsServer de build;
Windows11 físico/SAC e ciclo instalado continuam pendentes. É necessário ensaio
HTTPS real no domínio aprovado, carga/concorrência, monitoramento, recuperação de
chaves e contas administrativas, retenção, EULA/aceite e plano de incidentes.
Não há integração de cobrança, autosserviço de usuário remoto ou garantia de
inviolabilidade do licenciamento offline. A interface futura de pagamento somente
prevê verificação de evento autenticado; não existe endpoint que aceite uma
alegação não autenticada de pagamento para renovar assinaturas.
