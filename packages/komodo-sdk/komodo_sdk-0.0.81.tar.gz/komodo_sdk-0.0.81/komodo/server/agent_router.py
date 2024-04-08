from fastapi import Depends, APIRouter

from komodo.server.ask_request import get_request, add_request
from komodo.server.globals import get_email, get_ask_request_from_params, get_ask_request_from_body
from komodo.store.conversations_store import ConversationStore

router = APIRouter(
    prefix='/api/v1/agent',
    tags=['Agent']
)


@router.get('/conversations/{agent_shortcode}')
async def get_conversations(agent_shortcode, email=Depends(get_email)):
    conversation_store = ConversationStore()
    conversations = conversation_store.get_conversation_headers(email, agent_shortcode)
    return conversations


@router.post('/ask')
async def ask_agent(ask=Depends(get_ask_request_from_body)):
    ask_guid = add_request(ask)
    print("Ask Guid: ", ask_guid)
    return ask.run()


@router.get("/ask-streamed")
async def ask_agent_streamed(ask=Depends(get_ask_request_from_params)):
    return ask.stream()


@router.post('/ask/request')
async def ask_request(ask=Depends(get_ask_request_from_body)):
    ask_guid = add_request(ask)
    return {"ask_guid": ask_guid}


@router.get('/ask/response/{ask_guid}')
async def ask_response(ask_guid):
    ask = get_request(ask_guid)
    return ask.run()


@router.get('/ask/stream/{ask_guid}')
async def ask_stream(ask_guid):
    ask = get_request(ask_guid)
    return ask.stream()
