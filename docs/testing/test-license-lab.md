# Ativação TESTE no laboratório privado

Não existe servidor `.test` disponível na internet. A prova do #23 usou fixtures
em processo; o programa entregue para uso manual precisa de **outro build**, com
a origem HTTPS privada e a chave pública do laboratório do titular fixadas nele.
Nenhuma configuração do usuário converte produção em TESTE.

## Preparação na VM de desenvolvimento/servidor

Antes de gerar chaves, crie `C:/AgroLines-Privado` e restrinja sua ACL ao operador
e administradores. A subpasta `Lab` deve ser nova; herdará essas permissões.
Alternativamente use uma subpasta nova no perfil privado do operador.

Este processo fica **fora da VM limpa do cliente**. Requer checkout autorizado,
Python 3.12 e dependências de servidor/licenciamento já declaradas no projeto:

```powershell
python -m venv server-env
./server-env/Scripts/python.exe -m pip install -e '.[licensing]'
./server-env/Scripts/python.exe -m scripts.vm_license_lab init --directory C:/AgroLines-Privado/Lab --origin https://192.168.50.10
```

**Substitua `192.168.50.10` pelo IPv4 privado realmente atribuído à VM do servidor**,
alcançável pelas VMs cliente. O script não cria rede, domínio, NAT ou regra de
firewall. Usa apenas localhost/IPv4 RFC1918/loopback, porta 443 e diretório novo fora
do repositório. Para servidor e cliente em VMs distintas, `localhost` não serve.
Mantenha o IP estável; mudança de origem exige nova compilação. Não exponha a porta
na internet. O switch privado/interno e as regras precisam ser configurados pelo
titular; a VM pode ter conexão separada para baixar o instalador.

Restrinja `C:/AgroLines-Privado/Lab` ao operador/conta de serviço e administradores.
No Windows, confira **Properties → Security → Advanced** e a herança de permissões;
o modo POSIX `0600` do script não prova ACL Windows. Não use pasta compartilhada,
OneDrive/Drive ou repositório Git para o estado do servidor. O banco SQLite e as
chaves do laboratório não têm criptografia própria em repouso. Use disco protegido
e acesso restrito; não existe promessa de proteção contra administrador local.

Arquivos produzidos:

| Local | Uso e acesso |
|---|---|
| `client-build-inputs/{origin.json,public.json,tls-ca.pem,fixture.json}` | Únicos quatro insumos permitidos no build autorizado; chave pública, CA pública e fixtures sintéticas |
| `issuer.private-key`, `wrapping.private-key`, `tls-server.key` | Somente servidor, nunca cliente/Actions/diagnóstico |
| `test-accounts.json` | Contas fictícias e duas chaves por assinatura; entregue manualmente somente aos testadores autorizados |
| `license-lab.sqlite`, `server.json` | Estado local do servidor; nunca cliente ou artefato |

As contas são **`monthly@example.com`** e **`annual@example.com`**. São endereços de
exemplo, não envio de e-mail. As chaves são aleatórias por laboratório, não senha
universal. Consulte `test-accounts.json` localmente, sem transcrever chaves em logs.
Nenhum administrador remoto é criado; os endpoints administrativos permanecem
protegidos. As operações de laboratório abaixo exigem acesso local ao diretório.

## TLS sem alterar o Windows

O script gera certificado TLS de servidor **de laboratório**, com SAN correspondente
ao IP/localhost, válido por 14 dias, e CA pública por 30 dias. A chave privada da CA
não é retida. A CA pública é fixada exclusivamente no build TESTE. O cliente verifica
cadeia, validade e hostname com `CERT_REQUIRED`; rejeita outra CA e outro host.
**Não se instala certificado no Windows, não se altera o repositório de raízes e
não se desabilita validação HTTPS.** Isso não assina EXE/DLL, não dá confiança SAC,
não é certificado de produção nem compra de certificado.

Produção recusa a configuração de CA de laboratório e a chave reservada de TESTE;
continua usando HTTPS e confiança normal. O material de CI tem validade de sete dias;
compile em seguida. Após expirar TLS/fixtures, prepare um laboratório novo e recompile
com sua confiança pública. Não troque arquivos de confiança no cliente instalado.

