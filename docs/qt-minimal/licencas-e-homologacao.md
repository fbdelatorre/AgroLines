# Licenciamento e homologação — pendentes

A redução técnica não é declaração de conformidade LGPL. Textos integrais LGPLv3/GPLv3 e LGPLv2.1 são copiados de fontes oficiais identificadas por URL/blob/hash em `distribution/windows/third-party/sources.json`. A aplicação não adota GPL com essa inclusão. O coletor também preserva COPYING/NOTICE, evitando código Python de bases SPDX.

Permanecem pendentes: fontes correspondentes exatas do Qt WebEngine/Chromium, todos os avisos de terceiros efetivamente usados, direitos MSVC/UCRT, mecanismo LGPLv3 §4 e LGPLv2.1 §6 de substituição/recombinação e revisão da futura EULA/ativação. Não foram publicados objetos/bytecode avulsos nem fontes próprias adicionais. Nenhum kit de relink está aprovado. MSIX/WindowsApps não permite inferir substituição direta.

Store é a primeira rota a avaliar antes de contratar certificado. Sua assinatura de envelope não é assinatura Authenticode individual e catálogo presente não comprova SAC. `Test-StoreDeliveredTrust.ps1` inspeciona pacote recebido sem modificar segurança. Homologação física requer Store SignatureKind, SAC On, Defender ativo, Windows 11 sem Python/PostgreSQL, desconexão física e instalação/atualização/desinstalação/reabertura preservando projeto. Não execute instalação do candidato não assinado.
