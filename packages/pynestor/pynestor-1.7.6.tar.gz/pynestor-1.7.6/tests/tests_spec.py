import unittest
from dataclasses import dataclass
from unittest.mock import patch

from pynestor.preview_odoo_nestor import (
    EnvironementConfig,
    PreviewUpScript,
    PreviewUtils,
)
from pynestor.pynestor import NestorDescSet, NestorOpt


def _create_all_spec_sources(project_path):
    return NestorDescSet([NestorOpt("sources.branch", "test_branch")])


@dataclass
class MockInstance:
    name: str = "test"
    url: str = "test"
    existing: bool = True
    password: str = "test"
    verbose: bool = False
    filestore = None
    db = None
    spec = {}

    def exist(self):
        return self.existing

    def version(self, values):
        return 15.0

    def install(self, modules: str):
        pass

    def update(self, modules: str):
        pass

    def delete_and_exit_if_failed(self, return_code: int):
        pass

    def wait(self, up: bool = True, postgres: bool = True, timeout=0):
        pass

    def start(self):
        pass

    def direct_call(self, cde=""):
        pass

    def create(self, odoo_version: str = None, values_set: NestorDescSet = None):
        return type(self)()

    def set_memory_worker(self, workers: int = None, memory_hard: int = None, memory_soft: int = None):
        pass

    @staticmethod
    def list():
        pass

    def edit(self, values_set: NestorDescSet = None):
        pass

    def db_restore_from_s3(
        self,
        dump_path: str,
        alt_dump_path: str = None,
        s3_secret: str = None,
        bucket: str = None,
        set_password_to_all: bool = False,
        verbose: bool = False,
    ):
        pass


class TestEnvironment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env_dict = {
            "ENABLE_QUEUE_JOB": "True",
            "NESTOR_NAME": "test",
            "CI_PROJECT_DIR": "../src",
            "CI_BUILD_DIR": "./",
            "CI_PROJECT_PATH": "odoo/",
            "GITLAB_TOKEN": "test_token",
            "ODOO_VERSION": "15.0",
            "CI_COMMIT_REF_NAME": "test_mr",
        }

    def prepare_script(self, env_dict):
        config = EnvironementConfig(env_dict)
        config.apply_default()
        script = PreviewUpScript(config)
        return script

    def test_default_env(self):
        env_dict = self.env_dict.copy()
        script = self.prepare_script(env_dict)
        with patch.object(PreviewUtils, "_create_all_spec_sources") as mock_method:
            mock_method.return_value = NestorDescSet([NestorOpt("sources.branch", "test_branch")])
            values = script.get_spec_values(stage="restore")
        script.log_spec(values)
        self.assertTrue(values["options.queueJobs.enabled"].value)
        # values contient des NestorOpt; NestorOpt.value retourne la chaine
        self.assertEqual(values["options.queueJobs.channels"].value, "root:1")

    def test_always_restore(self):
        env_dict = self.env_dict.copy()
        env_dict.update({"ALWAYS_RESTORE": "True"})
        script = self.prepare_script(env_dict)
        script.inst = MockInstance()
        with patch.object(PreviewUtils, "_create_all_spec_sources") as mock_method:
            mock_method.return_value = NestorDescSet([NestorOpt("sources.branch", "test_branch")])
            with patch.object(type(script), "restore_db") as mock_restore_db:
                with patch.object(type(script), "stop") as mock_stop:
                    with patch.object(type(script), "edit_with_values") as mock_edit_with_values:
                        script.run_script()
                        mock_restore_db.assert_called_with()

    def test_always_restore_false(self):
        env_dict = self.env_dict.copy()
        env_dict.update({"ALWAYS_RESTORE": "false"})
        script = self.prepare_script(env_dict)
        script.inst = MockInstance()
        with patch.object(PreviewUtils, "_create_all_spec_sources") as mock_method:
            mock_method.return_value = NestorDescSet([NestorOpt("sources.branch", "test_branch")])
            with patch.object(type(script), "restore_db") as mock_restore_db:
                with patch.object(type(script), "stop") as mock_stop:
                    with patch.object(type(script), "edit_with_values") as mock_edit_with_values:
                        script.run_script()
                        mock_restore_db.assert_not_called()
