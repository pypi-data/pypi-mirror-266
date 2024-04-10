from fastapi import APIRouter, Depends

from komodo.server.globals import get_appliance_runtime

router = APIRouter(
    prefix='/api/v1/user',
    tags=['User']
)


@router.get("/profile", response_model=dict, summary="Get user profile.", description="Get user profile.")
async def get_user_profile(runtime=Depends(get_appliance_runtime)):
    return runtime.user.to_dict() if runtime and runtime.user else {"error": "User not found."}
