# PySide6 Community, AgroLines proprietário e Microsoft Store

Avaliação técnica/documental de 14/10/2026, proposta para revisão jurídica.
Responsável residente no Brasil; produto proprietário, licenças de uso próprias;
**nenhuma licença Qt Commercial adquirida**. Não é declaração de conformidade.
Nenhuma dependência, licença do projeto, política de privacidade ou visibilidade foi alterada.

## Conclusão e decisão recomendada

**LGPLv3 é uma alternativa potencial para o código próprio fechado, mas o MSIX
atual não demonstra as condições necessárias.** Há módulos redistribuídos que
não têm alternativa LGPL nas fontes consultadas, ausência de evidência de fonte
correspondente completa e nenhuma demonstração de substituição/relinking no
pacote Store assinado. Não recomendar submissão deste candidato como conforme.

Primeiro aprovar uma avaliação de um payload Qt mínimo (sem alterar dependências
neste PR), mantendo todos os módulos efetivamente necessários a UI/WebEngine/GIS.
Em paralelo, solicitar à Qt resposta escrita sobre contratação e migração do
projeto Community. Escolher a rota depois de provar o mecanismo LGPL e revisar
os termos, ou confirmar uma oferta comercial que cubra o projeto e os módulos.
Qt Commercial não dispensa GEOS/LGPL, Chromium ou outras licenças de terceiros,
nem assina automaticamente DLLs GIS ou comprova SAC.

## Módulos realmente usados e componentes incluídos

O inventário de 453 arquivos e o subconjunto de **299 arquivos originários de
wheels Qt** estão em `inventario-arquivos.csv` / `qt-arquivos.csv`, anexados
à conclusão da execução. A origem por wheel não atribui automaticamente licença
Qt a MSVC, codecs ou outros terceiros contidos no wheel.

Imports diretos de produção: **QtCore, QtGui, QtWidgets, QtSvg, QtWebChannel,
QtWebEngineCore e QtWebEngineWidgets**. QtNetwork/QtPrintSupport também aparecem
na execução. Imports em testes/ferramentas são analisados separadamente de uso do
cliente; dependências carregadas transitivamente continuam relevantes.

| Família | Evidência efetiva | Avaliação para a rota Community |
|---|---|---|
| PySide6/libpyside e Shiboken | Headers v6.12.0: Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only | Candidatos LGPL; conferir todo o binding/build, avisos e fontes correspondentes |
| QtBase: Core, Gui, Widgets, Network, OpenGL, PrintSupport; plugins Windows/imagens/estilos | QtBase v6.12.0 tem alternativa LGPL; DLLs e bindings observados | Revisar componentes/plugin e terceiros específicos, não somente o header representativo |
| QtSvg, QtWebChannel, QtPositioning | Imports ou carga transitiva; headers oficiais versionados registrados em fontes.json | Avaliar LGPL e dependências da versão real; Positioning carregado não prova coleta de localização |
| QtQml/QtQuick/QuickWidgets e auxiliares | Dependências carregadas, mesmo sem tela QML escrita pelo aplicativo | Headers de QtDeclarative consultados; incluir fontes/avisos/relinking aplicáveis |
| QtWebEngineCore/Widgets e QtWebEngineProcess | DLL/PYD e imagem do helper observados e correlacionados por hash/caminho | Fonte `dev` oferece LGPL; tag v6.12.0 indisponível no repo WebEngine. Versão exata 6.12.0.140/Chromium e correspondência de fonte/build ainda pendentes; não extrapolar `dev` ao binário |
| Qt Charts, Graphs, Data Visualization, Quick 3D, Virtual Keyboard | DLLs/plugins/QML presentes; headers v6.12.0 consultados declaram Commercial OR GPL-3.0-only | **Não tratá-los como LGPL.** Necessária decisão de remover componentes dispensáveis com testes ou obter direitos comerciais; nenhuma remoção executada |
| Qt Quick Timeline, Shader Tools e demais famílias não usadas diretamente | Presentes no inventário; documentação/fonte específica indicada quando obtida | Quick Timeline também declara Commercial OR GPL3; Shader Tools tem alternativa LGPL no header consultado. Demais módulos precisam de classificação própria; ausência de carga não autoriza descarte |
| Qt PDF, multimídia, geoservices, codecs e outros plugins/QML | Empacotados; grande parte não observada | Não presumir licença uniforme. Fontes Qt PDF `dev` não substituem fonte exata; codecs/patentes/notices adicionais precisam de revisão |
| MSVC/UCRT dentro dos wheels | Arquivos assinados, alguns carregados | Direitos de redistribuição Microsoft, não LGPL; verificar licença aplicável e REDIST |

A inclusão de módulos GPL não prova, isoladamente, que todo o aplicativo se
transformou em GPL: ligação/derivação versus mera agregação exige análise. Mesmo
um componente independente redistribuído tem obrigações próprias de fonte e
avisos. A falta de uso observado não elimina sua redistribuição no MSIX. O pacote
atual não permite simplesmente declarar que “PySide6 é LGPL” e encerrar a análise.

## O que LGPLv3 permite e exige

