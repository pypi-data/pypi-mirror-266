from fastapi import APIRouter, Depends

from komodo.server.globals import get_email
from komodo.store.conversations_store import ConversationStore

router = APIRouter(
    prefix='/api/v1/conversations',
    tags=['Conversations']
)


@router.get('/{guid}')
async def get_conversation(guid: str, email=Depends(get_email)):
    conversation_store = ConversationStore()
    conversation_data = conversation_store.get_conversation_as_dict(guid)
    filtered_messages = []
    for message in conversation_data[0]['messages']:
        if "Previously Run: Tool" not in message['text']:
            filtered_messages.append(message)
    conversation_data[0]['messages'] = filtered_messages

    return conversation_data


@router.delete('/{guid}')
async def delete_conversation(guid: str, email=Depends(get_email)):
    conversation_store = ConversationStore()
    response = conversation_store.delete_conversation(guid, email)
    return response
