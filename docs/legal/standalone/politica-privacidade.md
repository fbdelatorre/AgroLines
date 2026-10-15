# AgroLines standalone offline — Política de Privacidade

MINUTA PARA REVISÃO. NÃO PUBLICAR ENQUANTO HOUVER CAMPOS OU DECISÕES PENDENTES.
Versão documental: 15/10/2026.
Vigência: [DEFINIR A DATA DA PRIMEIRA DISPONIBILIZAÇÃO EFETIVA].
Endereço público: [DEFINIR E TESTAR URL HTTPS ANTES DE PUBLICAR].

## 1. Responsável, contato e escopo

O responsável pelos tratamentos sob sua gestão no AgroLines é FABRICIO JOSE
DELATORRE, pessoa física. Contato oficial de suporte e privacidade:
fabricio.grupodelatorre@gmail.com. A marca informada do aplicativo não corresponde
à confirmação de empresa constituída. Identificação e endereço de atendimento
exigíveis na contratação deverão constar do instrumento comercial apropriado;
não são inventados por esta minuta.

Esta política trata da versão Windows standalone exclusivamente offline, baseada
em runtime integrado e instalador Inno Setup. Ela não descreve colaboração online,
login remoto, convites, recuperação de senha, sincronização ou API como recursos
disponíveis. Nenhum desses serviços é exigido para abrir os projetos locais.
O PostgreSQL/PostGIS central e a arquitetura remota reservada a versões futuras
não integram o funcionamento desta edição distribuída.

O aplicativo processa os dados locais por ação do usuário. Isso não significa
que o desenvolvedor receba automaticamente esses dados ou seja controlador de
todo tratamento realizado pelo proprietário do projeto. Quem decide inserir e
usar dados pessoais de terceiros deve observar suas próprias responsabilidades.

## 2. Informações realmente processadas no computador

Projetos SQLite .agrolines podem conter nome e identificador local do projeto,
feições e nomes de talhões/propriedades informados nos arquivos, polígonos,
coordenadas, sistemas de referência originais e de trabalho, atributos importados,
relatórios de inspeção geométrica, referências de origem, identificadores de
revisões/eventos e datas de alteração. Não se promete que esses campos sejam
anônimos: localização e nomes podem permitir associação a pessoas.

Arquivos originais SHP e seus componentes, GPKG, KML, KMZ e GeoJSON podem conter
nomes, descrições, atributos, identificadores, caminhos e metadados não visíveis
na interface. Os originais/sidecars e seus dados arquivados na importação podem
permanecer no projeto e em seus backups, mesmo após alteração de uma geometria.
O usuário deve revisar o conteúdo e evitar informações pessoais desnecessárias.

Histórico de revisões e origens é conservado no arquivo local. A edição cria nova
revisão, não apaga automaticamente todas as versões anteriores. Backups e arquivos
restaurados conservam os dados incluídos, inclusive histórico e originais.

## 3. Rede, autenticação, credenciais e licenciamento

A política offline é fixada no perfil distribuído: clientes remotos são excluídos,
conexões Python são recusadas, PROJ não usa rede, drivers remotos GDAL são limitados
e Qt WebEngine usa recursos/mapa Leaflet locais e interceptação de pedidos. Não há
telemetria própria ou envio automático de projetos, arquivos, relatórios ou e-mails.
Testes negativos foram executados; observação física completa dos processos nativos
com rede desconectada continua parte da homologação, não garantia universal desta política.

Não há login remoto nem necessidade de guardar senha/token de servidor nesta edição.
O módulo de credenciais remotas com DPAPI das versões de colaboração é excluído
do pacote offline. Não se atribui ao SQLite criptografia por DPAPI. Não há coleta
implementada de CPF, RG, data completa de nascimento, identificador de hardware,
pagamento ou ativação comercial por este aplicativo.

Uma interface de licenciamento existe para evolução futura, sem infraestrutura
comercial completa nesta versão. Eventual ativação ou cadastro futuro exige nova
avaliação, informação sobre dados, base legal, segurança e retenção; não é autorizado
silenciosamente por esta política. Licenças offline válidas não devem depender de
contato periódico obrigatório para as funções agrícolas essenciais.

## 4. Armazenamento, proteção e permissões locais

Projetos, backups, exportações e destinos de diagnóstico são gravados em locais
escolhidos/acionados pelo usuário. Diretórios auxiliares usam armazenamento do
perfil Windows, como LocalAppData/AgroLines, inclusive temporários e evidências
quando esses procedimentos são acionados. O programa não administra automaticamente
todos os backups do Windows, serviços de sincronização ou outras cópias.

O AgroLines não implementa criptografia própria dos arquivos .agrolines ou backups.
Permissões de conta/pasta, criptografia do sistema e proteção do equipamento devem
ser administradas pelo usuário; esta política não presume BitLocker configurado,
segurança absoluta ou anonimização. Arquivos em pasta acessível a terceiros podem
ser lidos conforme as permissões do Windows.

