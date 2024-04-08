import asyncio
import base64
from typing import AsyncGenerator

from fastapi import HTTPException
from starlette.responses import StreamingResponse

from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.loaders.database.user_loader import UserLoader
from komodo.models.framework.agent_runner import AgentRunner
from komodo.models.framework.chat_message import ChatMessage
from komodo.shared.utils.digest import get_guid_full
from komodo.store.conversations_store import ConversationStore


class AskRequest:
    LOCAL_STORE = {}

    def __init__(self, appliance, agent_shortcode, email, prompt, *,
                 conversation_guid=None, collection_guid=None, file_guid=None):
        super().__init__()
        print("email: ", email, "agent_shortcode: ", agent_shortcode, "prompt: ", prompt)
        self.appliance = appliance
        self.agent_shortcode = agent_shortcode
        self.email = email
        self.prompt = prompt
        self.conversation_guid = conversation_guid
        self.collection_guid = collection_guid
        self.file_guid = file_guid

    def run(self):
        conversation = self.get_conversation()
        history = self.get_history(conversation.guid)

        store = ConversationStore()
        store.add_user_message(guid=conversation.guid, sender=self.email, text=self.prompt)

        try:
            runner = self.get_runner()
            reply = runner.run(self.prompt, history=history)
            store.add_agent_message(guid=conversation.guid, sender=self.agent_shortcode, text=reply.text)
            return {"reply": reply.text, "prompt": self.prompt}
        except Exception as e:
            print("Error while asking agent: ", e)
            raise HTTPException(status_code=500, detail=str(e))

    def stream(self):
        conversation = self.get_conversation()
        history = self.get_history(conversation.guid)

        store = ConversationStore()
        store.add_user_message(guid=conversation.guid, sender=self.email, text=self.prompt)

        def stream_callback():
            def display_tool_invocation(tool, arguments):
                yield "Gathering data..."

            try:
                runner = self.get_runner()
                runner.runtime.tools_invocation_callback = display_tool_invocation
                runner.runtime.tools_response_callback = store_tool_response
                return runner.run_streamed(self.prompt, history=history)

            except Exception as e:
                print("Error while asking agent: ", e)
                raise HTTPException(status_code=500, detail=str(e))

        def store_callback(reply):
            store.add_agent_message(conversation.guid, sender=self.agent_shortcode, text=reply)

        def store_tool_invocation(tool, arguments):
            store.add_agent_message(conversation.guid, sender=self.agent_shortcode,
                                    text=f"Tool: {tool.name}: Arguments: {arguments}")

        def store_tool_response(tool, arguments, output):
            store.add_agent_message(conversation.guid, sender=self.agent_shortcode,
                                    text=f"Previously Run: Tool: {tool.shortcode}: Arguments: {arguments} Output: {output}")

        return StreamingResponse(self.komodo_async_generator(stream_callback, store_callback),
                                 media_type='text/event-stream')

    async def komodo_async_generator(self, stream_callback, store_callback) -> AsyncGenerator[str, None]:
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

    def get_conversation(self):
        store = ConversationStore()
        conversation = store.get_or_create_conversation(self.conversation_guid, self.agent_shortcode,
                                                        self.email, self.prompt)
        return conversation

    def get_history(self, guid):
        store = ConversationStore()
        messages = store.get_messages(guid)
        return ChatMessage.convert_from_proto_messages(messages)

    def get_runner(self):
        loader = UserLoader(self.appliance)
        user = loader.get_user(self.email)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found: " + self.email)

        agent: KomodoAgent = self.appliance.get_agent(self.agent_shortcode)
        if agent is None:
            raise HTTPException(status_code=400, detail="Requested Agent is not available")

        runtime = KomodoRuntime(appliance=self.appliance, agent=agent, user=user)

        if self.collection_guid is not None:
            print("Collection Shortcode: ", self.collection_guid, "File Guids: ", self.file_guid)
            collection = runtime.get_collection(self.collection_guid)
            if collection:
                collection.selected_file_guids = self.file_guid.split(",") if self.file_guid is not None else []
                runtime.set_selected_collection(collection)
            else:
                raise HTTPException(status_code=400,
                                    detail="Requested collection is not available: " + self.collection_guid)

        return AgentRunner(runtime)


def add_request(ask: AskRequest) -> object:
    ask_guid = get_guid_full()
    AskRequest.LOCAL_STORE[ask_guid] = ask
    return ask_guid


def get_request(ask_guid) -> AskRequest:
    return AskRequest.LOCAL_STORE.get(ask_guid, None)


def pop_request(ask_guid) -> AskRequest:
    return AskRequest.LOCAL_STORE.pop(ask_guid, None)
