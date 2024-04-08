import datetime

from fastapi import Depends, APIRouter

from komodo.core.agents.chatdoc_agent import ChatdocAgent
from komodo.framework.komodo_features import KomodoFeatures
from komodo.server.globals import get_appliance, get_email

router = APIRouter(
    prefix='/api/v1/appliance',
    tags=['Appliance']
)


@router.get('/description', response_model=dict, summary='Get appliance description',
            description='Get the description of the appliance.')
def get_appliance_description(appliance=Depends(get_appliance)):
    agents = appliance.get_all_agents()
    return {
        "shortcode": appliance.shortcode,
        "name": appliance.name,
        "company": appliance.company,
        "type": appliance.type.name,
        "features": ", ".join([f.name for f in appliance.features]),
        "version": get_version(),
        "purpose": appliance.purpose,
        "agents": [a.summary() for a in agents]
    }


@router.get('/configuration', response_model=dict, summary='Get appliance configuration',
            description='Get the configuration of the appliance.')
def get_appliance_configuration(email=Depends(get_email), appliance=Depends(get_appliance)):
    agents = appliance.get_all_agents()
    return {
        "shortcode": appliance.shortcode,
        "name": appliance.name,
        "company": appliance.company,
        "type": appliance.type.name,
        "version": get_version(),
        "purpose": appliance.purpose,
        "user": email,
        "configunation": [
            {
                "feature": KomodoFeatures.chat.name,
                "description": "Chat with the agents",
                "agents": [a.summary() for a in agents]
            },
            {
                "feature": KomodoFeatures.chatdoc.name,
                "description": "Chat with documents",
                "agents": [ChatdocAgent().summary()]
            },
            {
                "feature": KomodoFeatures.chat.name,
                "description": "Chat with top 1 agents",
                "agents": [a.summary() for a in agents[:1]]
            },
            {
                "feature": KomodoFeatures.chat.name,
                "description": "Chat with top 2 agents",
                "agents": [a.summary() for a in agents[:2]]
            }, {
                "feature": KomodoFeatures.chatdoc.name,
                "description": "More chat with documents",
                "agents": [ChatdocAgent().summary()]
            }, {
                "feature": KomodoFeatures.reportbuilder.name,
                "description": "Report builder - no agents available",
                "agents": []
            }
        ]
    }


def get_version():
    import importlib.metadata
    try:
        return importlib.metadata.version('komodo-sdk')
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0." + str(datetime.datetime.now().strftime('%Y%m%d'))


@router.get('/index', summary='Index all data sources',
            description='Index all data sources for the appliance.')
def index_all_data_sources(appliance=Depends(get_appliance)):
    appliance.index(reindex=False)
    return {"status": "success"}


@router.get('/reindex', summary='Re-index all data sources.',
            description='Deletes all existing data and re-indexes all data sources for the appliance.')
def re_index_all_data_sources(appliance=Depends(get_appliance)):
    appliance.index(reindex=True)
    return {"status": "success"}


@router.get('/available-agents', summary='Get available agents',
            description='Get available agents for the appliance for a given feature.')
def get_available_agents(email=Depends(get_email), appliance=Depends(get_appliance)):
    agents = appliance.get_all_agents()
    return {"status": "success"}
