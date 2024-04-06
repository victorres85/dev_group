from fastapi import Depends, APIRouter, Form, Query, HTTPException 
from fastapi.responses import JSONResponse

from typing import List, Optional
from config.models import Stack, Software
from models.request.schemas import UserReq
from models.request.detailed_schemas import UserDetailed, PostDetailed
from models.handlers.user import UserHandler
from security.secure import get_current_user, is_superuser



users_router = APIRouter()


from fastapi import APIRouter, Form, HTTPException, Depends
from typing import Optional

users_router = APIRouter()


@users_router.get("/me",
    summary="Get my details",
    response_model=UserDetailed,
    responses={
        401: {"detail": "Not authorized user."},
        500: {"detail": "User not found"},
    },)
async def get_my_details(current_user: UserReq = Depends(get_current_user)): 
    """
    # Get My Details

    This endpoint allows an authenticated user to retrieve detailed information about 
    themselves, including their name, email, picture, bio, associated company, software 
    projects they have worked on, and technology stacks they know.

    # Returns:
        The user's detailed information in JSON format.

    # Errors:
        - 401: Not authorized user.
        - 500: Error retrieving user details.

    
    # Usage:
    You can retrieve the user's own information by making a GET request to the endpoint. Here's an example using JavaScript:

    ```
        const url = "/api/user/me";
        fetch(url, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('There was an error!', error));
    ```
    """
    try:
        result=current_user
        return result
    except Exception as e:
        return JSONResponse(content={'detail':'User not found'}, status_code=500)

@users_router.post("/add",
    summary="Add a new user",
    response_description="User create with success",
    responses={
        500: {"detail": "Add user problem encountered"},
    },
)
async def user_add(
    email: str = Form(..., description="The email of the new user."),
    name: str = Form(..., description="The name of the new user."),
    role: Optional[str] = Form(None, description="The user's role in the company."),
    joined: Optional[str] = Form(None, description="The date the user joined the company.")
): 
    """
    # Add User

    This endpoint adds a new user to the system. It takes the user's 
    email and name, and optionally their role and the date they joined the company.

# Flow:
1. The function first checks if the provided email is already registered in the system.
2. If the email is already registered, an HTTPException is raised with a status code of 400 and a detail message of "Email already registered".
3. If the email is not already registered, a new User object is created with the provided email, name, role, and joined date. The password is set to a hashed version of '1234', and the active status is set to True.
4. The new User object is saved to the database.
5. An asynchronous task is created to clear the 'users' cache and refresh it with the updated list of all users.
6. If all the above steps are completed successfully, the function returns True.
7. If any exception occurs during the above steps, the function catches the exception and returns False.

    # Parameters:
    - **email:** (str) The email of the new user.
    - **name:** (str) The name of the new user.
    - **role:** (Optional[str]) The user's role in the company.
    - **joined:** (Optional[str]) The date the user joined the company.

    # Returns:
        - 200: User create with success.

    # Errors:
        - 500: Add user problem encountered.
    """
    try:
        user_handler = UserHandler(email=email, name=name, role=role, joined=joined)
        result = await user_handler.insert_obj()
        if result:
            return JSONResponse(content={'detail':'User create with success'}, status_code=200)
        raise Exception  
        pass
    except Exception as e:
        return JSONResponse(content={'detail':'Add user problem encountered'}, status_code=500)

