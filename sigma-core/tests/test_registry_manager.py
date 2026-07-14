import unittest
import importlib.util

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

registry=load("registry","sigma-core/managers/registry_manager.py")
engine=load("engine","sigma-core/engine.py")

class RegistryManagerTests(unittest.TestCase):

    def test_manager_exists(self):
        pm=registry.RegistryManager(engine.engine)
        self.assertIsNotNone(pm)

if __name__=="__main__":
    unittest.main()
