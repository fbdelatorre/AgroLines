ROLE_NAMES = {
    "owner": "Proprietário",
    "administrator": "Administrador",
    "editor": "Editor",
    "operator": "Operador",
    "viewer": "Visualizador",
}
ROLE_DESCRIPTIONS = {
    "viewer": "Consulta os dados do escopo concedido, sem alterações.",
    "operator": (
        "Consulta o escopo concedido. A exportação de planos será disponibilizada em etapa futura."
    ),
    "editor": "Consulta e modifica os dados do escopo concedido.",
    "administrator": (
        "Gerencia cadastros, usuários e permissões "
        "da propriedade inteira. Não transfere titularidade."
    ),
}
STATUSES = {
    "pending": "Pendente",
    "accepted": "Aceito",
    "declined": "Recusado",
    "revoked": "Revogado",
    "expired": "Expirado",
}
SECTIONS = (
    "Painel",
    "Produtores",
    "Fazendas",
    "Talhões",
    "Safras",
    "Operações",
    "Máquinas",
    "Implementos",
    "Planejamentos",
    "Exportações",
    "Configurações",
)


def scope_text(scope):
    if scope.get("operation_id"):
        return (
            f"{scope['season_name']} · {scope['operation_name']}"
            if scope.get("season_name") and scope.get("operation_name")
            else "Escopo indisponível"
        )
    if scope.get("season_id"):
        return scope.get("season_name") or "Safra indisponível"
    return "Propriedade inteira"