O aplicativo não desativa SAC, Defender ou outros mecanismos de proteção. A
homologação física da distribuição legitimamente assinada ainda é necessária.
Não se declara compatibilidade SAC comprovada pela simples compilação ou assinatura.

## 5. Retenção, histórico, exportação e exclusão local

Não existe prazo automático de descarte de projetos, originais, histórico, backups
ou diagnósticos locais. O usuário conserva esses arquivos até removê-los por seus
próprios procedimentos. Não há exclusão seletiva de todas as revisões/originais
arquivados pela interface atual. Excluir só o arquivo que foi importado não elimina
a cópia já conservada dentro do projeto.

Para eliminar dados locais, feche o projeto e considere seu arquivo, backups,
restaurações, exportações, lixeira e cópias externas. Excluir uma cópia não elimina
as demais nem representa eliminação forense. O responsável não tem acesso automático
ao computador para realizar exclusão remota.

O usuário pode copiar/compartilhar arquivos por ferramentas externas sob sua
responsabilidade. Recursos de importação/exportação devem ser utilizados conforme
os formatos efetivamente disponíveis na versão; não se promete exportador ainda
não implementado. Nenhuma exportação implica upload pelo AgroLines.

## 6. Instalação, atualização e desinstalação

O instalador mantém os binários em Program Files, em pastas por versão, e um
launcher estável. Os projetos e backups devem ficar fora da instalação. A configuração
foi preparada para não excluir os dados externos; o ciclo físico de atualização,
desinstalação e preservação ainda precisa ser homologado com pacote legítimo.
Não se promete que essa preservação já foi comprovada apenas pelo script.

Mantenha backup verificável antes de atualizar/desinstalar. Desinstalar não é um
pedido de eliminação dos arquivos pessoais, projetos, lixeira ou cópias de outros
programas. Não há atualizador online próprio obrigatório nesta edição. O Windows
e o meio utilizado para obter o instalador podem ter tratamentos próprios, distintos
do processamento local do AgroLines.

## 7. Diagnósticos, falhas e suporte voluntário

A execução normal não envia relatórios de falha ao desenvolvedor. Probes de
manutenção acionados expressamente podem gravar versões, resultados sintéticos,
caminhos, componentes carregados, processos auxiliares e eventos de integridade
no destino indicado ou em LocalAppData/AgroLines/Evidence. Caminhos e eventos podem
revelar conta/computador e dados de outros programas; não são presumidos anônimos.
Não há descarte automático desses arquivos locais.

O canal de suporte previsto é o Gmail pessoal gratuito informado, não Google
Workspace. Segundo o titular, ainda não começou a receber suporte de testadores
AgroLines nessa conta; só ele tem acesso, não encaminha esses materiais a outros
serviços nem os baixa para pastas sincronizadas. Essas declarações não comprovam
que MFA, segurança, retenção e exclusão já tenham sido configurados/testados.

O envio por e-mail é iniciativa voluntária do usuário, utilizando outro programa.
O AgroLines não envia projetos, capturas, logs ou dados pessoais para esse endereço.
Descreva o problema e use exemplo sintético sempre que possível. Não envie senhas,
tokens, documentos pessoais, dados sensíveis ou projeto completo sem necessidade.
Envio para suporte não autoriza reutilização indiscriminada, publicidade ou venda.
Dados de terceiros desnecessários devem ser evitados e minimizados pelo atendimento.

## 8. Tratamentos sob responsabilidade do titular e prazos propostos

Para gestão do programa privado inicial, o procedimento previsto usa nome/contato
mínimos disponíveis legitimamente, declaração de maioridade e registro de aceite
vinculado à versão do termo, sem cadastro dentro do aplicativo ou documentos de
identidade como padrão. Os registros próprios são mantidos durante a participação
e eliminados em até 30 dias após saída/encerramento, salvo conservação legal ou
justificativa legítima documentada. Não se promete apagar registros exclusivos da Microsoft.

Mensagens, anexos, projetos e relatórios recebidos para suporte serão conservados
por até 90 dias após encerramento do atendimento, depois excluídos das contas,
pastas e repositórios sob controle do titular, salvo obrigação legal ou necessidade
justificada e documentada. Pedidos de privacidade e registro mínimo da resposta
serão conservados por até 12 meses após conclusão, para comprovação do atendimento,
ressalvadas obrigações legais/defesa de direitos.

Esses prazos foram decisões operacionais do titular, dependem de rotina manual e
não foram implementados como exclusão automática. Não se promete eliminação imediata
de cópias dos provedores ou backups fora de seu controle. Não se aplicam automaticamente
aos projetos que continuam somente no computador do usuário.

A venda comercial ainda não foi iniciada nem foi definida a modalidade de licença.
Dados de contratação, faturamento, pagamento, ativação e suas retenções não são
inventados nesta versão; devem ser definidos e informados antes desse tratamento.

