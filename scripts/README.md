# Scripts
`Configure.ps1 [-Desktop]`: ambiente Python 3.12 e dependências no Windows.
`Start-Server.ps1`: conexão com PostgreSQL, migração aditiva e API em loopback;
senha solicitada de forma protegida quando a URL não estiver configurada.
`integration_check.py`: fluxo HTTP real com dados sintéticos, para banco de teste migrado.
Comandos e configuração no README. Scripts nunca recriam o banco automaticamente.

`native_inventory.py`: inventário com hashes, sem importar módulos nativos.
`Audit-NativeWindows.ps1`: Authenticode e cadeia, somente leitura.
`Test-SmartAppControl.ps1`: probes Windows 11/SAC ativo e eventos 3077/3033 por teste,
sem alterar proteções. Procedimento e limitações em [segurança Windows](../docs/windows-security.md).
Esses scripts são de mantenedores; não constituem instalador para clientes.
