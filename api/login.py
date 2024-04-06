
from fastapi import APIRouter, Depends, Request, HTTPException, Body
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm

from starlette.requests import Request
from fastapi.responses import JSONResponse

from authlib.integrations.starlette_client import OAuthError
from datetime import timedelta
from config.models import User

from security.secure import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, get_password_hash, verify_password
from security.secure import valid_email_from_db, create_access_token, get_current_user, is_superuser
from config.oauth_connect import oauth

from models.request.schemas import UserReq, UserCreate, UserPasswordChange
from models.request.detailed_schemas import UserDetailed
from models.handlers.user import UserHandler
from services import send_email_verification, generate_password
from typing import Annotated
from fastapi import BackgroundTasks
from datetime import  timedelta

bearer = HTTPBearer()
login_router = APIRouter()


@login_router.get('/google_login', tags=['Authentication'],
    summary="Create a New User", 
    responses={
        200: {"detail": "Login successful."},
        500: {"detail": "Login failed."},
    },) 
async def google_login(request: Request):

    """
    # OAuth Google Login

    This endpoint initiates the OAuth Google login process. It redirects the user to the Google
    authentication page, where the user can grant access to their Google account information.
    After successful authentication, the user will be redirected back to the '/token' endpoint
    to handle the retrieved information.

    # Flow:
    1. User must be redirected to this endpoint to start the login process.
    2. The user will be then redirected to the Google authentication page to log in and grant access.
    3. After authentication, Google will redirect the user back to the '/token' endpoint.
    4. The '/token' endpoint will handle the information received from Google OAuth, including
       user's name, email, and picture.
    5. It will check if the user's email is already registered in the system.
    6. If the email is not registered, the user's email, name, and picture will be registered,
       and a JWT token will be assigned to the user's session.
    7. A message 'Login successful' will be returned.
    8. Subsequent interactions will require the JWT token for authentication.

    # Returns:
        {'detail':'Login successful.'}

    # Errors:
        - 500: Login failed.

    """
    try:
        redirect_uri = request.url_for('token')
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception as e:
        return JSONResponse(content={'detail':'Login failed.'}, status_code=500)

@login_router.get('/token', include_in_schema=False,
    responses={
        200: {"detail": "Login successful."},
        500: {"detail": "Login failed."},
    },)
async def token(request: Request):
    try:
        access_token = await oauth.google.authorize_access_token(request)
        email = access_token.get('userinfo', {}).get('email', None)
        name = access_token.get('userinfo', {}).get('name', None)
        picture = access_token.get('userinfo', {}).get('picture', None)
        if not valid_email_from_db(email):
            existing_user = UserHandler(email=email, name=name, picture=picture).insert_obj_from_oauth()
    
        if valid_email_from_db(email):
            access_token_expires = timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
            new_access_token = create_access_token({'sub': email}, expires_delta=access_token_expires)
            request.session['jwt_token'] = new_access_token
            return JSONResponse(content={'detail':'Login successful.'}, status_code=200)
    except OAuthError as e:
        return JSONResponse(content={'detail':'Login failed.'}, status_code=500)


@login_router.post("/login", tags=['Authentication'],
    summary="System User Login", 
    response_model=UserDetailed,
    responses={
        401: {"detail": "Incorrect email or password."},
        500: {"detail": "Login failed."},
    },)
async def login_for_access_token(request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ):
    """
    User Login

    This endpoint allows users to log in by providing their email and password. The login
    credentials will be verified, and if they are correct, an Access Token will be issued
    to the user.

    # Flow:
    1. The front-end should make a POST request to '/login' with the 'email' and 'password'
       fields in the request body.
    2. The server will verify the provided credentials and proceed with the login process.
    3. If the email and password match a registered user, an Access Token will be generated.
    4. The Access Token will be stored in the user's session for subsequent interactions.
    5. A message 'Login successful' will be returned.

    # Parameters:        
        {
            "grant_type": "",
            "username": "user's email", # required
            "password": "user's password", # required
            "scope": "",
            "client_id": "",
            "client_secret": ""
        }

    # Returns:
        {'detail': 'Login successful',
        "access_token": "JWT token.", 
        "data": User Data.}

    # Errors:
        - 401: Incorrect email or password.
        - 500: Login failed.
        
    # Note:
    This endpoint uses OAuth2PasswordRequestForm, which by default contains fields for 'username'
    and 'password'. However, in this implementation, the 'username' field has been replaced by
    'email' to better match the semantics of the application. The 'email' field will be treated
    as the user's login username.
    """
    try:
        email = form_data.username.lower()
        password = form_data.password
            
        user = authenticate_user(email, password)
        if not user:
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        access_token_expires = timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        request.session['jwt_token'] = access_token
        user_data = await UserHandler().get_details(uid=user.uid)
        data = user_data
        return JSONResponse(content={'detail':'Login successful.' , 'access_token': access_token, 'data':data}, status_code=200)
    except HTTPException as e:
        return JSONResponse(content={'detail':'Incorrect email or password.'}, status_code=401)
    except Exception as e:
        return JSONResponse(content={'detail':'Login failed.'}, status_code=500)


