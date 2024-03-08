from pathlib import Path

from voobeeldcode.Enums import AuthType, Environment
from voobeeldcode.GisDataSyncerOtlmow import GisDataSyncerOtlmow

# settings_path = Path('/home/davidlinux/Documents/AWV/resources/settings_GISDataSync.json')
settings_path = r"C:\GoogleTeamDrive\GIStools\Python_scripts\Projecten\GISDataSyncAWV\voobeeldcode\settings_sample.json"

if __name__ == '__main__':
    syncer = GisDataSyncerOtlmow(settings_path=settings_path, auth_type=AuthType.CERT, env=Environment.PRD)

    syncer.transform_api_result_to_geojson(file_path=Path('example.geojson'))

