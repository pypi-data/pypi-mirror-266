from fastapi import Depends, APIRouter

from komodo.server.globals import get_appliance
from komodo.shared.utils.digest import get_guid_short

router = APIRouter(
    prefix='/api/v1/reports',
    tags=['Reports and Analysis']
)


@router.get('', summary='Get list of reports', description='List of guids and descriptions.')
async def list(appliance=Depends(get_appliance)):
    # generate 10 random reports for now
    reports = [{'guid': get_guid_short(), 'name': f'Report {i}', 'description': f'Report {i}'} for i in range(10)]
    return reports


@router.get('/{guid}', summary='Get report details', description='Get details of a report.')
async def get(guid: str, appliance=Depends(get_appliance)):
    return {'guid': guid, 'name': f'Report {guid}', 'description': f'Report {guid}'}