@users_router.patch("/update",
    summary="Update user details",
    response_model=UserDetailed,
    responses={
        200: {"detail": "Successful operation"},
        500: {"detail": "Update user problem encountered"},
    },
)
async def user_update(
    name: Optional[str] = Form(None, description="The name of the user to update."),
    bio: Optional[str] = Form(None, description="A brief bio or description of the user."),
    stacks: Optional[str] = Form(None, description=f"""Options: {str([stack.name for stack in Stack.nodes.all()]).replace("'", "")}"""),
    twitter: Optional[str] = Form(None, description="The user's Twitter handle."),
    linkedin: Optional[str] = Form(None, description="The user's LinkedIn profile."),
    github: Optional[str] = Form(None, description="The user's GitHub profile."),
    joined: Optional[str] = Form(None, description="The date the user joined the company."),
    role: Optional[str] = Form(None, description="The user's role in the company."),
    softwares: Optional[str] = Form(None, description=f"""Options: {str([software.name for software in Software.nodes.all()]).replace("'", "")}"""),
    company: Optional[str] = Form(None, description=f"""send uid"""),
    picture: Optional[str] = Form(None, description=f"""send uid"""), #File(None), 
    current_user: UserReq = Depends(get_current_user)): 
    """
    # Update User Details

    This endpoint updates the details of a user in the system.

    # Flow:
    1. The user's bearer token is used to identify the existing user in the system.
    2. The user's attributes are updated based on the provided information.
    3. The user's relationships (company, stacks, softwares) are handled and updated if necessary.
    4. An asynchronous task is created to clear the 'users' cache and refresh it with the updated list of all users.
    5. If the user is not found or there's a problem with related nodes (e.g., company or software), an error is returned.
    6. Upon successful update, the updated user details are returned.

    # Parameters:
    - **name:** (str) The name of the user to update.
    - **bio:** (Optional[str]) A brief bio or description of the user.
    - **stacks:** (Optional[str]) A string containing the tech stacks associated with the user, separated by commas.
    - **softwares:** (Optional[str]) A string containing the software names associated with the user, separated by commas.
    - **company:** (Optional[str]) A string containing the company name associated with the user.
    - **picture:** (UploadFile) An uploaded file containing the user's picture.
    - **twitter:** (Optional[str]) The user's Twitter handle.
    - **linkedin:** (Optional[str]) The user's LinkedIn profile.
    - **github:** (Optional[str]) The user's GitHub profile.
    - **joined:** (Optional[str]) The date the user joined the company.
    - **role:** (Optional[str]) The user's role in the company.


    # Returns:
        - 200: The user's detailed information in JSON format.

    # Errors:
        - 500: Update user problem encountered.
        - 401: Not authorized user.
        - 404: User not found.
        - 404: Company not found.
        - 404: Software not found.
        - 409: Only one company can be associated with a user.

    # Note on Relationships:
    Relationships (company, stacks, softwares) are updated by deleting all existing 
    relationships and recreating them using the provided data. If a user has existing 
    relationships and wants to add new ones, all the relationships must be passed together. 
    
    For example, if a user has worked on 2 softwares and wants to add a new relationship 
    with another software, all 3 softwares must be passed. If only the new software is passed, 
    the relationships with the other 2 softwares will be broken, and only the new 
    relationship will remain.

    # Usage:
    You can use JavaScript to make a PATCH request to this endpoint, providing the required parameters.

    ```javascript
    const url = "/api/user/update";

    const formData = new FormData();
    formData.append("name", "USER NAME");
    formData.append("bio", "USER BIO");
    formData.append("stacks", "STACKS SEPARETED BY COMA");
    formData.append("softwares", "SOFTWARES SEPARETED BY COMA");
    formData.append("company", "COMPANY NAME USER WORKS FOR");
    formData.append("picture", "PICTURE URL");
    formData.append("twitter", "TWITTER HANDLE");
    formData.append("linkedin", "LINKEDIN PROFILE");
    formData.append("github", "GITHUB PROFILE");
    formData.append("joined", "DATE USER JOINED THE COMPANY");


    fetch(url, {
        method: 'PATCH',
        headers: {
            'accept': 'application/json',
            'Authorization': 'Bearer TOKEN',
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('There was an error!', error));
    ```

    Replace `"USER NAME"`, `"USER BIO"`, `"STACKS SEPARETED BY COMA"`, \
    `"SOFTWARES SEPARETED BY COMA"`, `"COMPANY USER WORKS FOR"`, `"PICTURE URL"`, \
    `"TWITTER HANDLE"`, `"LINKEDIN PROFILE"`, `"GITHUB PROFILE"`, and \
    `"DATE USER JOINED THE COMPANY"` with the appropriate values for the user you \
    are updating. 
    """
    try:
        softwares = softwares.split(",") if softwares else []
        stacks = stacks.split(",") if stacks else []
        try:
            user_handler = UserHandler(uid=current_user.uid, name=name, bio=bio, role=role.lower(), joined_at=joined, twitter=twitter, linkedin=linkedin,  github=github, stacks=stacks, softwares=softwares, company_uid=company, picture=picture)
            user_data = await user_handler.update_obj()
            if user_data:
                return JSONResponse(content={'detail':'Login successful.' , 'data':user_data}, status_code=200)
            raise Exception  
        except HTTPException as e:
            return JSONResponse(content={'detail':f'{e.detail}'}, status_code=404)
        except Exception as e:
            return JSONResponse(content={'detail':'Update user problem encountered'}, status_code=500)
    except Exception as e:
        return JSONResponse(content={f'detail':'error {e}'}, status_code=500)


