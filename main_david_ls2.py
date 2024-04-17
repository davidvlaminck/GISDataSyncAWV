import json
from pathlib import Path

from voobeeldcode.EMInfraAPI.AbstractRequester import AbstractRequester
from voobeeldcode.EMInfraAPI.LS2Client import LS2Client
from voobeeldcode.EMInfraAPI.RequesterFactory import RequesterFactory
from voobeeldcode.Enums import AuthType, Environment

settings_path = Path('/home/davidlinux/Documents/AWV/resources/settings_GISDataSync.json')


def create_requester_with_settings(settings_path: Path, auth_type: AuthType, env: Environment
                                   ) -> AbstractRequester:
    with open(settings_path) as settings_file:
        settings = json.load(settings_file)
    return RequesterFactory.create_requester(settings=settings, auth_type=auth_type, env=env)


if __name__ == '__main__':
    requester = create_requester_with_settings(
        settings_path=settings_path, auth_type=AuthType.JWT, env=Environment.PRD)
    ls2_client = LS2Client(requester=requester)

    print(ls2_client.wegsegment_by_id(id='674669'))




