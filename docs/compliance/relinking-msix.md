# Alternativas LGPL e integridade MSIX

| Alternativa | Requisitos e implementação possível | Materiais | Evidência e falta demonstrar | Situação |
|---|---|---|---|---|
| A — biblioteca compartilhada substituível | Versão compatível modificada deve funcionar com a obra entregue; definir localização segura, seleção legítima e direitos, sem gravar em WindowsApps nem relaxar proteções | Fontes/patches/build das bibliotecas, instruções e teste da aplicação real com ABI compatível | Dois consumidores sintéticos inalterados funcionam com Qt Core e GEOS modificados em Linux. Diretório protegido/integridade MSIX impedem tratar troca direta como solução. Rota MSIX/Store/SAC não demonstrada | IMPLEMENTADO, AGUARDANDO VALIDAÇÃO apenas para PoC; rota oficial BLOQUEADA |
| B — recombinação/relinking | Forma utilizável por destinatário para produzir obra com biblioteca modificada, respeitando LGPL3 §4(d)(0) ou LGPL2.1 §6(a) separadamente | Minimal Corresponding Source/Corresponding Application Code conforme Qt; materiais GEOS próprios de §6. Scripts, dependências, build/link e informações de instalação quando exigidas | Receitas/patches de consumidores públicos sintéticos preparados; nenhum objeto/bytecode/fonte proprietário publicado. PyInstaller exige analisar recomposição do CArchive/PYZ e hooks, assinatura legítima do resultado e eventual ativação offline | PENDENTE DE REVISÃO JURÍDICA e de prova Windows; fornecer material próprio exige autorização |
| C — distribuição adicional legítima | Avaliar se mecanismo/material adicional satisfaz direitos relativos à cópia Store, com acesso equivalente e licenças/EULA compatíveis | Fontes correspondentes exatas; eventualmente cópia recombinável/instalador legítimo autorizado e materiais de B | Pacote parcial de fontes preparado localmente. Fonte separada por si só não dá substituição/relinking nem comprova dever da cópia Store. Uma distribuição alternativa não é automaticamente cura | PENDENTE DE REVISÃO JURÍDICA e Microsoft/fornecedores |

Não se implementou busca de DLLs em diretório gravável do usuário, bypass de
integridade, modificação de manifesto oficial, chave compartilhada, certificado de
teste, Developer Mode, instalação unsigned nem desativação SAC/Defender. Não há
kit com código, bytecode ou objetos próprios do AgroLines.

## Teste necessário da rota escolhida

1. Obter fontes/build/patches/avisos exatos e escolher a modalidade após revisão.
2. Preparar biblioteca modificada compatível e materiais efetivamente exigidos.
3. Demonstrar recombinação/substituição com aplicação, dados sintéticos e licença
   offline válida, sem bloqueio indevido por integridade/ativação do AgroLines.
4. Somente com rota de assinatura/distribuição legitimamente autorizada, testar
   instalação/execução em Windows 11, SAC On e Defender ativo. Não copiar bibliotecas
   bloqueadas para outro caminho para tentar contornar decisões de confiança.
5. Conferir regras/termos Store, identidade, atualizações, suporte e direito do
   usuário de exercitar modificações. Registrar limites de suporte sem anular direitos.

O [PoC](../../tools/compliance-poc/README.md) prova a mecânica de ligação compartilhada
em ambiente sintético Linux. Não prova os itens 1–5 para a obra AgroLines. Assinatura
da Microsoft cobre integridade/distribuição segundo seu fluxo, não licença LGPL
nem confiança automática de cada DLL/PYD. Não há motivo demonstrado para entregar
chaves privadas próprias como primeiro experimento; há necessidade de avaliar
Installation Information quando exigida e uma rota utilizável de instalação.