@users_router.get("/list",
    summary="List all users",
    response_model=List[UserDetailed],
    responses={
        401: {"detail": "Not authorized user."},
        500: {"detail": "List users problem encountered"},
    },)
async def list_all_user(current_user: UserReq = Depends(get_current_user)): 
    """
    # List All Users

    Retrieve a list of all users registered in the system.


    # Flow:
    1. The user's bearer token is used to authenticate the user and give access to this endpoint.
    2. The function `get_all` is called to retrieve all users from the system.
    3. The users are sorted based on their strength attribute.
    4. The details of each user are retrieved using the `get_details` function.
    5. If a user's details cannot be retrieved, that user is skipped.
    6. If there's an exception during the process, an error is returned.
    7. Upon successful retrieval, a list of user details is returned.


    # Returns:
        - A list of user details in the response body.

    # Errors:
        - 401: Not authorized user. 
        - 500: List users problem encountered. 

    # Usage:
    You can retrieve the user's own information by making a GET request to the endpoint. Here's an example using JavaScript:

    ```
        const url = "/api/user/list";

        fetch(url, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
                'Authorization': 'Bearer TOKEN',
            },
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('There was an error!', error));
    ```
    """
    try:
        user_handler = UserHandler()
        result = await user_handler.get_all()
        if result:
            return result
        return JSONResponse(content={'detail':'List users problem encountered'}, status_code=500)
    except HTTPException as e:
        return JSONResponse(content={'detail':'Not authorized user.'}, status_code=401)
    except Exception as e:
        return JSONResponse(content={'detail':'List users problem encountered'}, status_code=500)

@users_router.get("/search",
    summary="Users lookup",
    responses={
        200: {"model": UserDetailed},
        401: {"detail": "Not authorized user."},
        500: {"detail": "Search user problem encountered"},
    },)
