import os
import sys
import json
import unittest
import importlib.util
from types import ModuleType
from enum import Enum
from typing import Mapping

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
        self.assertEqual(themes.clean_theme, 'Nazism, Aryanism, Antisemitism, Anti-communism, White Aryan Resistance')