Foi lido o texto integral LGPLv3 e GPLv3 do repositório oficial QtBase v6.12.0;
URLs/blobs/SHA-256 estão em `fontes.json`. As seguintes são condições a cumprir,
**não medidas declaradas já implementadas**:

1. LGPLv3 §4 permite um *Combined Work* sob termos próprios, desde que eles não
   restrinjam modificação das partes da biblioteca e engenharia reversa para
   depurar essas modificações. O código próprio pode permanecer proprietário
   quando essa opção é realmente aplicável; isso não isenta código derivado ou
   módulos somente GPL.
2. §4(a–c): avisos destacados de uso/licença; cópias de **LGPLv3 e GPLv3**; copyright
   e referência aos textos nos avisos em execução quando aplicável. Verificar
   diálogo de licenças/manual e conteúdo do pacote, além do coletor automático.
3. Redistribuição das bibliotecas: fornecer *Corresponding Source* pertinente,
   alterações e scripts/configuração de build sob a licença aplicável. GPLv3 §6(d)
   prevê acesso equivalente à fonte e direções claras, inclusive em outro servidor.
   Link genérico à homepage ou apenas LICENSE não comprova cumprimento. Não escolher
   uma oferta de fonte de três anos indiscriminadamente: §6(b) e §6(c) têm condições
   próprias, inclusive restrição não comercial de §6(c).
4. §4(d)(1): um mecanismo de biblioteca compartilhada adequado deve operar com
   uma versão modificada **compatível com a interface**. DLL/PYD separado ajuda,
   mas não basta se integridade/identidade/ativação impede substituir e executar.
5. Alternativamente §4(d)(0): fornecer *Minimal Corresponding Source* e
   *Corresponding Application Code* em forma e termos que permitam recombinar/relinkar.
   Isso pode envolver objetos/bytecode e materiais de build; não afirmar que publicar
   todo o source próprio é sempre necessário nem que PYZ sozinho é kit suficiente.
6. §4(e) remete à *Installation Information* apenas quando requerida pelo GPLv3 §6,
   e na extensão necessária. A definição de *User Product* e a transação concreta
   exigem revisão jurídica; não presumir obrigação universal de entregar chave
   privada de assinatura nem uma dispensa universal por ser software desktop.
7. Alterações às bibliotecas e sublicenças/termos de terceiros precisam de avaliação
   própria; licença comercial do aplicativo não pode retirar direitos LGPL de terceiros.

GEOS tem LGPL 2.1 no COPYING consultado, com seus requisitos específicos (§6,
substituição/relinking, fonte e termos). Não substituir sua análise pelo texto da
LGPLv3 do Qt. Versões das cópias GEOS vendorizadas devem ser ligadas às fontes exatas.

## MSIX, assinatura, Store e substituição de bibliotecas

A documentação Microsoft consultada confirma integridade pelo BlockMap/assinatura:
MSIX instalado tem arquivos em WindowsApps protegidos; alteração de conteúdo pode
ser bloqueada ou remediada. **Não existe neste PR um fluxo comprovado de substituição
in-place dentro do pacote oficial.** Reempacotar o mesmo Publisher/identidade sem
chave/fluxo autorizado não é solução. Microsoft assinar o MSIX não concede ao usuário
o direito técnico de publicar uma revisão sob a identidade oficial nem elimina LGPL.

| Caminho a avaliar | Situação / prova necessária |
|---|---|
| DLL compartilhada substituível no pacote instalado | Não demonstrado; proteções MSIX e assinatura impedem assumir §4(d)(1) satisfeito |
| Kit de recombinação/relinking com fonte de terceiros e código de aplicação apropriado | Possível proposta §4(d)(0); preparar documentação/build/compatibilidade e executar versões modificadas de forma legítima. Não implementado ou aprovado |
| Distribuição alternativa legítima dos materiais para recombinação | Revisar se satisfaz a obrigação relativa à cópia Store, EULA, ativação e instalação. Extração/execução atual sem identidade não prova cumprimento nem confiança; não orientar o usuário a executar binários bloqueados |
| Pacote recomposto/assinado por identidade legitimamente autorizada | Direitos, cadeia pública, identidade distinta quando cabível e viabilidade operacional precisam de confirmação. Não compartilhar chave privada ou alterar a identidade Store oficial |
| Qt Commercial cobrindo o projeto | Pode evitar as obrigações LGPL específicas do Qt coberto, sujeito ao contrato. Não resolve GEOS nem confiança dos outros PE |

Nenhuma rota exige ou autoriza desativar SAC/Defender, instalar certificado de teste,
habilitar Developer Mode, criar exclusões ou procurar DLLs em diretório inseguro.
Uma versão modificada continua sujeita às regras legítimas de confiança do Windows;
a viabilidade do mecanismo com SAC ativo precisa de evidência real.

Não foi encontrada nas políticas Store consultadas uma aprovação genérica de LGPL
nem uma proibição universal. Segurança (§10.2) e direitos de propriedade intelectual
(§11.2) continuam obrigatórios. O acordo aceito pelo desenvolvedor, os termos de
licença padrão/customizados aos usuários e eventuais diferenças para MSIX devem
ser conferidos antes da conclusão: as URLs tentadas do acordo/termos não puderam
ser lidas neste ambiente. **Não afirmar que a Store resolve automaticamente ou
inviabiliza necessariamente LGPL.**

