# Questões residuais e decisões comerciais

As evidências técnicas são reutilizadas, não substituídas por parecer automatizado.
Estados abaixo não alteram os dos sete casos no [relatório](README.md).

## Revisão profissional com perguntas delimitadas

| ID | Fato comprovado e documento | Questão jurídica concreta | Alternativas / menor próximo passo | Estado |
| --- | --- | --- | --- | --- |
| J01 | Qt/PySide/Shiboken externos; Qt Core e bindings substituídos no aplicativo, sem alterar seu EXE; demais módulos não demonstrados. [Instruções](standalone/INSTRUCOES-LGPL.md), [provas #19](../commercial-standalone/native-replacement.md). | LGPLv3 §4(d)(1) atende o mecanismo compartilhado real? Que Installation Information §4(e)/GPLv3 §6 é devida diante do Windows protegido e de variantes legítimas? | Revisar a instalação standalone, ABI, direitos de modificação e novas provas apenas dos alvos necessários. Se inadequado, delimitar §4(d)(0) antes de divulgar material próprio. Não presumir exigência de entregar chave privada ou comprar Qt Commercial. | **REVISÃO JURÍDICA** |
| J02 | Duas versões GEOS 3.11.3/3.14.1 substituídas separadamente; 22/22; fonte/receita Shapely obtida, materiais residuais Fiona ainda U04. libiconv LGPL2.1+ e FreeXL/SpatiaLite com alternativas próprias. | LGPLv2.1 §6 e modalidade de entrega de fontes; eleição de alternativas MPL/LGPL nos builds concretos e componentes estáticos. | Avaliar cada biblioteca/licença separadamente. Escolher entrega de fontes/acesso equivalente durável permitido. Não aplicar automaticamente LGPL3 ao GEOS nem GPL do utilitário iconv à DLL. | **REVISÃO JURÍDICA** |
| J03 | OpenBLAS DLL é idêntico ao wrapper publicado; commit/patches e receitas GCC disponíveis. `-static-libgcc`, teste de ausência de libquadmath no script upstream; texto GCC Runtime Library Exception 3.1 original incorporado. [Registros](records/publication-verification.json). | O processo de compilação específico satisfaz “Eligible Compilation Process” e as condições da exceção? Restam objetos GPL sem exceção aplicável? | Revisar receitas/toolchain e escopo dos componentes. Somente se faltar prova necessária, solicitar mapa e versões exatos. Não concluir automaticamente que GCC estático exige abrir o AgroLines ou que a exceção cobre tudo. | **REVISÃO JURÍDICA** |
| J04 | CPython LICENSE e Shapely Windows pass-through incluem condições Microsoft; launcher próprio usa CRT estático; nova libaec compilada em MSVC. [Textos de origem](../../distribution/legal/supplemental/materials.json). | Quais direitos/condições de redistribuição MSVC/UCRT alcançam cada arquivo e ferramentas usadas, incluindo build hospedado e launcher? | Confrontar origem por hash, termos da ferramenta efetivamente usada e lista de REDIST. Não presumir aceitação de contrato não apresentado nem aplicar condições CPython indiscriminadamente a todos os DLLs. | **REVISÃO JURÍDICA** |
| J05 | [EULA](standalone/EULA.md) está completa como minuta, com opções pendentes, exceções LGPL, consumidor e validade técnica, sem foro abusivo ou limite fictício de indenização. | Adequação à Lei 9.609/1998 arts. 7/8, CDC e venda por pessoa física, inclusive identificação, suporte, garantias e aceite verificável. | Preencher quadro com titular e revisar a minuta antes de adotá-la; exibição Inno não é prova de aceite. | **REVISÃO JURÍDICA** |
| J06 | [Política standalone](standalone/politica-privacidade.md), programa18+, Gmail pessoal futuro sem suporte confirmado; decisões de retenção90d/30d/12m. [Análise prévia de privacidade](../privacy/offline/). | Bases legais por finalidade e mecanismo de transferência internacional realmente aplicável ao Gmail pessoal e outros fornecedores efetivos; proporcionalidade da retenção e resposta a direitos/incidentes. | Usar análise das12finalidades existente; distinguir operação futura, tratamento local e plataforma. Documentar hipótese adotada e instrumento aplicável; não inventar DPA Workspace para Gmail gratuito. | **REVISÃO JURÍDICA** |

Referências oficiais para a revisão (não prova de contratação):

- [LGPLv3](https://www.gnu.org/licenses/lgpl-3.0.html),
  [LGPLv2.1](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html),
  [GCC Runtime Library Exception 3.1](https://www.gnu.org/licenses/gcc-exception-3.1.html).
- [Licenças Qt](https://doc.qt.io/qt-6/licensing.html),
  [obrigações LGPL Qt](https://www.qt.io/licensing/open-source-lgpl-obligations),
  [licenças WebEngine](https://doc.qt.io/qt-6/qtwebengine-licensing.html).
- [Redistribution Visual Studio 2022](https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution).
  Lista não é concessão universal independente dos termos aplicáveis.
- [Lei 9.609/1998](https://www.planalto.gov.br/ccivil_03/leis/l9609.htm),
  [CDC](https://www.planalto.gov.br/ccivil_03/leis/l8078compilado.htm),
  [LGPD](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm).
- [Privacidade Google](https://policies.google.com/privacy?hl=pt-BR),
  [transferências Google](https://policies.google.com/privacy/frameworks?hl=pt-BR),
  [privacidade Microsoft](https://www.microsoft.com/pt-br/privacy/privacystatement),
  [privacidade GitHub](https://docs.github.com/pt/site-policy/privacy-policies/github-general-privacy-statement).
  Esses documentos gerais não comprovam o mecanismo jurídico aplicável ao tratamento
  pelo titular. Store/Pages não são automaticamente fornecedores do runtime standalone.

## Decisões do titular

Todas **DEPENDE DO TITULAR**, não são contratos/licenças já adotados. Nenhum dado
fiscal ou endereço pessoal deve ser inserido no repositório público por padrão.

| Decisão exata | Por que é necessária / efeito de adiar | Próximo passo conservador |
| --- | --- | --- |
| Definir usuário/dispositivo, quantidades, duração, edição/módulos, preço/renovação e validade técnica/suporte/atualizações. Informar identificação fiscal/endereço exigíveis em meio contratual seguro. | EULA não pode ser oferecida comercialmente com opções em branco; testes gratuitos não se tornam venda. | Preencher o quadro para revisão, sem implantar ativação comercial ou coleta de hardware. |
| Autorizar revisão/adotar versão final de EULA e termos18+, escolher modo de aceite verificável e guarda do registro. | Minuta não é contrato aceito; titular não pode assumir que testadores aceitaram. | Aproveitar o modelo de aceite externo ao app em docs/privacy/offline; não criar cadastro invasivo. |
| Escolher modalidade durável de entrega de fontes/avisos de terceiros, local e responsável pela conservação. | Artefatos Actions expiram e ainda faltam fontes exatas de alguns componentes. Adiar mantém bloqueada a entrega comercial. | Entregar pacote de fontes separado junto à versão, ou acesso equivalente aprovado, após completar U01/U02/U04/U06. Não publicar código próprio. |
| Definir início efetivo/vigência, futura URLHTTPS pública e canal de distribuição dos testadores standalone; aprovar tratamentos/bases após revisão e executar rotinas Gmail/retenção. | Política continua minuta; Pages não pode publicar campos pendentes. Grupo PartnerCenter não é controle de acesso automático do instalador standalone. | Configurar MFA/recuperação/acessos e controles mínimos já especificados, ensaiar exclusão manual e atendimento com dados sintéticos; só depois iniciar suporte. |
| Após os itens anteriores, decidir se autoriza etapa de assinatura legítima e homologação física, com elegibilidade/cotação documentada. | Não existe confiança SAC/instalação comercial aprovada neste trabalho. | Conservar diagnósticos sem instalação; seguir roteiro #19 com candidato confiável e autorização posterior. Sem compra agora. |

Nenhuma necessidade jurídica concreta de adquirir Qt Commercial foi demonstrada.
Isso não é declaração de regularização automática da Community: materiais exatos,
mecanismo adequado e revisão acima continuam necessários. Uma licença Qt paga
também não resolve GEOS, vendors, GCC, privacidade ou confiança do Windows por si só.

## Critérios objetivos antes da distribuição

1. Respostas residuais incorporadas por hash/componente, sem GPL incompatível não
   tratado; os gates técnicos passam e não restam avisos/fontes obrigatórios ausentes.
2. Revisão registrada sobre LGPL, GCC/Microsoft, EULA e LGPD; campos contratuais
   preenchidos, política adotada na data correta e procedimentos operacionais ensaiados.
3. Materiais de terceiros entregues com a versão/acesso equivalente durável, nos
   termos aplicáveis; instruções adequadas de substituição/instalação para a cópia real.
4. Candidato/launcher/setup/uninstaller e nativos com confiança legítima verificada
   nos gates existentes; nenhuma compra/assinatura presumida por este documento.
5. Windows11 real com SAC/Defender ativos, usuário comum, sem Python/PostgreSQL,
   offline: instalar, abrir/importar/editar/reabrir/restaurar,22/22; atualizar e
   desinstalar preservando projetos/backups e sem rejeição CodeIntegrity/AppModel.
   Conservar hashes, caminhos carregados, resultados e logs. Ausência de evento
   isoladamente não comprova confiança: é necessário funcionamento real observado.

Os critérios não autorizam executar instalação agora nem publicar/mesclar. A versão
atual permanece diagnóstico de build e os fatos não foram convertidos em aprovação jurídica.
