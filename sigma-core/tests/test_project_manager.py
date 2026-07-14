import unittest
import importlib.util

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

project=load("project","sigma-core/managers/project_manager.py")
engine=load("engine","sigma-core/engine.py")

class ProjectManagerTests(unittest.TestCase):

    def test_manager_exists(self):
        pm=project.ProjectManager(engine.engine)
        self.assertIsNotNone(pm)

if __name__=="__main__":
    unittest.main()