async def search(users: str = Query([], description="Value to search in name, email, and bio fields"),
            companies: str = Query([], description="Value to search in name, description fields"),
            softwares: str = Query([], description="Value to search in name, description fields"),
            stacks: str = Query([], description="Value to search in name, description fields"),
            current_user: UserReq = Depends(get_current_user)): 
    """
    # Users Lookup

    This endpoint allows users to search for other users based on various criteria such as their names,
    email addresses, and bio information, or based on companies, software projects, or technology stacks
    they are associated with.

    # Flow:
    1. The user's bearer token is used to authenticate the user and give access to this endpoint.
    2. The user can provide search criteria in the query parameters: `users`, `companies`, `softwares`, and `stacks`.
    3. The `users` parameter is used to search for values in the name, email, and bio fields of users.
    4. The `companies` parameter is used to search for values in the name and description fields of companies.
    5. The `softwares` parameter is used to search for values in the name and description fields of software projects.
    6. The `stacks` parameter is used to search for values in the name and description fields of technology stacks.
    7. If no search criteria are provided, the endpoint will return a list of user details.
    8. Multiple values can be provided separated by commas for each parameter.
    9. The endpoint then calls the `search` function with the provided search criteria and the `current_user`.
    11. The result is returned as a JSON response containing a list of detailed user information that matches the search criteria.
    
    # Parameters:
    - **users **: A comma-separated list of values to search in the name, email, and bio fields of users.
    - **companies **: A comma-separated list of values to search in the name and description fields of companies.
    - **softwares **: A comma-separated list of values to search in the name and description fields of software projects.
    - **stacks **: A comma-separated list of values to search in the name and description fields of technology stacks.

    # Returns:
        - 200: Returns a list of detailed user information that matches the search criteria.
        
    # Errors:    
        - 401: Returns an error if the user is not authorized or not authenticated.
        - 500: Returns an error if there is a problem encountered during the user search.

    # Note:
        - The search is case-insensitive. 
        - The search is performed using the `contains` operator, so the search criteria can be a substring of the actual value.
        - The search criteria can be a single value or multiple values separated by commas.
        - If multiple values are provided, the search will return results that match any of the values.
        - If no search criteria are provided, the endpoint will return a list of all users.

    # Observation:
    - Different weights are applied to search results based on their associations with the search criteria:
        - A weight of 1.0 is applied for direct user matches in the `users` parameter.
        - A weight of 0.8 is applied for matches in companies, software projects, or technology stacks.
    - The current implementation returns a random list of user details if no search criteria are provided. This provides varied results.
    - In the future, more complex sorting criteria can be added to return users based on their similarities with the user making the request or other relevant criteria.

    # Usage:
    - To search for users with names or emails matching "John" or "Jane", use: `/search?users=john,jane`
    - To search for users associated with companies named "company01", use: `/search?companies=company01`
    - To search for users associated with software projects named "Project A" or "Project B", use: `/search?softwares=project a,project b`
    - To search for users associated with technology stacks named "Python" or "JavaScript", use: `/search?stacks=python,javascript`
    - To search for users associated with companies named "company01" and software projects named "Project A" or "Project B", use: `/search?companies=company01&softwares=project a,project b`
    You can search for a company by making a POST request to the endpoint and passing the required parameters. Here's an example using JavaScript:

    ```javascript
        const url = "api/users/search?users=KEY_WORDS_FOR_USERS_SEPARETED_BY_COMA&companies=KEY_WORDS_FOR_COMPANIES_SEPARETED_BY_COMA&softwares=KEY_WORDS_FOR_SOFTWARES_SEPARETED_BY_COMA&stacks=KEY_WORDS_FOR_STACKS_SEPARETED_BY_COMA";

        fetch(url, {
            method: 'POST',
            headers: {
                'accept': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('There was an error!', error));
    ```
    Replace `KEY_WORDS_FOR_USERS_SEPARETED_BY_COMA`, `KEY_WORDS_FOR_COMPANIES_SEPARETED_BY_COMA`, `KEY_WORDS_FOR_SOFTWARES_SEPARETED_BY_COMA`, and `KEY_WORDS_FOR_STACKS_SEPARETED_BY_COMA` with the appropriate values.
    """

    try:
        users = users.lower().split(",") if users else []
        companies = companies.lower().split(",") if companies else []
        softwares = softwares.lower().split(",") if softwares else []
        stacks = stacks.lower().split(",") if stacks else []
        user_handler = UserHandler()
        result = await user_handler.search(users=users, companies=companies, softwares=softwares, stacks=stacks, current_user=current_user)
        if result:
            return result
        return JSONResponse(content={'detail':'No user was found.'}, status_code=400)
    except HTTPException as e:
        return JSONResponse(content={'detail':'Not authorized user.'}, status_code=401)
    except Exception as e:
        return JSONResponse(content={'detail':'Search user problem encountered'}, status_code=500)