@login_router.post("/change_password", tags=['Authentication'],
    responses={
        200: {"detail": "Password changed successfully."},
        401: {"detail": "Incorrect password."},
        500: {"detail": "Password change failed."},
    },)
def change_password(data: UserPasswordChange,
        user: UserReq = Depends(get_current_user)
):
    """
    # Change Password

    This endpoint allows an authenticated user to change their password. It accepts the user's current password and the new password, and performs the change if the current password is verified.

    # Flow:
    1. The user must be authenticated to access this endpoint.
    2. The user provides their current password and the new password they wish to set.
    3. The system verifies the current password. If incorrect, a 401 error is returned.
    4. If the current password is correct, the system will update the password with the new hash.
    5. A message 'Password changed successfully.' will be returned if the process is successful.
    6. If the password change fails due to any issue, a 500 error with the message 'Password change failed.' is returned.

    # Parameters:
        data: UserPasswordChange - Contains the current password and the new password to be set.
        user: UserDetailed - The currently authenticated user retrieved from the session.

    # Returns:
        {'detail': 'Password changed successfully.'}

    # Errors:
        - 500: Password change failed.
    """
    current_user = User.nodes.get_or_none(email=user.email)
    email = current_user.email
    new_password_hash = get_password_hash(data.new_password)
    current_password_hash = current_user.password
    if not verify_password(data.password, current_password_hash):
        return JSONResponse(content={'detail':'Password incorrect.'}, status_code=500) 

    try:
        pass_change =  current_user.password = new_password_hash
        current_user.save()
        password1 = User.nodes.get_or_none(email=user.email).password

        if verify_password(data.new_password, password1):
            return JSONResponse(content={'detail':'Password changed successfully.'}, status_code=200)
        else:
            raise HTTPException(status_code=500, detail="Password change failed")

    except Exception as e:
        return JSONResponse(content={'detail':'Password change failed.'}, status_code=500)  


@login_router.post("/create_new_user", tags=['Authentication'],
    summary="Create a New User", 
    status_code=201,
    response_description="User successfully created.",
    responses={
        201: {"detail": "User successfully created."},
        400: {"detail": "Email already registered or not allowed."},
        401: {"detail": "Not authorized to create user."},
        500: {"detail": "User creation failed."},
        },)
async def create_new_user(background_tasks: BackgroundTasks, user: UserCreate, current_user: UserReq = Depends(is_superuser)):
    """
    # Create a New User

    This endpoint allows the creation of a new user in the system. The email provided must belong to one of the
    allowed domains, which include 'company01.com', 'feedmanager.co.uk', 'klickkonzept.de', 'smartkeyword.io', 
    'kiliagon.com' and 'arcane.run'. An exception will be raised if the email is already registered in the system, 
    or if the email's domain is not in the allowed list.

    ## Flow:
    1. The current user must be a superuser to access this endpoint
    2. Check if the email is already registered in the system.
    3. Validate the email's domain to see if it is in the allowed domains.
    4. If the email is not registered and its domain is allowed, a password will be generated.
    5. Hash the password and insert the new user's email and hashed password into the system.
    6. Send an email verification to the new user.
    7. Return a message 'User successfully created.'

    # Returns:
        {'detail':'User successfully created.'}

    # Errors:
        - 400: Email already registered or not allowed.
        - 401: Not authorized to create user (if the user is not a superuser).
        - 500: User creation failed.
    """
    try:
        domains = ['company01.com', 'feedmanager.co.uk', 'klickkonzept.de', 'smartkeyword.io', 'kiliagon.com', 'arcane.run','gmail.com']
        email_domain = user.email.split('@')[1]
        if email_domain not in domains:
            return JSONResponse(content={'detail':'Email already registered or not allowed.'}, status_code=400)
        password = generate_password()
        hashed_password = get_password_hash(password)
        await UserHandler(email=user.email, password=hashed_password).insert_obj()

        # Add the task to send the email to the background tasks
        background_tasks.add_task(send_email_verification, user.email, password)
        return {"detail": "User successfully created."}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e


@login_router.post('/logout', tags=['Authentication'],
    responses={
        302: {"detail": "Logout successful."},
        400: {"detail": "Logout failed."},})  # Tag it as "authentication" for our docs
def logout(request: Request, user: UserReq = Depends(get_current_user)):
    """
    # Logout Endpoint

    This endpoint handles the logout process for authenticated users. Once a user is logged in and has a valid JWT token,
    they can be logged out by being redirected to this endpoint.

    # Flow:
    1. The user must be redirected to this endpoint to start the logout process.
    2. The endpoint will attempt to remove the JWT token from the user's session.
    3. A message 'Logout successful' will be returned if the process is successful.
    4. Subsequent interactions will require the user to log in again, as the JWT token will no longer be valid.

    # Returns:
        {'detail':'Logout successful.'}

    # Errors:
        - 400: Logout failed. The failure could be due to the JWT token not being found in the user's session or other unexpected issues.

    """
    try:
        request.session.pop(request.session['jwt_token'], None)
        return  JSONResponse(content={'detail': 'Logout successful.'}, status_code=302)
    except Exception as e:
        return JSONResponse(content={'detail': 'Logout failed.'}, status_code=500)
