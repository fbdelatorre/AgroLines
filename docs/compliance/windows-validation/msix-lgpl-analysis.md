# Substituição/recombinação LGPL e MSIX — limites técnicos

Complementa [a análise anterior](../relinking-msix.md), sem adotar modalidade jurídica.
Fontes oficiais Microsoft: [integridade/WindowsApps](https://learn.microsoft.com/en-us/windows/msix/desktop/desktop-to-uwp-behind-the-scenes),
[ordem de DLLs](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order),
[LoadLibraryExW](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibraryexw),
[assinatura Store](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/code-signing-options).
Consulta documentada em official-research.json. Textos LGPL originais e análise
separada GEOS permanecem no dossiê pai.

## A — biblioteca compartilhada substituível

O Windows protege a pasta instalada WindowsApps. O MSIX tem manifesto, mapa de
blocos e assinatura do envelope; pode haver catálogo CodeIntegrity, cuja presença
**não é universal**. Alterar uma DLL lá dentro não é mecanismo suportado de
substituição. Não alterar ACLs, catálogos, raízes ou políticas de integridade.
Atualizações da Store substituem o pacote como unidade; não preservam uma edição
manual de DLL em sua instalação protegida.

DLL separada no payload não demonstra LGPLv3 §4(d)(1), nem GEOS LGPLv2.1 §6(b).
O carregador considera mecanismos de resolução, incluindo módulos já carregados,
Known DLLs e o grafo de dependências para aplicativos empacotados. `PATH` ou uma
pasta externa não garantem precedência. Os importadores e nomes originais/renomeados
constam de reference-components.json. Qt ainda depende de plugins, recursos,
WebEngineProcess, ICU/dados quando presentes e versões/ABI compatíveis.

No laboratório Qt, cópias byte a byte do **mesmo consumidor sintético** são
executadas em duas pastas comuns, cada uma contendo sua Qt6Core.dll. O próprio
consumidor consulta GetModuleHandle/GetModuleFileName. GEOS recebe um caminho
absoluto; AddDllDirectory é restrito ao processo filho e ao diretório de laboratório,
com LoadLibraryEx via ctypes. Isso demonstra somente o nível registrado nos
relatórios Windows; não testa a resolução do aplicativo sob identidade de pacote.
**Nenhum mecanismo procura executar um arquivo bloqueado pelas proteções.**

A implementação futura de busca externa no produto exigiria aprovação de arquitetura,
proteção contra preloading/hijacking, origem/ABI, tratamento de erro, interação
com licenciamento e confiança SAC. Não foi implementada nem proposta como bypass.
Não se deve rejeitar bibliotecas modificadas legítimas por um hash proprietário
fixo e simultaneamente alegar que isso cumpre substituição LGPL.

## B — recombinação/relinking

LGPLv3 §4(d)(0): avaliar Minimal Corresponding Source e Corresponding Application
Code utilizável para recombinar com biblioteca modificada, condições/direitos e
§4(e)/GPLv3 §6 quando Installation Information for aplicável. GEOS: analisar
**LGPLv2.1 §6(a)–(e)** independentemente; não importar automaticamente obrigações
LGPLv3. Nenhum kit do AgroLines foi publicado ou declarado suficiente.

Materiais a identificar antes de autorizar um kit:

| Camada | Materiais técnicos a avaliar | Limite atual |
| --- | --- | --- |
| Qt/PySide/Shiboken | fontes exatas, patches, geradores, flags, headers, import libs, ABI/CRT, plugins/recursos/WebEngine/PDF | Fontes candidatas; mapa exato de todos os builds pendente |
| GEOS de Fiona e Shapely | fontes de cada versão, C API/ABI x64, compilador/CRT, import libs, receitas e reparos delvewheel | Pares distintos; consumidor isolado não cobre todos os importadores |
| Python/PyInstaller | versão do runtime/bootloader, spec/hooks, Analysis, scripts de reconstrução e materiais de aplicação suficientes | Ter DLLs externas ao PYZ não demonstra recombinação integral |
| Aplicação proprietária | eventualmente objetos/bytecode/outros materiais utilizáveis sob os termos exigidos | Não disponibilizados, autorização específica e revisão jurídica necessárias |
| Novo pacote | identidade/versão/manifesto, payload reconstruído e assinatura/distribuição legítima | Empacotar novamente invalida a assinatura anterior; não reutilizar assinatura Microsoft |

Objeto C++ nem sempre é a representação adequada da camada Python. Publicar apenas
um script PyInstaller sem os materiais necessários não fecha §4(d)(0). PyInstaller
não garante segredo: compilar/empacotar Python não impede extração. O laboratório
GEOS congelado contém exclusivamente consumidor sintético, não o AgroLines.
Compatibilidade da C API é testada apenas nas funções exercitadas; QtCore é compilado
junto de seus próprios headers/import library. Não comprova ABI com todas as DLLs
dos wheels ou todo o aplicativo.

## C — material/distribuição alternativa

Uma árvore descompactada ou pacote reconstruído sintético pode demonstrar aspectos
mecânicos. Para atender à **cópia Store** é necessário demonstrar que os materiais
permitem exercer os direitos aplicáveis e que os termos da distribuição não os
retiram. Fornecer um download externo de outro produto não resolve isso por si só.
Um pacote reconstruído requer um caminho de assinatura/instalação confiável próprio
ou legítimo fluxo Store autorizado; o usuário não obtém a chave Microsoft e não
pode reaproveitar a assinatura do envelope original. Certificado público também
não garante, sozinho, aceitação SAC.

**Resultado atual:** recombinação integral AgroLines, substituição sob identidade
MSIX e execução de MSIX confiável **NÃO DEMONSTRADAS / BLOQUEADAS POR REQUISITO
EXTERNO**. Solicitações Qt/Microsoft e revisão jurídica tratam essas condições;
nenhuma compra Qt Commercial é tecnicamente imposta por esses ensaios.
