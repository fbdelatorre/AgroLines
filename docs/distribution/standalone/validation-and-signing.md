# Assinatura futura e homologação

## Implementado

Build experimental não assinado, identificado como `EXPERIMENTAL-UNSIGNED`, com
hashes e origem. `Prepare-SigningPlan.ps1` inventaria PE e consulta Authenticode/
SignTool; gera plano sem acessar chave. A política standalone herda direitos,
hashes e bloqueios da política existente, alterando só o nome do executável próprio.
Não autoriza assinar dependências por inferência. Dos 78 PE sem assinatura na
referência, 77 são de terceiros e um é o executável próprio. Novos hashes de terceiros,
procedência desconhecida, assinatura inválida e divergência de payload continuam
bloqueando aprovação. Cadeia genérica inconclusiva não equivale automaticamente a
malware; avaliar verificação Authenticode com timestamp e origem em conjunto.

Compilação standalone comercial está bloqueada tanto no wrapper quanto no `.iss`.
O workflow atual não tem etapa de assinatura ou acesso a segredos. Não há envio
à Store nem dependência dos identificadores oficiais para executar o standalone.

## Fluxo preparado para futura autorização

1. Resolver obrigações/licenças de terceiros e fontes/avisos do dossiê; revisar
   EULA proprietária, procedimento LGPL e documentos de privacidade. A política
   existente é minuta offline ligada à distribuição Store; avaliar adaptação de
   canal antes da distribuição standalone, sem marcar aprovação por CI.
2. Confirmar serviço/certificado público para titular no Brasil, custos e
   elegibilidade. Nenhum certificado foi comprado. Não usar identidade Publisher
   da Store como identidade fictícia de certificado standalone. Artifact Signing
   não deve ser presumido disponível a pessoa física brasileira.
3. Em builder de assinatura protegido, rever hashes/direitos da política derivada,
   preencher evidências das decisões e gerar plano. Reutilizar
   `Sign-ApprovedNative.ps1`, com CA/KSP, origem, SHA e timestamp verificados;
   preservar byte a byte assinaturas upstream válidas. Executar gate de transição
   e refazer manifesto após assinatura. Nenhuma chave privada no aplicativo.
4. Criar etapa protegida futura do compilador Inno com `SignTool`/`SignedUninstaller`
   para assinar desinstalador **durante** a compilação e depois o instalador; verificar
   ambos e todos PE. O wrapper experimental recusa esse modo hoje, intencionalmente.
   Não basta assinar somente o arquivo externo do instalador.
5. Gerar novo candidato, novo hash e relatório; somente após autorização realizar
   testes físicos abaixo. Uma assinatura válida não é prova de aceitação SAC.

## Testes físicos pendentes (não executados pelo workflow)

Usar Windows 11 x64 real com SAC e Defender ativos, sem Python/pip/PostgreSQL;
certificados de teste, Developer Mode, exclusões e mudanças de proteção proibidos.
Guardar evidências localmente com dados exclusivamente sintéticos.

| Fase | Critério objetivo |
|---|---|
| Antes | Conferir SHA/assinaturas/cadeia/timestamp; registrar Windows, SAC, Defender, usuário comum e ausência de dependências instaladas. |
| Instalação autorizada | Assinado legitimamente, instalador em pt-BR, caminho correto, UAC só na instalação, atalhos e desinstalador funcionais. Cancelamento sem perda de dados. |
| Execução offline | Desconectar rede; abrir por atalho como usuário comum; WebEngine/Leaflet locais; sem login, DNS/API/tiles externos; registrar tráfego dos descendentes por ferramenta autorizada sem alterar firewall. |
| GIS | Importar SHP/GPKG/KML/KMZ/GeoJSON sintéticos; conferir SRC; editar vértice numérico 0,001 m, undo/redo, histórico; salvar/fechar/reabrir; backup/restauração; 22/22 referências computacionais. Isso não homologa acurácia absoluta de campo. |
| Atualização | Backup anterior; snapshots SQLite fechados e hashes; instalar próximo candidato autorizado, atalhos para versão nova; projetos/histórico/backup idênticos e reabertos; verificar conta comum, interrupção/cancelamento e biblioteca substituída numa cópia separada. |
| Desinstalação | Remover por Configurações → Aplicativos; atalhos/runtime removidos; projetos/backups externos com mesmos hashes e conteúdo; reinstalar candidato autorizado e reabrir. Não prometer limpeza de arquivos criados pelo usuário. |
| Confiança | Registrar assinaturas de todos PE, caminhos realmente carregados, CodeIntegrity 3077/3033 e AppModel; investigar bloqueios. CI sem evento não comprova SAC. |

O coletor somente leitura `tools/windows-lgpl-lab/Collect-Homologation.ps1` registra
estado e eventos; suas consultas de pacote Store não validam instalação Inno.
Não executar helpers antigos `Test-Installed.ps1`/`Test-Upgrade.ps1` sobre este
experimento sem assinatura. Automação destrutiva de instalação foi deliberadamente
excluída do novo workflow.

## Bloqueios comerciais reais

- Fontes/patches/avisos exatos e eventuais recursos GPL/codecs vendorizados ainda
  pendentes nos dossiês anteriores; revisar com fornecedores e profissional jurídico.
- Demonstração nativa completa do mecanismo LGPL e condições da futura EULA.
- Certificado/serviço legítimo, autorização de assinatura por arquivo e etapas
  protegidas para instalador/desinstalador; custos e elegibilidade a confirmar.
- Homologação física de instalação, atualização, desinstalação, tráfego offline e
  SAC; teste de múltiplos usuários, escala de tela e recuperação após falha.
- Privacidade: bases legais/transferências, vigência, URL e procedimentos manuais
  de suporte/testadores adultos ainda dependem das revisões/decisões anteriores.

Não há ativação comercial nova, updater automático ou garantia de aprovação Store.
Projetos não receberam criptografia própria nesta implementação.

Fontes técnicas: [PyInstaller collection modes](https://pyinstaller.org/en/stable/hooks.html#hook-global-variables),
[Inno](https://github.com/jrsoftware/issrc/releases/tag/is-7_1_0),
[assinatura/SAC](https://learn.microsoft.com/en-us/windows/apps/develop/smart-app-control/code-signing-for-smart-app-control).
A arquitetura reaproveita o princípio de dependências integradas do QGIS; nenhum
código QGIS/PyQGIS ou pacote OSGeo4W foi incorporado.
