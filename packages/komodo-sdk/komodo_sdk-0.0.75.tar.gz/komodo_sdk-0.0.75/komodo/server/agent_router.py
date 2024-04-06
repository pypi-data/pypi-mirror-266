import asyncio
import base64
from typing import AsyncGenerator

from fastapi import Depends, APIRouter, HTTPException, Body
from starlette.responses import StreamingResponse

from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.loaders.database.collection_loader import CollectionLoader
from komodo.models.framework.agent_runner import AgentRunner
from komodo.models.framework.appliance_runtime import ApplianceRuntime
from komodo.models.framework.chat_message import ChatMessage
from komodo.server.globals import get_appliance, get_email_from_header
from komodo.store.conversations_store import ConversationStore

router = APIRouter(
    prefix='/api/v1/agent',
    tags=['Agent']
)


@router.get('/conversations/{agent_shortcode}')
async def get_conversations(agent_shortcode, email=Depends(get_email_from_header)):
    conversation_store = ConversationStore()
    conversations = conversation_store.get_conversation_headers(email, agent_shortcode)
    return conversations


@router.post('/ask/{agent_shortcode}')
async def ask_agent(agent_shortcode, message=Body(), guid=Body(), collection_shortcode=Body(), file_guid=Body(),
                    email=Depends(get_email_from_header), appliance=Depends(get_appliance)):
    print("email: ", email, "agent_shortcode: ", agent_shortcode, "prompt: ", message)
    conversation = get_conversation(guid, agent_shortcode, email, message, collection_shortcode)
    history = get_history(conversation.guid)

    store = ConversationStore()
    store.add_user_message(guid=conversation.guid, sender=email, text=message)

    try:
        runner = get_runner(appliance, agent_shortcode, email, collection_shortcode, file_guid)
        reply = runner.run(message, history=history)
        store.add_agent_message(guid=conversation.guid, sender=agent_shortcode, text=reply.text)
        return {"reply": reply.text, "message": message}
    except Exception as e:
        print("Error while asking agent: ", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ask-streamed")
async def ask_agent_streamed(email: str, agent_shortcode: str, prompt: str, guid: str = None,
                             collection_shortcode=None, file_guid=None, appliance=Depends(get_appliance)):
    print("email: ", email, "agent_shortcode: ", agent_shortcode, "prompt: ", prompt)

    conversation = get_conversation(guid, agent_shortcode, email, prompt, collection_shortcode)
    history = get_history(conversation.guid)

    store = ConversationStore()
    store.add_user_message(guid=conversation.guid, sender=email, text=prompt)

    def stream_callback():
        def display_tool_invocation(tool, arguments):
            yield "Gathering data..."

        try:
            runner = get_runner(appliance, agent_shortcode, email, collection_shortcode, file_guid)
            runner.runtime.tools_invocation_callback = display_tool_invocation
            runner.runtime.tools_response_callback = store_tool_response

            return runner.run_streamed(prompt, history=history)
        except Exception as e:
            print("Error while asking agent: ", e)
            raise HTTPException(status_code=500, detail=str(e))

    def store_callback(reply):
        store.add_agent_message(conversation.guid, sender=agent_shortcode, text=reply)

    def store_tool_invocation(tool, arguments):
        store.add_agent_message(conversation.guid, sender=agent_shortcode,
                                text=f"Tool: {tool.name}: Arguments: {arguments}")

    def store_tool_response(tool, arguments, output):
        store.add_agent_message(conversation.guid, sender=agent_shortcode,
                                text=f"Previously Run: Tool: {tool.shortcode}: Arguments: {arguments} Output: {output}")

    return StreamingResponse(komodo_async_generator(stream_callback, store_callback),
                             media_type='text/event-stream')


def get_conversation(guid: str, agent_shortcode: str, email: str, prompt: str, collection_shortcode: str = None):
    store = ConversationStore()
    guid = collection_shortcode if guid is None else guid
    conversation = store.get_or_create_conversation(guid, agent_shortcode, email, prompt)
    return conversation


def get_history(guid):
    store = ConversationStore()
    messages = store.get_messages(guid)
    return ChatMessage.convert_from_proto_messages(messages)


def get_runner(appliance, agent_shortcode, email, collection_shortcode=None, file_guid=None):
    # Get Agent Info based on short code
    runtime = ApplianceRuntime(appliance)
    agent: KomodoAgent = runtime.get_agent(agent_shortcode)
    if agent is None:
        raise HTTPException(status_code=400, detail="Respective Agent is not available")

    collection = None

    if collection_shortcode is not None:
        file_guids = file_guid.split(",") if file_guid is not None else []
        collection = CollectionLoader.load(collection_shortcode, file_guids=file_guids)
        collection.cache = appliance.config.cache()
        collection.user = runtime.get_user(email)

    user = runtime.get_user(email)
    runtime = KomodoRuntime(appliance=appliance, agent=agent, user=user, collection=collection)

    return AgentRunner(runtime)


async def komodo_async_generator(stream_callback, store_callback) -> AsyncGenerator[str, None]:
    reply = ""
    exception_occurred = False  # Flag to indicate an exception occurred during yield
    exception_message = ""  # To store the exception message
    for part in stream_callback():
        reply += part
        if exception_occurred:
            break  # Stop processing if an exception has occurred

        try:
            encoded = base64.b64encode(part.encode('utf-8')).decode('utf-8')
            yield f"data: {encoded}\n\n"
            await asyncio.sleep(0)

        except Exception as e:
            exception_occurred = True
            exception_message = str(e)

    store_callback(reply)

    if exception_occurred:
        print("Error while streaming: " + exception_message)
    else:
        print("stream complete")
        yield "event: stream-complete\ndata: {}\n\n"
