class BaseManager:
    def __init__(self, engine):
        self.engine = engine

    @property
    def root(self):
        return self.engine.root

    @property
    def db(self):
        return self.engine.db

    @property
    def projects_dir(self):
        return self.engine.projects_dir

    @property
    def config(self):
        return self.engine.config

    @property
    def local_config(self):
        return self.engine.local_config

    @property
    def local_config_migration(self):
        return self.engine.local_config_migration

    @property
    def identity(self):
        return self.engine.identity

    @property
    def context(self):
        return self.engine.context

    @property
    def workspace(self):
        return self.engine.workspace

    @property
    def logger(self):
        return self.engine.logger

    @property
    def service(self):
        return self.engine.service

    @property
    def event(self):
        return self.engine.event

    @property
    def task(self):
        return self.engine.task

    @property
    def plugin(self):
        return self.engine.plugin

    @property
    def registry(self):
        return self.engine.registry

    @property
    def database(self):
        return self.engine.database

    @property
    def projects(self):
        return self.engine.projects

    @property
    def nodes(self):
        return self.engine.nodes

    @property
    def packages(self):
        return self.engine.packages

    @property
    def templates(self):
        return self.engine.templates

    @property
    def releases(self):
        return self.engine.releases

    @property
    def api(self):
        return self.engine.api

    @property
    def sync(self):
        return self.engine.sync

    def manager(self, name):
        return self.engine.manager(name)
