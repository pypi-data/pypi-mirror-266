import unittest
from click.testing import CliRunner

from lumipy.cli.commands.setup import setup


class TestCli(unittest.TestCase):

    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_setup_domain(self):
        result = self.runner.invoke(setup)
        self.assertIn("Setting up python providers", result.stdout)

    def test_setup_domain_with_domain(self):
        result = self.runner.invoke(setup, ['--domain', 'fbn-ci'])
        self.assertIn("Setting up python providers", result.stdout)
