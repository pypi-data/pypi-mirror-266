import sys
import unittest
import importlib.util
from types import ModuleType
from enum import Enum

from configparser import ConfigParser


class Submodule(Enum):
    MODULE = 'metalarchivist', './src/metalarchivist/__init__.py'
    EXPORT = 'metalarchivist.export', './src/metalarchivist/export/__init__.py'
    IFACE = 'metalarchivist.interface', './src/metalarchivist/interface/__init__.py'


def run_test_cases():
    unittest.main(argv=[''], verbosity=2)


def prepare_submodule(submodule: Submodule) -> ModuleType:
    submodule_name, submodule_path = submodule.value
    spec = importlib.util.spec_from_file_location(submodule_name, submodule_path)
    
    if spec is None:
        raise ModuleNotFoundError

    module = importlib.util.module_from_spec(spec)
    sys.modules[submodule_name] = module

    if spec.loader is None:
        raise ModuleNotFoundError

    spec.loader.exec_module(module)

    return module


def load_module():
    config = ConfigParser()
    config.read('metallum.cfg')

    metalarchivist = prepare_submodule(Submodule.MODULE)
    interface = prepare_submodule(Submodule.IFACE)
    export = prepare_submodule(Submodule.EXPORT)

    return metalarchivist, interface, export, config


class TestThemes(unittest.TestCase):
    
    metalarchivist, interface, export, config = load_module()

    def test_themes(self):
        themes = self.interface.Themes('National Socialism, Aryanism, Antisemitism, Anti-communism, W.A.R.')
        self.assertIsNotNone(themes)
        self.assertEqual(len(themes.phases), 5)
        self.assertEqual(themes.clean_theme, 'Anti-communism, Antisemitism, Aryanism, Nazism, White Aryan Resistance')

        themes = self.interface.Themes('Satanism, War, Hate, National Socialism, Anti-Judeo-Christianity, Racism')
        self.assertIsNotNone(themes)
        self.assertEqual(len(themes.phases), 6)
        self.assertEqual(themes.clean_theme, 'Anti-Judeo-Christianity, Hate, Nazism, Racism, Satanism, War')
        
        themes = self.interface.Themes('National Socialism, War, Winter')
        self.assertIsNotNone(themes)
        self.assertEqual(len(themes.phases), 3)
        self.assertEqual(themes.clean_theme, 'Nazism, War, Winter')

        themes = self.interface.Themes('National Socialism, Nazism')
        self.assertIsNotNone(themes)
        self.assertEqual(len(themes.phases), 1)
        self.assertEqual(themes.clean_theme, 'Nazism')

        themes = self.interface.Themes('Satanism, Anti-Christianity, Death, Genocide, Hatred, National Socialism')
        self.assertIsNotNone(themes)
        self.assertEqual(len(themes.phases), 6)
        self.assertEqual(themes.clean_theme, 'Anti-Christianity, Death, Genocide, Hatred, Nazism, Satanism')
