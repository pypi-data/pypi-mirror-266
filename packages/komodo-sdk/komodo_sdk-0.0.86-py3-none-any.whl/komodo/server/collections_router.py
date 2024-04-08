from pathlib import Path
from typing import List

import aiofiles
from fastapi import APIRouter, HTTPException, Depends, Request, Body
from fastapi import File, UploadFile
from starlette.responses import FileResponse
from werkzeug.utils import secure_filename

from komodo.framework.komodo_collection import KomodoCollection
from komodo.server.globals import get_appliance, get_appliance_runtime, get_selected_collection
from komodo.shared.documents.text_extract_helper import TextExtractHelper

router = APIRouter(
    prefix='/api/v1/collections',
    tags=['Collections']
)


@router.post('')
async def create_collection(name=Body(), description=Body(), runtime=Depends(get_appliance_runtime)):
    try:
        path = runtime.config.locations().user_collections(runtime.user.email) / secure_filename(name)
        collection = KomodoCollection(path=path, name=name, description=description)
        return collection.get_collection_metadata()
    except:
        raise HTTPException(status_code=500, detail="Failed to create collection")


@router.get('')
async def list_collection(runtime=Depends(get_appliance_runtime)):
    collections = runtime.get_available_collections()
    response = [c.get_collection_metadata() for c in collections]
    return response


@router.get('/{shortcode}')
async def get_collection(collection=Depends(get_selected_collection)):
    return collection.get_collection_with_files()


@router.delete('/{shortcode}')
async def delete_collection(collection=Depends(get_selected_collection)):
    if collection.belongs_to_user():
        return collection.delete_collection()

    raise HTTPException(status_code=403, detail="You are not authorized to delete this collection")


@router.post("/upload_files/{shortcode}")
async def upload(files: List[UploadFile] = File(...), collection=Depends(get_selected_collection)):
    try:
        folder = collection.path
        for file in files:
            filepath = folder / Path(file.filename).name
            contents = await file.read()
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(contents)

        collection_dict = collection.get_collection_metadata()

    except Exception as e:
        return {"message": "There was an error uploading the file: " + str(e)}

    return {"message": f"Successfully uploaded {[file.filename for file in files]}", "collection": collection_dict}


@router.post('/upload_stream/{shortcode}')
async def upload_stream(request: Request, collection=Depends(get_selected_collection)):
    # For full discussion on this approach, see:
    # https://stackoverflow.com/questions/65342833/fastapi-uploadfile-is-slow-compared-to-flask/70667530#70667530
    try:
        folder = collection.path
        filename = request.headers['filename']
        filepath = folder / Path(filename).name

        async with aiofiles.open(filepath, 'wb') as f:
            async for chunk in request.stream():
                await f.write(chunk)

        collection_dict = collection.get_collection_metadata()

    except Exception as e:
        return {"message": "There was an error uploading the file: " + str(e)}

    return {"message": f"Successfully uploaded {filename}", "collection": collection_dict}


@router.get('/{shortcode}/{file_guid}')
def download_file(file_guid: str, collection=Depends(get_selected_collection)):
    file = collection.get_file_by_guid(file_guid)
    if not Path(file).exists():
        raise HTTPException(status_code=404, detail="File not found.")

    return FileResponse(file, media_type='application/octet-stream', filename=file.name)


def adjust_filename_to_txt(filename):
    import os
    base = os.path.splitext(filename)[0]  # Removes current extension if present
    return f"{base}.txt"


@router.get('/{shortcode}/{file_guid}/{format}')
def download_file_format(file_guid: str, format: str, collection=Depends(get_selected_collection),
                         appliance=Depends(get_appliance)):
    file = collection.get_file_by_guid(file_guid)
    if not Path(file).exists():
        raise HTTPException(status_code=404, detail="File not found in collection. Please re-upload the file.")

    if format == 'text':
        cache = appliance.config.locations().cache()
        helper = TextExtractHelper(file, cache)
        helper.extract_text()

        extracted = helper.extracted_path()
        if extracted.exists():
            return FileResponse(extracted, media_type='text/plain', filename=adjust_filename_to_txt(file.name))
        else:
            raise HTTPException(status_code=404, detail="Text data not available for this file")

    raise HTTPException(status_code=404, detail="Format not supported: " + format)


@router.delete('/{shortcode}/{file_guid}')
async def delete_file(file_guid: str, collection=Depends(get_selected_collection)):
    file = collection.get_file_by_guid(file_guid)
    if collection.belongs_to_user():
        return collection.delete_file(file.name)
    raise HTTPException(status_code=403, detail="You are not authorized to delete this file")