## Nosso licenciamento comercial

`core/licensing.py` possui interfaces e `DevelopmentLicense`; não há emissão,
ativação comercial, heartbeat ou bloqueio de DLL por licença implementados.
Licenças por usuário/instalação, validade e módulos próprios são propostas separadas
da escolha Community/Commercial. A assinatura de um arquivo de licença do AgroLines
não é assinatura Authenticode nem licença Qt.

Ao implementar futuramente, a EULA e controles devem preservar as permissões LGPL
aplicáveis: não proibir indiscriminadamente toda engenharia reversa e modificação
necessária da biblioteca, nem invalidar uma licença válida só pela substituição de
Qt/GEOS por versão modificada compatível. Limites legítimos de uso do código próprio
e direitos de terceiros devem ficar separados. A viabilidade e redação precisam de
revisão jurídica. Não se exige prometer suporte a bibliotecas modificadas.

Não inserir chave privada de emissão ou assinatura de executáveis no cliente.
PyInstaller empacota bytecode Python; compilação/empacotamento **não garantem sigilo
ou resistência absoluta à extração**. O repositório continua público por decisão de
preservação nesta tarefa, e os artefatos Actions existentes também têm exposição;
revisar o histórico de distribuição real, não presumir “nenhum binário foi entregue”
só porque a Store ainda não publicou. Não houve alteração automática de visibilidade.

## Qt Commercial e migração desde Community

A fonte oficial `pyside/pyside-setup`, tag v6.12.0, documentação
`sources/pyside6/doc/commercial/index.rst`, efetivamente lida, descreve:

- Editions Community LGPLv3/GPLv3 e Commercial.
- Qt for Application Development Professional/Enterprise e Device Creation
  Professional/Enterprise como licenças com acesso aos pacotes comerciais.
- Para desktop, **Application Development** é a categoria a cotar; não comprar
  Device Creation por inferência. Escopo final e elegibilidade vêm da proposta/contrato.
- Pacotes comerciais via Qt Account/Installer/qtpip; a documentação orienta não
  usar `pip install pyside6` Community para um build que se pretende comercial.
- Migração técnica: retirar os pacotes Community e usar ambiente novo com wheels
  comerciais. **Não realizamos essa troca.**

Esse documento **não aprova migração jurídica do projeto AgroLines já iniciado**,
preço, retroatividade, cobertura de redistribuições anteriores ou contrato individual.
Páginas qt.io de contrato/FAQ/obrigações estão bloqueadas pelo proxy; bloqueio não é
recusa do fornecedor nem prova de seus termos. Solicitar confirmação escrita:

| Questão para Qt | Condição que precisa ficar comprovada |
|---|---|
| Projeto já desenvolvido com Community e artefatos já gerados | Se pode migrar; condições, eventuais exigências temporais, regularização/cobertura anterior e futura |
| Pessoa física no Brasil, um desenvolvedor | Elegibilidade, contrato/licenciado correto, assentos para colaboradores/CI, impostos/moeda/custo recorrente |
| Escopo | PySide6, Shiboken, WebEngine/Chromium, módulos GPL detectados e versões efetivas, Windows x64 e redistribuição pela Store |
| Builds e contrato | Fonte dos wheels comerciais, CI/build agents, direitos de distribuição após expiração/rescisão e suporte/atualizações |
| Obrigações restantes | Terceiros, notices, codecs/patentes e requisitos de código/fonte que a licença não abrange |

Não afirmar que iniciar com Community proíbe definitivamente migração; tampouco
que pagar agora relicencia automaticamente tudo. Só aceitar a rota comercial após
contrato aplicável e resposta documentada, autorizados pelo responsável.

## Pendências em ordem prática

1. Revisão dos módulos efetivamente redistribuídos e suas versões/licenças; decisão
   sobre payload Qt mínimo. Remoção exige autorização e testes de GIS/UI/helpers.
2. Validar textos/notices completos, fontes correspondentes e terceiros de Qt,
   NumPy/OpenBLAS, Fiona/GDAL, pyproj/PROJ, Shapely/GEOS, Python e Microsoft runtimes.
3. Escolher e provar mecanismo LGPL de recombinação/substituição compatível com
   Store/Windows e EULA, ou obter resposta/contrato Qt Commercial para o projeto.
4. Resolver assinatura dos 78 PE unsigned com CA elegível/direitos de redistribuição,
   preservando assinaturas upstream aceitas. Artifact Signing Public Trust **não está
   disponível para pessoa física residente no Brasil**, conforme quickstart consultado.
5. Somente após autorização e saneamento, gerar candidato correspondente e realizar
   homologação física de pacote confiável Windows 11/SAC On/Defender ativo, offline.

Este documento é diagnóstico e proposta. Não é EULA adotada, compra, mudança de
licença, alteração técnica do motor ou aprovação jurídica/Store/SAC.
