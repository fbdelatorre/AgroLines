# SAC/Store — coleta somente de leitura e teste físico futuro

**Não executado em Windows 11 físico. Não há aprovação SAC.** Hosted Windows que
compila consumidores sintéticos não representa instalação sob identidade Store,
nem computador sem Python, nem SAC On. Não executar os binários sintéticos em
máquina protegida se o Windows os bloquear; guardar a falha, sem contorná-la.

O novo coletor `tools/windows-lgpl-lab/Collect-Homologation.ps1` reutiliza
`scripts/Windows-Security.ps1` e
`distribution/windows/signing/Test-StoreDeliveredTrust.ps1`. Não instala/ativa
aplicativos, certificados ou catálogos, não habilita logs, não altera registro,
Defender/SAC/Developer Mode, não abre rede nem envia evidências. Só escreve em um
**novo diretório local fora do pacote e do repositório**.

## Antes e depois da sessão

1. Apenas após o roteiro de autorização Store, usar máquina Windows 11 real e
   instalação legítima. Em **Windows Security → App & browser control → Smart App
   Control**, registrar **On**, não Evaluation. Defender deve permanecer ativo.
   A interface é a verificação documentada pelo [overview oficial](https://learn.microsoft.com/en-us/windows/apps/develop/smart-app-control/overview).
2. Guardar o horário de início e o registro da obtenção pela Store, sem credenciais
   ou contas de testadores. Guardar evidência visual da versão do Windows/estado SAC.
   Não alterar a configuração para obter o resultado esperado.
3. Rodar PowerShell já permitido pela máquina (não alterar ExecutionPolicy), por
   exemplo, na cópia dos scripts revisados:

```powershell
./tools/windows-lgpl-lab/Collect-Homologation.ps1 -OutputDirectory "$env:LOCALAPPDATA/AgroLines-Homologacao/antes-001" -Since (Get-Date).AddMinutes(-10)
```

4. Desconectar fisicamente rede/Wi-Fi para a sessão funcional autorizada. Abrir pelo
   menu Iniciar, importar fixtures inteiramente sintéticas SHP/GPKG/KML/KMZ/GeoJSON,
   editar vértices, undo/redo, salvar, fechar, reabrir, consultar versões e restaurar
   backup. Registrar resultados e valores/precisão, horário e eventuais falhas.
   Não copiar projetos reais para diagnóstico. Usar planilha/JSON manual por etapa
   com `passed/failed/not_run` e observações, sem inventar aprovação automática.
5. Coletar novamente em pasta nova, fornecendo opcionalmente arquivo funcional e
   log de inicialização **sem segredos/dados reais**, ambos <=10 MB:

```powershell
./tools/windows-lgpl-lab/Collect-Homologation.ps1 -OutputDirectory "$env:LOCALAPPDATA/AgroLines-Homologacao/depois-001" -Since $inicioDoTeste -FunctionalEvidence ./resultado-sintetico.json -StartupLog ./inicializacao-sintetica.txt
```

`$inicioDoTeste` é a variável definida pelo operador no início da sessão atual;
a janela deve ser das últimas 24h. Não são comandos para instalar o diagnóstico.
Se um script/consulta for bloqueado, registrar e parar essa etapa; não usar flags
para desativar verificações. Teste do usuário não exige instalar Python ou PG.

## O que os arquivos comprovam — e o que não comprovam

| Evidência | Interpretação |
| --- | --- |
| OS Caption/Version/Build/Architecture | Identifica máquina, distingue Server do laboratório e Windows 11 físico |
| SAC registry + `CiTool -lp -json` | Evidência auxiliar somente de leitura; [CiTool documentado](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/operations/citool-commands). O helper correlaciona estado/política; leitura indisponível/inconclusiva não é On. Confirmar também a interface documentada. |
| Get-MpComputerStatus | Estado observado do Defender, sem modificá-lo |
| Get-AppxPackage | Name/Publisher/PFN/versão/arquitetura/Status/SignatureKind/DevelopmentMode/caminho; origem Store exige também o registro da obtenção, não só um nome igual |
| SignTool dos PE | Assinatura embutida com `/pa /all /v /tw`; resultado por arquivo, não inferência global |
| Catálogo, se existir | Verifica assinatura do CodeIntegrity.cat e **pertencimento criptográfico de cada arquivo** com `/c`. Não basta encontrar o catálogo. Ausência/não cobertura não equivale automaticamente a rejeição SAC; exige resultado real. |
| CodeIntegrity 3077/3033, AppModel-Runtime/Admin e Application | Eventos relacionados por identidade/nome nativo, no intervalo; Application pode registrar falhas de DLL/Windows Error Reporting. Falso positivo por nome comum exige revisão. Log desabilitado, acesso negado e consulta sem eventos são estados distintos. Não habilitamos canais nem prometemos detectar toda falha de DLL. |
| Resultado funcional/log fornecidos pelo operador | São copiados e recebem hash; o coletor **não valida** sua veracidade nem gera testes aprovados |

SDK/SignTool ausentes ou falha de consulta são registrados como inspeção incompleta;
não instalar ferramentas adicionais silenciosamente nem declarar tudo confiável.
O coletor conserva os eventos em pasta privada: podem conter caminhos pessoais,
outros aplicativos e detalhes de falhas. **Não commitar/reenviar automaticamente.**
Minimizar/redigir antes de compartilhar, seguir retenção de suporte aplicável.

Não existe captura de rede/ETW completa neste coletor. Snapshot, ausência de evento,
assinatura válida e testes unitários offline não comprovam ausência de toda conexão
nativa. A homologação requer teste físico desconectado, operações reais e investigação
específica de qualquer bloqueio. Atualização/desinstalação são verificações separadas
com cópias de segurança e pacotes legítimos. Campos `sac_approved` e
`submission_authorized` permanecem **false**, inclusive quando a coleta termina.