## Iniciar e ativar

```powershell
./server-env/Scripts/python.exe -m scripts.vm_license_lab serve --directory C:/AgroLines-Privado/Lab --authorize-private-listener
```

O processo escuta somente no IPv4 configurado, HTTPS/443, sem confiar em headers de
proxy e sem access log com requisições. Se necessário, o titular pode permitir
**somente essa aplicação/porta no perfil privado e origem das VMs de teste** pelo
firewall. Não desative firewall/Defender, não libere rede pública e não abra porta no
roteador. Se a rede privada/TLS não funcionar, pare e diagnostique; não use HTTP.

Na VM cliente com o build correspondente: **Minha licença → E-mail do titular**,
use uma conta fictícia; **Chave desta vaga**, use a chave da vaga 1; nomeie
`VM TESTE 1`; clique **Ativar esta vaga**. Não é necessário importar certificados,
instalar Python ou configurar variáveis de ambiente no cliente.
Feche/reabra; desligue o adaptador virtual e confirme uso offline até o vencimento.

A confiança TESTE usa armazenamento separado em
`%LOCALAPPDATA%/AgroLines/TestProfile/license.dpapi` e âncora HKCU
`Software/AgroLines/Licensing/TestProfile`. Não apague/copíe esses dados para
simular novos computadores. Projetos/backups continuam externos ao runtime.
Não é demonstrada migração automática da ativação de teste antiga do #23.

## Mensal/anual, duas vagas e ciclo

1. Ative vaga 1 na primeira VM e vaga 2 numa **segunda instalação limpa**.
2. Numa terceira VM/instalação limpa, tente usar qualquer uma dessas chaves já
   ocupadas: deve haver recusa HTTP 409 e nenhuma terceira vaga. Clonar uma VM
   **após ativá-la** copia identidade/estado e não prova controle de três máquinas.
3. Repita com `annual@example.com`. O plano deve ser Anual e a validade diferente.
   Mensal/anual usam os cálculos de calendário existentes, sem alterar o relógio.
4. Renove no servidor e use **Verificar licença agora** no cliente:

```powershell
./server-env/Scripts/python.exe -m scripts.vm_license_lab renew --directory C:/AgroLines-Privado/Lab --plan monthly
./server-env/Scripts/python.exe -m scripts.vm_license_lab expire --directory C:/AgroLines-Privado/Lab --plan monthly
```

Após `expire`, reconecte/verifique: edição deve ser bloqueada, recuperação dos dados
preservada. A alteração no servidor não altera magicamente uma licença offline já
emitida. Para prova de vencimento já offline, antes da revogação, execute:

```powershell
./server-env/Scripts/python.exe -m scripts.vm_license_lab short-expiry --directory C:/AgroLines-Privado/Lab --plan monthly --seconds 120
```

No cliente, verifique online para receber a licença curta assinada, desconecte e
aguarde dois minutos. A edição deve ficar indisponível e recuperação preservada.
Não avance o relógio do Windows para tentar forçar o teste.

5. Instale o sucessor 1.0.0.8 na mesma pasta, confirme atualização e que ativação,
   projetos e versão anterior funcionam. Essa atualização requer o **mesmo** laboratório
   e chaves públicas; ambos instaladores são gerados na mesma execução.
6. Por último, revogue e peça verificação online:

```powershell
./server-env/Scripts/python.exe -m scripts.vm_license_lab revoke --directory C:/AgroLines-Privado/Lab --plan monthly
```

Revogação deve sobreviver ao reinício após recebida. Uma VM offline sem receber a
decisão poderá usar licença válida até vencer; não prometa revogação imediata sem rede.
Revogação é definitiva nesse fluxo: use laboratório novo para começar novamente.
Não substitua o backend de produção por esse SQLite. Encerre com Ctrl+C e remova
o estado privado somente após terminar/reter as evidências necessárias, sob controle
do titular. Nunca envie chaves/SQLite para suporte ou para um repositório público.
