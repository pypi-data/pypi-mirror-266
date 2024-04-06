from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import FileResponse, Response
from komodo.store.logo_store import LogoStore
from io import BytesIO

router = APIRouter(
    prefix='/api/v1/logo',
    tags=['Logo']
)

logo_store = LogoStore()

@router.post('/upload', status_code=201)
async def upload_logo(logo: UploadFile = File(...)):
    # Validate file extension
    filename = logo.filename
    extension = filename.rsplit('.', 1)[-1].lower()
    if extension not in ["jpg", "jpeg", "png"]:
        raise HTTPException(status_code=400, detail="Only JPG or JPEG or PNG files are allowed")

    logo_bytes = await logo.read()
    logo_store.upload_logo(logo_bytes, extension)
    return {"message": "Logo uploaded successfully"}

@router.get('/download', responses={200: {"content": {"image/jpeg": {}, "image/png": {}}}}, description="Download the logo")
def get_logo():
    logo_bytes, logo_extension = logo_store.retrieve_logo() 
    if not logo_bytes:
        raise HTTPException(status_code=404, detail="Logo not found")
    
    # Determine the media type based on the file extension
    if logo_extension == 'jpeg' or logo_extension == 'jpg':
        media_type = "image/jpeg"
    elif logo_extension == 'png':
        media_type = "image/png"
    else:
        # Default or unsupported media type handling, adjust as needed
        raise HTTPException(status_code=415, detail="Unsupported media type")
    
    # Return the logo bytes with the appropriate media type
    return Response(content=logo_bytes, media_type=media_type)