## 9. Bases legais, fornecedores e transferências

[REVISÃO JURÍDICA NECESSÁRIA ANTES DA PUBLICAÇÃO: definir e documentar as bases legais
por finalidade para gestão dos testadores, suporte, pedidos de direitos e quaisquer
tratamentos comerciais futuros. Não se afirma consentimento, execução contratual
ou legítimo interesse já adotados por esta minuta.]

Google/Gmail poderá processar mensagens enviadas voluntariamente para suporte.
Microsoft/Partner Center administra o grupo privado “AgroLines - Testadores Internos”
no canal Store já preparado; isso é separado do uso local da edição standalone.
Não se presume que a Microsoft esteja distribuindo este instalador standalone.
Não foram confirmadas consultas/exportações de relatórios de instalações, avaliações,
falhas ou estatísticas pelo titular; não se afirma uso atual desses relatórios.

GitHub é usado no desenvolvimento, CI e evidências sintéticas. Uma futura página
estática da política está preparada, mas não foi publicada/validada. Visitas pelo
navegador e downloads escolhidos pelo usuário são tratamentos da plataforma, não
telemetria enviada pelo app. O mecanismo efetivo de entrega do instalador comercial
é [DEFINIR ANTES DA DISTRIBUIÇÃO]; não se inventam outros fornecedores.

Os serviços citados podem envolver tratamento fora do Brasil conforme suas práticas.
Isso não demonstra transmissão de projetos pelo app offline. Países, papéis,
contratos e mecanismo aplicável à LGPD dependem da conta e do fluxo real; não se
presume DPA Workspace para Gmail pessoal nem equivalência automática de SCC/DPF
a mecanismo LGPD já adotado. [REVISÃO/COMPROVAÇÃO PENDENTE PARA OS FLUXOS EXTERNOS.]

Referências dos provedores: https://policies.google.com/privacy?hl=pt-BR ;
https://www.microsoft.com/pt-br/privacy/privacystatement ;
https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement .
Essas referências não substituem a conferência dos documentos efetivamente aplicáveis.
Não há uso confirmado para publicidade, perfilamento ou comercialização de dados.

## 10. Direitos, atendimento e incidentes

Nos casos aplicáveis, a LGPD prevê confirmação, acesso, correção, informação sobre
compartilhamento, anonimização, bloqueio/eliminação nas hipóteses legais, portabilidade
quando cabível, oposição e direitos relativos ao consentimento. Solicite pelo contato
informado, com o mínimo necessário para localizar o tratamento. Não envie documento,
senha ou token espontaneamente. Verificação de legitimidade deve ser proporcional.

O titular deve registrar o pedido, localizar os dados sob seu controle, avaliar
obrigações legais, responder nos prazos aplicáveis e documentar ações/limitações.
Não existe atendimento automático na interface. Pedidos sobre projetos que só o
usuário controla ou sobre registros de outro controlador podem exigir atuação de
quem tem esses dados. A política não dá acesso remoto ao desenvolvedor.

Incidentes e exposição acidental devem ser relatados pelo contato oficial. O
procedimento manual deve conter acesso indevido sob controle do titular, minimizar
exposição, avaliar riscos e pessoas afetadas, preservar evidências necessárias e
realizar comunicações à ANPD/titulares quando legalmente exigidas. Não se promete
detecção automática, recuperação de cópias de terceiros ou ausência de incidentes.

## 11. Testadores, público e alterações

O primeiro programa privado é voluntário, gratuito e exclusivo para pessoas com
18 anos ou mais. A declaração simples e o aceite do termo aprovado são controles
manuais prévios; não se declara que foram obtidos. Não há cadastro de menores,
coleta invasiva de idade ou bloqueio etário no código. Não se exige CPF/RG, data
completa de nascimento, imagem ou autorização parental no programa inicial.
Uma ampliação para menores depende de revisão jurídica/operacional, inclusive art.
14 da LGPD e melhor interesse. Dados desnecessários de menores eventualmente
recebidos em anexos exigem minimização e avaliação das obrigações, não cadastro.

A classificação de conteúdo Store informada continua Brasil Livre / IARC 3+ /
Microsoft 3+, distinta da elegibilidade 18+ do grupo; não foi alterada ou revalidada
em tempo real por esta política. Audiência privada e grupo existente permanecem.
Essas configurações não são condições de ativação nem prova de idade no standalone.

Mudanças relevantes serão comunicadas manualmente por e-mail aos testadores cujos
contatos possam ser utilizados legitimamente, e na página da política quando houver
URL pública validada. Não há envio automático implementado. Novas práticas exigem
atualizar o texto e rever suas bases antes da adoção. A vigência e URL continuam
pendentes; esta minuta não está juridicamente aprovada ou pronta para publicação.
