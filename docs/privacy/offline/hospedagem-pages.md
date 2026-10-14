# Hospedagem gratuita preparada, sem publicação

Foi preparado `.github/workflows/privacy-pages.yml`, com execução exclusivamente
manual e recusa de textos com `[CONFIRMAR:` ou `NÃO PUBLICAR`. Não foi executado,
não configuramos Pages nem enviamos e-mails. Só publica o HTML estático da política,
sem projetos, termos internos, scripts, fontes externas ou analytics próprios.

Após revisão e autorização do responsável:

1. Resolver bases legais, fornecedores/transferências e medidas operacionais.
   Preencher data da primeira disponibilização e URL pretendida da política;
   retirar o aviso de revisão somente com texto efetivamente aprovado.
2. Conferir a visibilidade do repositório e disponibilidade gratuita de Pages para
   a conta. Em Settings / Pages selecionar GitHub Actions e revisar permissões e
   ambiente github-pages. Esta alteração não foi feita por esta tarefa.
3. Revisar o diff e executar manualmente o workflow na revisão aprovada, informando
   `PUBLICAR_POLITICA_REVISADA`. Isso publica apenas a política, não o aplicativo.
4. Usar a URL retornada pelo deploy. Se a configuração padrão de project site for
   aplicável, a candidata é `https://fbdelatorre.github.io/AgroLines/`; **não é URL
   confirmada nem acessível demonstrada nesta tarefa**. Ajustar a URL no texto se
   o deploy retornar endereço diferente e republicar a política aprovada.
5. Testar em navegador sem login e outro acesso de rede: HTTPS válido, HTTP 200,
   texto correto em português, sem campos pendentes e sem recursos externos.
   Guardar data, URL, revisão e resultado. Só então fornecer ao Partner Center.
6. Atualizar o HTML/TXT local e gerar o MSIX correspondente ao texto aprovado.
   Avisar mudanças relevantes manualmente por e-mail a contatos legitimamente
   disponíveis, após autorização; não usar ferramenta de envio automático.

A Store exige URL de privacidade (política 10.5.1). O TXT é auxiliar e não substitui
essa URL. A hospedagem envolve o GitHub como fornecedor: revisar sua declaração e
transferências, sem afirmar que a página pública é um recurso offline do aplicativo.
