from fastapi import HTTPException, Header, Depends

from komodo.framework.komodo_app import KomodoApp
from komodo.framework.komodo_collection import KomodoCollection
from komodo.models.framework.appliance_runtime import ApplianceRuntime

g_appliance: KomodoApp = KomodoApp.default()


def get_appliance() -> KomodoApp:
    if not g_appliance:
        raise HTTPException(status_code=404, detail="Appliance not found")
    return g_appliance


def set_appliance_for_fastapi(appliance: KomodoApp):
    global g_appliance
    g_appliance = appliance


def get_email_from_header(x_user_email: str = Header(None), appliance=Depends(get_appliance)):
    if x_user_email is None:
        raise HTTPException(status_code=400, detail="X-User-Email header missing")

    try:
        runtime = ApplianceRuntime(appliance)
        user = runtime.get_user(x_user_email)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Can not validate: " + x_user_email + " - " + str(e))

    if not user:
        raise HTTPException(status_code=401, detail="User not found: " + x_user_email)

    return x_user_email


def get_appliance_runtime(email=Depends(get_email_from_header), appliance=Depends(get_appliance)):
    runtime = ApplianceRuntime(appliance=appliance)
    runtime.set_user(runtime.get_user(email))
    return runtime


def get_collection(shortcode, email=Depends(get_email_from_header),
                   appliance=Depends(get_appliance)) -> KomodoCollection:
    runtime = ApplianceRuntime(appliance=appliance)
    runtime.set_user(runtime.get_user(email))
    if collection := runtime.get_collection(shortcode):
        return collection

    raise HTTPException(status_code=404, detail="Collection not found")
