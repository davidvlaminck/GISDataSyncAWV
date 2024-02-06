import json
from pathlib import Path

from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject

from voobeeldcode.EMInfraAPI.AbstractRequester import AbstractRequester
from voobeeldcode.EMInfraAPI.EMInfraImporter import EMInfraImporter
from voobeeldcode.EMInfraAPI.RequesterFactory import RequesterFactory
from voobeeldcode.Enums import AuthType, Environment


class GisDataSyncerOtlmow:
    def __init__(self, settings_path: Path, auth_type: AuthType, env: Environment):
        self.requester = self.create_requester_with_settings(
            settings_path=settings_path, auth_type=auth_type, env=env)
        self.em_infra_importer = EMInfraImporter(requester=self.requester)

    @classmethod
    def create_requester_with_settings(cls, settings_path: Path, auth_type: AuthType, env: Environment
                                       ) -> AbstractRequester:
        with open(settings_path) as settings_file:
            settings = json.load(settings_file)
        return RequesterFactory.create_requester(settings=settings, auth_type=auth_type, env=env)

    def transform_api_result_to_geojson(self, file_path: Path) -> None:

        api_response = self.em_infra_importer.get_objects_from_oslo_search_endpoint_using_iterator(
            resource='assets', filter_dict={"uuid": ['e1a42f68-f510-46f5-b587-854fa0c493df']})

        response_list = next(api_response)
        clean_dict = self.clean_dict(response_list[0])

        asset = OTLObject.from_dict(clean_dict, datetime_as_string=True)

        converter = OtlmowConverter()
        converter.create_file_from_assets(filepath=file_path, list_of_objects=[asset])

    @classmethod
    def clean_dict(cls, dict_to_clean: dict) -> dict:
        new_d = {}
        for k, v in dict_to_clean.items():
            if k in {'@context', '@id', '@type'}:
                continue
            if ':' in k:
                continue
            if '.' in k:
                k = k.split('.', 1)[-1]
            if isinstance(v, dict):
                v = cls.clean_dict(v)
            if isinstance(v, list):
                new_v = []
                for item in v:
                    if isinstance(item, dict):
                        new_v.append(cls.clean_dict(item))
                    else:
                        new_v.append(item)
                v = new_v
            new_d[k] = v
        return new_d
