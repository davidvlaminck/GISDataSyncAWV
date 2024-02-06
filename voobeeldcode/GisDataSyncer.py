import json
from pathlib import Path

from requests import Session

from voobeeldcode.EMInfraAPI.EMInfraImporter import EMInfraImporter
from voobeeldcode.EMInfraAPI.RequesterFactory import RequesterFactory
from voobeeldcode.Enums import AuthType, Environment


class GisDataSyncer:
    def __init__(self, settings_path: Path, auth_type: AuthType, env: Environment):
        self.requester = self.create_requester_with_settings(
            settings_path=settings_path, auth_type=auth_type, env=env)
        self.em_infra_importer = EMInfraImporter(requester=self.requester)

    @classmethod
    def create_requester_with_settings(cls, settings_path: Path, auth_type: AuthType, env: Environment
                                       ) -> Session:
        with open(settings_path) as settings_file:
            settings = json.load(settings_file)
        return RequesterFactory.create_requester(settings=settings, auth_type=auth_type, env=env)
