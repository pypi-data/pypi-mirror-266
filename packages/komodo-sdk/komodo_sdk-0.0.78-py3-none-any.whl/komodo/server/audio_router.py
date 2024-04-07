import asyncio
import os
import time
from io import BytesIO

from fastapi import Depends, APIRouter
from starlette.responses import FileResponse, StreamingResponse

from komodo.server.globals import get_appliance
from komodo.shared.utils.digest import get_guid_short

router = APIRouter(
    prefix='/api/v1/audio',
    tags=['Text to Speech']
)


@router.get('/hello', summary='Text to Speech', description='Convert text to speech.')
async def simple(appliance=Depends(get_appliance)):
    from openai import OpenAI
    client = OpenAI()
    start_time = time.time()

    from openai import OpenAI

    client = OpenAI()

    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input="Hello world! This is a streaming test.",
    )

    folder = "/tmp/komodo-audio"
    guid = get_guid_short()
    path = os.path.join(folder, f"{guid}.mp3")
    os.makedirs(folder, exist_ok=True)
    response.stream_to_file(path)
    return FileResponse(path, media_type="audio/mpeg")


@router.get('/wonderful', summary='Text to Speech', description='Convert text to speech.')
async def wonderful(appliance=Depends(get_appliance)):
    from openai import OpenAI
    client = OpenAI()
    start_time = time.time()

    async def generate():
        with client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice="nova",
                response_format="opus",  # similar to WAV, but without a header chunk at the start.
                input="""I see trees of green
                        Red roses too
                        I see them bloom
                        For me and you
                        And I think to myself
                        What a wonderful world
                        I see skies of blue
                        And clouds of white
                        The bright blessed day
                        The dark sacred night
                        And I think to myself
                        What a wonderful world
                    """,
        ) as response:
            print(f"Time to first byte: {int((time.time() - start_time) * 1000)}ms")
            for chunk in response.iter_bytes(chunk_size=1024):
                yield chunk
                await asyncio.sleep(0)

    print(f"Done in {int((time.time() - start_time) * 1000)}ms.")
    return StreamingResponse(generate(), media_type="audio/ogg")


@router.get('/testing-opus', summary='Text to Speech', description='Convert text to speech.')
async def test_1(appliance=Depends(get_appliance)):
    from openai import OpenAI
    client = OpenAI()
    start_time = time.time()

    async def generate():
        with client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice="nova",
                response_format="opus",  # similar to WAV, but without a header chunk at the start.
                input="""I see skies of blue and clouds of white 
                    The bright blessed days, the dark sacred nights 
                    And I think to myself 
                    What a wonderful world""",
        ) as response:
            print(f"Time to first byte: {int((time.time() - start_time) * 1000)}ms")
            for chunk in response.iter_bytes(chunk_size=1024):
                yield chunk
                await asyncio.sleep(0)

    print(f"Done in {int((time.time() - start_time) * 1000)}ms.")

    return StreamingResponse(generate(), media_type="audio/ogg")


@router.get("/testing-buffer")
async def test_buffer():
    # Example response object from your audio source
    from openai import OpenAI

    client = OpenAI()
    start_time = time.time()

    with client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input="""I see skies of blue and clouds of white 
                The bright blessed days, the dark sacred nights 
                And I think to myself 
                What a wonderful world""",
    ) as response:
        print(f"Time to first byte: {int((time.time() - start_time) * 1000)}ms")

        # Create a BytesIO object to hold the audio data
        audio_buffer = BytesIO()

        # Assuming response.iter_content() gives you chunks of audio data
        for chunk in response.iter_content(chunk_size=4096):
            audio_buffer.write(chunk)

        # Important: Seek back to the start of the BytesIO object before reading from it
        audio_buffer.seek(0)

        # Create and return a StreamingResponse that streams the audio data
        return StreamingResponse(audio_buffer, media_type="audio/mpeg")
