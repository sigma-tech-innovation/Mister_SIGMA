class AuthorizationManager:
    """
    Gestion centralisée des rôles et permissions Sigma.

    Ce premier socle RBAC fonctionne localement à partir du contexte
    unifié. PostgreSQL et l'API deviendront ensuite les sources de
    vérité des appartenances, rôles et permissions partagées.
    """

    ROLE_PERMISSIONS = {
        "administrator": {
            "*",
        },
        "owner": {
            "*",
        },
        "manager": {
            "context.read",
            "identity.read",
            "workspace.read",
            "workspace.update",
            "project.read",
            "project.create",
            "project.update",
            "project.delete",
            "registry.read",
            "registry.update",
            "node.read",
            "node.register",
            "package.read",
            "template.read",
            "release.read",
            "sync.read",
            "sync.execute",
            "user.read",
            "membership.read",
        },
        "developer": {
            "context.read",
            "identity.read",
            "workspace.read",
            "project.read",
            "project.create",
            "project.update",
            "registry.read",
            "node.read",
            "node.register",
            "package.read",
            "package.create",
            "template.read",
            "release.read",
            "sync.read",
            "sync.execute",
        },
        "operator": {
            "context.read",
            "identity.read",
            "workspace.read",
            "project.read",
            "registry.read",
            "node.read",
            "node.register",
            "package.read",
            "template.read",
            "release.read",
            "sync.read",
            "sync.execute",
        },
        "viewer": {
            "context.read",
            "identity.read",
            "workspace.read",
            "project.read",
            "registry.read",
            "node.read",
            "package.read",
            "template.read",
            "release.read",
            "sync.read",
        },
    }

    DEFAULT_ROLE = "viewer"

    def __init__(self, engine):
        self.engine = engine

    def role(self):
        role = self.engine.context.get(
            "role",
            self.DEFAULT_ROLE
        )

        if not role:
            return self.DEFAULT_ROLE

        return str(role).strip().lower()

    def roles(self):
        return sorted(self.ROLE_PERMISSIONS)

    def role_exists(self, role):
        return (
            str(role).strip().lower()
            in self.ROLE_PERMISSIONS
        )

    def permissions(self, role=None):
        selected_role = (
            str(role).strip().lower()
            if role is not None
            else self.role()
        )

        permissions = self.ROLE_PERMISSIONS.get(
            selected_role,
            set()
        )

        return sorted(permissions)

    def has_permission(self, permission, role=None):
        permissions = set(
            self.permissions(role)
        )

        return (
            "*" in permissions
            or permission in permissions
        )

    def require(self, permission, role=None):
        if not self.has_permission(
            permission,
            role
        ):
            selected_role = (
                str(role).strip().lower()
                if role is not None
                else self.role()
            )

            raise PermissionError(
                "Permission denied: "
                f"role={selected_role}, "
                f"permission={permission}"
            )

        return True

    def can(self, action, resource, role=None):
        return self.has_permission(
            f"{resource}.{action}",
            role
        )

    def validate(self):
        role = self.role()
        exists = self.role_exists(role)

        errors = []

        if not exists:
            errors.append(
                f"Unknown role: {role}"
            )

        return {
            "valid": exists,
            "role": role,
            "permissions": (
                self.permissions(role)
                if exists
                else []
            ),
            "errors": errors,
        }

    def snapshot(self):
        validation = self.validate()

        return {
            "organization_id": (
                self.engine.context.organization_id()
            ),
            "user_id": (
                self.engine.context.user_id()
            ),
            "workspace_id": (
                self.engine.context.workspace_id()
            ),
            "role": validation["role"],
            "permissions": validation["permissions"],
            "valid": validation["valid"],
            "errors": validation["errors"],
        }
