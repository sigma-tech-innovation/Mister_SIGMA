import unittest
import importlib.util

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

release=load("release","sigma-core/managers/release_manager.py")
engine=load("engine","sigma-core/engine.py")

class ReleaseManagerTests(unittest.TestCase):

    def test_manager_exists(self):
        pm=release.ReleaseManager(engine.engine)
        self.assertIsNotNone(pm)

if __name__=="__main__":
    unittest.main()
