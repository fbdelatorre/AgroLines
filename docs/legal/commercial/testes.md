# Matriz de aceitação executável

Dados sintéticos, sem cliente real, cobrança ou serviço público. Comandos:

```sh
pytest tests/test_commercial_licensing.py tests/test_license_network.py tests/test_commercial_desktop.py
pytest tests/test_legal_materials.py tests/test_source_delivery.py tests/test_standalone.py
python -m scripts.precision_report --output precision-report.json
```

| Caso solicitado | Evidência implementada | Limite |
|---|---|---|
|1 Primeira ativação online | test_full_lifecycle_two_seats_offline_renewal_revocation; APIHTTPS in-process | TLS/domain público ainda a configurar/testar |
|2 Primeira ativação offline recusada | mesmo teste, transporte indisponível e recuperação semgeometry | Não há licença automática/desenvolvimento no perfil comercial |
|3 Segundo PC aceito | duas vagas, mesma subscription_id/validade | UUID/DPAPI não é atestado de hardware |
|4 Terceiro recusado | ambas as chaves ocupadas devolvem409; testePostgreSQL concorrente | Réplicas deliberadamente adulteradas poradmin não são impedidas de forma absoluta |
|5/6 Chave inválida/outro usuário | test_bad_key_owner_expiry_tampering_and_copy | Sem e-mail real enviado ou autenticação de caixa postal presumida |
|7 Vencimento | mesmo teste; servidor recusa e cliente entra emrecuperação | Não apaga projetos |
|8 Renovação | anual/mensal porcalendário, emissão comnova revisão | Sem cobrança real ou gateway |
|9 Revogação online | assinatura/ativação e resposta assinada | Offline só aprende ao conectar/expirar |
|10/11 Uso offline/rede indisponível | primeira prova e provaWindows congelada | Licença continua até expires_at, sem heartbeat obrigatório |
|12 Servidor503 | test_server_maintenance_does_not_revoke_a_valid_local_license | Sem garantiaSLA inventada |
|13 Cópia para outra instalação | verify comUUID divergente falha; DPAPI é ensaiado noWindows | Copiar todas as credenciais poradmin é outra ameaça, não prometemosDRM perfeito |
|14 Alteração local | assinatura/payload/algoritmo inválidos; guard/response corrompidos recusados | Não se usaJSONeditável como licença |
|15 Retrocesso do relógio | teste de relógio e correção somente comnova resposta de servidor | Não impede todo rollback de imagem poradmin |
|16/17 Substituição/desativação | rotação controlada da chave e revogação antiga | Computador antigo offline conserva validade até conhecer decisão/vencer |
|18 Revogação persistida | restauração do arquivo anterior não remove registro independente | Não é prova contra restauração completa deWindows/registro |
|19 Reinstalação | recarga do mesmo vault/âncora preservaUUID; DPAPI congelado | Instalação/desinstalação física do setup continua pendente |
|Duas instâncias abertas | testesde recarga/mescla e resposta atrasada; provaWindows comdois processos congelados eDPAPI/mutex | Não instala nem altera registroWindows protegido; usa chaveLab própria descartável |
|20 Atualização | estado fora da versão, reabertura e verificações do launcher | Ciclo de setup confiável real ainda não executado |
|Salvar GIS emandamento após expirar | test_already_started_vertex_edit_can_save_after_license_expires | Permissão capturada sópara a operação iniciada |
|Recuperar semativação válida | test_recovery_shell_can_open_existing_project_without_activation | Não permite criar/importar/iniciar novas edições |
|Usuário não escolhe validade | campoextra expires_at recusado; rotasadmin exigemMFA | Administração deve estar isolada na implantação |
|Revogado não recebe nova lista de máquinas | test_client_cannot_choose_expiry_and_revoked_seat_cannot_list_other_devices | Mantém direito de recuperar seus arquivos locais |
|Administração | MFA, antirreplay, viewer semescrita, auditoria, correção autenticada | Recuperação de conta e segregação operacional precisam configuração |
|Rede limitada | subprocessos: contexto/thread/origem/porta eStore fechado; TLSverify/redirects | TraceWindows nativo e infraestruturaTLS reais ainda requeremhomologação |
|Materiais jurídicos | licença/versão/hash/recursos/kit/fontesextras/HTML/TXT | Testes não aprovam interpretação jurídica |

As suítes gerais preservam importaçãoSHP/GPKG/KML/KMZ/GeoJSON, edição, undo/redo,
histórico,SQLite, backup/restauração, WebEngine/Leaflet offline e22referências.
WindowsActions usaServer descartável com proteções preservadas; não éWindows11/SAC.
O script `commercial_probe` só executa no build experimental comchave pública
sintética e guardas de ambiente. Sua entrada não é aceita pelo perfil de produção.
Não é possível trocar umbuildStore fechado para comercial porconfiguração local.

Antes de produção: repetir comendpointHTTPS real, certificado público válido,
rede fisicamente desconectada depois da ativação e instalador legitimamenteconfiável.
Incluir timeout/falha503, dois PCs reais, terceiro, renovação, revogação e recuperação
de dados, atualização e desinstalação, evidenciandoWindows/SAC/Defender semalterações.
