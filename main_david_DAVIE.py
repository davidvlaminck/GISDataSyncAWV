import json
from pathlib import Path

from voobeeldcode.EMInfraAPI.AbstractRequester import AbstractRequester
from voobeeldcode.EMInfraAPI.DavieCoreClient import DavieCoreClient
from voobeeldcode.EMInfraAPI.LS2Client import LS2Client
from voobeeldcode.EMInfraAPI.RequesterFactory import RequesterFactory
from voobeeldcode.Enums import AuthType, Environment

settings_path = Path('/home/davidlinux/Documents/AWV/resources/settings_GISDataSync.json')


def create_requester_with_settings(settings_path: Path, auth_type: AuthType, env: Environment, **kwargs
                                   ) -> AbstractRequester:
    with open(settings_path) as settings_file:
        settings = json.load(settings_file)
    return RequesterFactory.create_requester(settings=settings, auth_type=auth_type, env=env, **kwargs)


if __name__ == '__main__':
    requester = create_requester_with_settings(cookie='d9b0fdba990a4891a450d80c6c99ab62',
                                               settings_path=settings_path, auth_type=AuthType.COOKIE,
                                               env=Environment.PRD)
    davie_client = DavieCoreClient(requester=requester)

    print(davie_client.aanlevering_by_id(id='247114da-80f6-489d-9faa-ac0f5254970b'))
    print(davie_client.historiek_by_aanlevering_id(id='247114da-80f6-489d-9faa-ac0f5254970b'))