@users_router.delete("/delete/{uid}",
    responses={
        200: {"detail": "Successful operation"},
        500: {"detail": "delete user problem encountered"},
    },)
async def delete_obj(uid: str, current_user: UserReq = Depends(is_superuser)): 
    """
    # Delete a User

    This endpoint deletes a user from the system by their email. It will first find the user
    by the provided email, disconnect all relationships associated with the user, and then
    delete the user node. This operation can only be performed by a superuser.

    # Flow:
    1. The current user must be a superuser to access this endpoint.
    2. The system finds the user by the provided email.
    3. All relationships of the user (knows, works for, worked on) will be disconnected.
    4. The user node will be deleted.
    5. A message 'Successful operation' will be returned if the deletion was successful.
    
    # Parameters:
    - **email** (str): The email of the user to be deleted.

    # Returns:
        {'message':'Successful operation'}

    # Errors:
        - 401: Not enough privileges (if the current user is not a superuser).
        - 404: User not found.
        - 500: delete user problem encountered.

    """
    try:
        user_handler = UserHandler(uid=uid)
        result = await user_handler.delete_obj()
        if result:
            return {'message':'Successful operation'}
        else: 
            return JSONResponse(content={'message':'delete user problem encountered'}, status_code=500) 
    except HTTPException as e:
        return JSONResponse(content={'detail':'Not enough privileges'}, status_code=401)

@users_router.get("/{uid}",
    response_model=UserDetailed,
    responses={
        401: {"detail": "Not authorized user."},
        404: {"detail": "User not found."},
        500: {"detail": "Search user problem encountered"},
    },)
async def get_user(uid: str, current_user: UserReq = Depends(get_current_user)): 
    """
    # Get User by Uid

    Retrieve detailed information about a user by their email address.
   
    # Flow:
    1. The user's bearer token is used to authenticate the user and give access to this endpoint.
    2. The function `get_by_uid` is called to retrieve user from the system.
    3. The details of the user are retrieved using the `get_details` function.
    4. If there's an exception during the process, an error is returned.
    5. Upon successful retrieval, the user's details is returned.

    # Parameters:
    - **uid** (str): The uid of the user to retrieve details for.
   
    # Return:
        - If the user is found, detailed information about the user is returned.

    # Errors:
        - 401: Not authorized user.
        - 404: User not found.
        - 500: Search user problem encountered. 
    """
    try:
        user_handler = UserHandler(uid=uid)
        result = await user_handler.get_by_uid()
        if result:
            return result
        return JSONResponse(content={'detail':'User not found.'}, status_code=404)
    except HTTPException as e:
        return JSONResponse(content={'detail':'User not found.'}, status_code=404)
    except Exception as e:
        return JSONResponse(content={'detail':'Search user problem encountered'}, status_code=500)


@users_router.get("/tagged_posts/",
    responses={
        200: {"model": List[PostDetailed]},
        401: {"detail": "Not authorized user."},
        404: {"detail": "No posts have been found."},
        500: {"detail": "Search user problem encountered"},
    },)
async def get_tagged_posts(current_user: UserReq = Depends(get_current_user)): 
    """
    # Get User Tagged Posts

    Retrieve a list of posts that the user has been tagged in.

    # Flow:
    1. The user's bearer token is used to authenticate the user and give access to this endpoint.
    2. The function `get_user_tagged_posts` is called to retrieve all posts that the user has been tagged in.
    3. If there are no posts found, an error is returned.
    4. Upon successful retrieval, a list of detailed post information is returned.

    # Returns:
        - A list of post details in the response body.

    """
    try:
        user_handler = UserHandler(uid=current_user.uid)
        result = await user_handler.get_user_tagged_posts()
        if result:
            return result
        return JSONResponse(content={'detail':'No posts have been found.'}, status_code=404)
    except HTTPException as e:
        return JSONResponse(content={'detail':'Search user problem encountered'}, status_code=404)