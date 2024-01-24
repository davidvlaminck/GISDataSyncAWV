from pathlib import Path

from voobeeldcode.Enums import AuthType, Environment
from voobeeldcode.GisDataSyncer import GisDataSyncer

settings_path = Path('/home/davidlinux/Documents/AWV/resources/settings_GISDataSync.json')

if __name__ == '__main__':
    syncer = GisDataSyncer(settings_path=settings_path, auth_type=AuthType.JWT, env=Environment.PRD)

    assets_page = next(syncer.em_infra_importer.get_objects_from_oslo_endpoint_with_iterator(resource='assets'))
    print(assets_page)


