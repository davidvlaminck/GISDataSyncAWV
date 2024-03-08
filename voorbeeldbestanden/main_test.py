import json
from pathlib import Path

from otlmow_model.OtlmowModel.Classes.Onderdeel.Boom import Boom

from voobeeldcode.Enums import AuthType, Environment
from voobeeldcode.GisDataSyncerOtlmow import GisDataSyncerOtlmow


settings_path = r"C:\toegang\settings_gisdatasync.json"



if __name__ == '__main__':
    syncer = GisDataSyncerOtlmow(settings_path=settings_path, auth_type=AuthType.CERT, env=Environment.PRD)

    syncer.transform_api_result_to_geojson(file_path=Path('example.geojson'))