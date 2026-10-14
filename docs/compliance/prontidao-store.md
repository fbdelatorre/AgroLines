# Prontidão para a Microsoft Store — nenhuma submissão autorizada

Documentação oficial e hashes consultados nesta etapa em [evidence/research.json](evidence/research.json).
Páginas da Microsoft são referência de regras, não prova de acordo aceito na conta.
A URL tentada para App Developer Agreement retornou 404; obter o acordo/versão
realmente aceitos no Partner Center. Não inventar cláusulas ou contrato comercial.

| Tema | Verificação/fundamento | Resultado e falta |
|---|---|---|
| Win32/MSIX | Aplicativo x64 com runtime e recursos locais; Windows.Desktop mínimo 10.0.22000.0, teste-alvo 10.0.26100.0 | Base compilada preservada; CI não é instalação limpa |
| Identidade | DelatorreCOrporation.AgroLines; CN=43189595-B928-4D57-90A4-24300E4D4976; PFN DelatorreCOrporation.AgroLines_pj9w8xnf5vxmg; Store 9NRDJ3ZTM978 | Nenhuma alteração; conta Individual/nome requer esclarecimento §10.14 |
| Assinatura/integridade | Documentação de signing options: Store assina MSIX após certificação; Windows exige pacote confiável; blockmap protege conteúdo instalado | Envelope atual unsigned não é instalável autorizado. Não há equivalência automática entre envelope/catalog e confiança de toda DLL/PYD; 78 unsigned permanecem |
| Propriedade intelectual | Store Policies §11.2 e §10.2 exigem direitos e avisos aplicáveis | Este dossiê materializa avisos/fontes parciais; LGPL, copyrights/credits estáticos e direitos ainda não fechados |
| Licenças/EULA | Termos próprios não podem retirar direitos de terceiros; conferir licença padrão/customizada realmente aplicável no cadastro | Minuta para revisão; Store não aprova genericamente LGPL nem corrige direitos por assinar |
| Privacidade | §10.5.1 exige URL e política de Desktop/Win32; §10.5.4 métodos modernos de criptografia para dados pessoais | MD/HTML/TXT disponíveis para revisão; campos/revisões e ausência de cifra local pendentes. Pages inativo |
| Capabilities | §10.6 exige relação legítima com funções; manifesto usa runFullTrust e unvirtualizedResources | Win32/helper e exclusão estreita LocalAppData/AgroLines para dados duráveis justificam pedido, não comprovam aprovação Microsoft |
| Audiência | Documento visibility-options: Private audience é diferente de só ocultar listagem/link; grupo usa contas pessoais Microsoft | Manter audiência privada e grupo informados; configuração não foi alterada/verificada em tempo real; nenhuma pessoa convidada |
| Atualização/desinstalação | Arquivos de projetos ficam fora da instalação e exclusão AppData é restrita | Manifesto não prova preservação; exigir upgrade/desinstalação/reinstalação com comparação de hashes em Windows real |
| Segurança | SAC/Defender preservados, sem test cert, Developer Mode, AllowUnsigned ou instalação unsigned | Testar pacote legítimo distribuído pela Store após autorização de submissão; SAC só depois dessa evidência física |

## Antes da primeira submissão privada

Fechar evidências/fontes/avisos realmente exigidos e rota LGPL/EULA; resolver campos
obrigatórios de privacidade e conta/capabilities; revisar novo candidato e seu hash;
obter autorização expressa. Um MSIX unsigned pode ser entrada do fluxo Store segundo
a documentação oficial de assinatura, mas esse fato **não libera este candidato**
com pendências. Não publicar automaticamente após certificação: revisar opções de
submissão/audiência manualmente. Nenhuma configuração foi alterada.

## Depois de autorizada e aceita a distribuição de teste

Windows 11 real com SAC On e Defender ativo, sem Python/pip/PostgreSQL: instalar da
Store, registrar identidade/assinatura e Code Integrity pertinentes minimizados;
desconectar fisicamente, abrir projeto sintético, importar cinco formatos, editar,
salvar/reabrir/histórico/backup/restaurar. Observar helpers Qt/WebEngine e carregamento
GIS, realizar atualização e desinstalação/reinstalação preservando arquivos reais de
teste. Não inferir confiança do laboratório a partir de CI ou do catálogo isolado.
Nenhum teste exige baixar a segurança. Dados/eventos pessoais não devem ir ao GitHub.
