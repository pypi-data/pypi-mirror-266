from fastapi import HTTPException, Depends, Header

from komodo.framework.komodo_app import KomodoApp
from komodo.framework.komodo_collection import KomodoCollection
from komodo.framework.komodo_user import KomodoUser
from komodo.models.framework.appliance_runtime import ApplianceRuntime

g_appliance: KomodoApp = KomodoApp.default()

# Initialize the app with your service account
import firebase_admin


def get_appliance() -> KomodoApp:
    if not g_appliance:
        raise HTTPException(status_code=404, detail="Appliance not found")
    return g_appliance


def set_appliance_for_fastapi(appliance: KomodoApp):
    global g_appliance
    g_appliance = appliance

    # Initialize the app with your service account if firebase key is provided
    key = appliance.config.get_firebase_key()
    if key and key.exists():
        print("Initializing Firebase for this appliance")
        from firebase_admin import credentials
        cred = credentials.Certificate(key)
        firebase_admin.initialize_app(cred)


def get_user(appliance=Depends(get_appliance), x_user_email: str = Header(None), authorization: str = Header(None)):
    firebase_key = appliance.config.get_firebase_key()
    if firebase_key and firebase_key.exists():
        return get_user_from_token(authorization)
    else:
        return get_user_from_email(x_user_email, appliance)


def get_email(user=Depends(get_user)):
    return user.email


def get_appliance_runtime(user=Depends(get_user), appliance=Depends(get_appliance)):
    runtime = ApplianceRuntime(appliance=appliance, user=user)
    return runtime


def get_selected_collection(shortcode, runtime=Depends(get_appliance_runtime)) -> KomodoCollection:
    if collection := runtime.get_collection(shortcode):
        return collection

    raise HTTPException(status_code=404, detail="Collection not found: " + shortcode)


def get_user_from_email(x_user_email, appliance):
    if x_user_email is None:
        raise HTTPException(status_code=400, detail="X-User-Email header missing")

    try:
        runtime = ApplianceRuntime(appliance)
        user = runtime.get_user(x_user_email)
        if not user:
            raise HTTPException(status_code=401, detail="User not found: " + x_user_email)
        return user

    except Exception as e:
        raise HTTPException(status_code=500, detail="Can not validate: " + x_user_email + " - " + str(e))


def get_user_from_token(token):
    from firebase_admin import auth

    # Extract the token from the Authorization header
    if token is None:
        raise HTTPException(status_code=400, detail="Authorization header missing")

    try:
        # Verify the ID token while checking if the token is revoked
        decoded_token = auth.verify_id_token(token, check_revoked=True)
        uid = decoded_token['uid']
        provider_id = decoded_token['firebase']['sign_in_provider']
        name = decoded_token.get('name', 'Anonymous')
        email = decoded_token.get('email', f"anon-{uid}@firebase.app")

        # Now you have access to the user's information
        print(f"UID: {uid}, Name: {name}, Email: {email}, Provider ID: {provider_id}")
        return KomodoUser(email=email, name=name, uid=uid, provider_id=provider_id)

    except auth.RevokedIdTokenError:
        # Raised if the ID token has been revoked. You might handle this by asking the user to reauthenticate.
        print("ID token has been revoked")
        raise HTTPException(status_code=401, detail="ID token has been revoked")
    except auth.InvalidIdTokenError:
        # Raised if the ID token is invalid or expired. You might redirect the user to login again.
        print("Invalid ID token")
        raise HTTPException(status_code=401, detail="Invalid ID token")
    except Exception as e:
        # Handle other exceptions
        print(f"Error verifying ID token: {e}")
        raise HTTPException(status_code=401, detail="Error verifying ID token")
