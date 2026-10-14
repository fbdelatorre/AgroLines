# Preparação para envio privado — nenhuma autorização de envio

**Teste técnico, envio privado e distribuição comercial são estados distintos.**
O candidato é diagnóstico não assinado, não instalável/entregável aos testadores.
Nenhum item abaixo libera envio automaticamente. Não houve alteração do Partner Center.

| Gate | Evidência / ação | Situação / responsável |
|---|---|---|
| Execução técnica | Linux/Windows, 22 referências, EXE congelado isolado, mapa/WebEngine, 5 formatos, vértices/undo/redo/histórico/backup | Resultados da revisão em README; Codex |
| Inventário | Comparação original/atual, hashes, origem, assinaturas, imports PE e observações | Artefatos da execução; Codex |
| Licenças/IP | Revisar todos os componentes, textos/notices, fontes exatas e obrigações LGPL; definir termos próprios sem suprimir direitos de terceiros | Pendente jurídico/fornecedores/responsável |
| Recombinação | Demonstrar LGPLv3 §4(d) e LGPLv2.1 §6 no contexto Store/SAC, ou contrato Qt aplicável; não publicar objetos próprios sem autorização | Pendente jurídico, técnica e autorização; Qt Commercial não resolve GEOS |
| Privacidade | Bases legais, transferências, vigência, URL pública HTTPS e procedimentos operacionais confirmados | Pendente responsável/jurídico; políticas preservadas, Pages inativo |
| Participantes | Private audience, grupo `AgroLines - Testadores Internos`, aceite verificável 18+; nenhuma coleta invasiva | Reconfirmar manualmente antes do envio; não convidar nesta tarefa |
| Store/idade | Brasil Livre / IARC 3+ / Microsoft 3+ independentes da participação 18+ | Preservado conforme relato; sem nova verificação do painel |
| Identidade | `DelatorreCOrporation.AgroLines`, Publisher `CN=43189595-B928-4D57-90A4-24300E4D4976`, PFN `DelatorreCOrporation.AgroLines_pj9w8xnf5vxmg`, ID `9NRDJ3ZTM978` | Verificação de archive/SDK automatizada; conferência Partner Center manual |
| Versão | x64 1.0.0.0; Windows.Desktop mínimo 10.0.22000.0; revisão Store zero | Não confirma se versão já ocupada no Partner Center; revisão manual antes de enviar |
| Capabilities | `runFullTrust`: Win32/PyInstaller e helpers; `unvirtualizedResources`: dados duráveis fora da instalação, diretório restrito LocalAppData/AgroLines | Justificativas em docs/microsoft-store-msix.md; aprovação Microsoft pendente; não remover acesso durável sem migração/teste |
| Integridade | Hash/BlockMap/pack-unpack e payload íntegros; assinaturas upstream preservadas | CI pode medir; pacote não assinado não deve ser instalado |
| Confiança | Pacote efetivamente recebido pela Store: SignatureKind Store/Status Ok; assinatura embutida e catálogo avaliados separadamente por arquivo | Pendente Microsoft e Windows físico; catálogo não é inventado nem instalado |
| Publicação | Publicação manual e audiência privada conferidas; aprovação expressa para submissão | Não autorizado; nunca usar audiência pública apenas com link oculto |
| Instalar offline | Instalar pacote confiável, depois desligar fisicamente rede; máquina sem Python/GIS/PostgreSQL, SAC On e Defender ativo | Pendente bancada física; aquisição inicial da Store requer conexão |
| Operações | Inicialização normal, projeto existente/novo, SHP/GPKG/KML/KMZ/GeoJSON, mapa, edição 0,001 m, undo/redo, geometria inválida, fonte/SRC, histórico/backup/restauração | Probes congelados complementam, não substituem interface física |
| Rede | Sem conexões próprias; recursos locais; monitorar também helper WebEngine, GIS e tráfego nativo | Controles automatizados parciais; rastreamento físico completo pendente |
| Atualização/desinstalação | Duas versões Store legítimas, hashes/projetos/backup preservados após atualizar, desinstalar e reinstalar | Pendente teste; manifesto sozinho não comprova preservação |
| SAC/Defender | Registrar estado antes/depois, eventos CodeIntegrity 3077/3033 e logs AppX; não alterar configurações | Pendente máquina Windows 11 Pro física; sucesso CI não é aprovação |
| Comercial | Gates anteriores, EULA/licenciamento próprio, contratos/rotas de suporte e manutenção, revisão final | Não pronto; sem cobrança/ativação comercial implementada nesta tarefa |

Antes do primeiro envio privado: concluir os gates jurídicos e de proveniência,
revisar capabilities/versão/audiência no painel e obter autorização expressa.
A homologação do **pacote recebido da Store** só ocorre após o envio privado
legitimamente autorizado e processado pela Microsoft; não fingir que pode ser
concluída inteiramente antes dessa etapa. Isso não é aprovação comercial.
