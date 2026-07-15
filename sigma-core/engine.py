from pathlib import Path
from datetime import datetime
import json
import importlib.util

ROOT = Path.cwd()

def load(name, relative):
    spec = importlib.util.spec_from_file_location(
        name,
        ROOT / relative
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

Database = load("database","sigma-core/managers/database_manager.py")
Project  = load("project","sigma-core/managers/project_manager.py")
Node     = load("node","sigma-core/managers/node_manager.py")
Package  = load("package","sigma-core/managers/package_manager.py")
Registry = load("registry","sigma-core/managers/registry_manager.py")
Template = load("template","sigma-core/managers/template_manager.py")
Release  = load("release","sigma-core/managers/release_manager.py")
Api       = load("api","sigma-core/managers/api_manager.py")
Config   = load("config","sigma-core/managers/config_manager.py")
DatabaseConfig = load(
    "database_config",
    "sigma-core/managers/database_config_manager.py"
)
DataProvider = load(
    "data_provider",
    "sigma-core/managers/data_provider_manager.py"
)
NotionProvider = load(
    "notion_provider",
    "sigma-core/managers/data_providers/notion_provider.py"
)
LocalConfig = load(
    "local_config",
    "sigma-core/managers/local_config_manager.py"
)
LocalConfigMigration = load(
    "local_config_migration",
    "sigma-core/managers/local_config_migration_manager.py"
)
Identity = load("identity","sigma-core/managers/identity_manager.py")
Context = load(
    "context_manager",
    "sigma-core/managers/context_manager.py"
)
Authorization = load(
    "authorization_manager",
    "sigma-core/managers/authorization_manager.py"
)
Organization = load(
    "organization_manager",
    "sigma-core/managers/organization_manager.py"
)
User = load(
    "user_manager",
    "sigma-core/managers/user_manager.py"
)
Membership = load(
    "membership_manager",
    "sigma-core/managers/membership_manager.py"
)
Authentication = load(
    "authentication_manager",
    "sigma-core/managers/authentication_manager.py"
)
Session = load(
    "session_manager",
    "sigma-core/managers/session_manager.py"
)

Device = load(
    "device_manager",
    "sigma-core/managers/device_manager.py"
)
Workspace = load("workspace","sigma-core/managers/workspace_manager.py")
Service = load("service","sigma-core/managers/service_manager.py")
Logger = load("logger","sigma-core/managers/logger_manager.py")
Event = load("event","sigma-core/managers/event_manager.py")
Task = load("task","sigma-core/managers/task_manager.py")
Plugin = load("plugin","sigma-core/managers/plugin_manager.py")
Sync = load(
    "sync_manager",
    "sigma-core/managers/sync_manager.py"
)

class SigmaEngine:

    def __init__(self):

        self.root = ROOT
        self.db = ROOT / "sigma-db"
        self.projects_dir = ROOT / "sigma-projects"

        self.database = Database.DatabaseManager(self)
        self.projects = Project.ProjectManager(self)
        self.nodes = Node.NodeManager(self)
        self.packages = Package.PackageManager(self)
        self.registry = Registry.RegistryManager(self)
        self.templates = Template.TemplateManager(self)
        self.releases = Release.ReleaseManager(self)
        self.api = Api.ApiManager(self)
        self.config = Config.ConfigManager(self)
        self.database_config = DatabaseConfig.DatabaseConfigManager(self)
        self.data_provider = DataProvider.DataProviderManager(self)
        self.notion_provider = NotionProvider.NotionProvider(
            token=self.config.get(
                "notion_token",
                ""
            ),
            database_id=self.config.get(
                "notion_database_id",
                ""
            ),
        )
        self.data_provider.register(
            "notion",
            self.notion_provider
        )
        self.local_config = LocalConfig.LocalConfigManager(self)
        self.local_config_migration = LocalConfigMigration.LocalConfigMigrationManager(self)
        self.identity = Identity.IdentityManager(self)
        self.context = Context.ContextManager(self)
        self.authorization = Authorization.AuthorizationManager(self)
        self.organization = Organization.OrganizationManager(self)
        self.user = User.UserManager(self)
        self.membership = Membership.MembershipManager(self)
        self.authentication = Authentication.AuthenticationManager(self)
        self.session = Session.SessionManager(self)
        self.device = Device.DeviceManager(self)
        self.workspace = Workspace.WorkspaceManager(self)
        self.service = Service.ServiceManager(self)
        self.logger = Logger.LoggerManager(self)
        self.event = Event.EventManager(self)
        self.task = Task.TaskManager(self)
        self.plugin = Plugin.PluginManager(self)
        self.sync = Sync.SyncManager(self)

        self.managers = {
            "database": self.database,
            "projects": self.projects,
            "nodes": self.nodes,
            "packages": self.packages,
            "registry": self.registry,
            "templates": self.templates,
            "releases": self.releases,
            "api": self.api,
            "config": self.config,
            "database_config": self.database_config,
            "data_provider": self.data_provider,
            "notion_provider": self.notion_provider,
            "local_config": self.local_config,
            "local_config_migration": self.local_config_migration,
            "identity": self.identity,
            "context": self.context,
            "authorization": self.authorization,
            "organization": self.organization,
            "user": self.user,
            "membership": self.membership,
            "authentication": self.authentication,
            "session": self.session,
            "device": self.device,
            "workspace": self.workspace,
            "service": self.service,
            "logger": self.logger,
            "event": self.event,
            "task": self.task,
            "plugin": self.plugin,
            "sync": self.sync,
        }

    def manager(self, name):

        try:
            return self.managers[name]
        except KeyError:
            available = ", ".join(sorted(self.managers.keys()))
            raise KeyError(
                f"Unknown manager '{name}'. Available managers: {available}"
            )

    def load_json(self, path):

        p = Path(path)

        if not p.exists():
            return []

        txt = p.read_text(encoding="utf-8").strip()

        if txt == "":
            return []

        return json.loads(txt)

    def save_json(self, path, data):

        Path(path).write_text(
            json.dumps(data, indent=4),
            encoding="utf-8"
        )

    def now(self):
        return datetime.now().isoformat()

engine = SigmaEngine()
