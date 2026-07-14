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
Identity = load("identity","sigma-core/managers/identity_manager.py")
Workspace = load("workspace","sigma-core/managers/workspace_manager.py")
Service = load("service","sigma-core/managers/service_manager.py")
Logger = load("logger","sigma-core/managers/logger_manager.py")
Event = load("event","sigma-core/managers/event_manager.py")

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
        self.identity = Identity.IdentityManager(self)
        self.workspace = Workspace.WorkspaceManager(self)
        self.service = Service.ServiceManager(self)
        self.logger = Logger.LoggerManager(self)
        self.event = Event.EventManager(self)

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
            "identity": self.identity,
            "workspace": self.workspace,
            "service": self.service,
            "logger": self.logger,
            "event": self.event,
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
