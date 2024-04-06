from fastapi import Depends, APIRouter, Form, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
from config.models import Stack
from models.handlers.stack import StackHandler
from models.request.schemas import StackReq, UserReq
from models.request.detailed_schemas import StackDetailed

from security.secure import get_current_user, is_superuser

stacks_router = APIRouter()


@stacks_router.post(
    "/add",
    responses={
        200: {"model": StackReq},
        400: {"detail": "Stack already exists"},
        409: {"detail": "Only one parent stack can be added"},
        401: {"detail": "Not authorized user."},
        500: {"detail": "Create stack problem encountered"},
    },
)
async def add_stack(
    name: str = Form(..., description="Stack name"), 
    description: Optional[str] = Form(None, description="Optional Stack Description"), 
    stack_type: Optional[str] = Form(None, description="Options: [database or frontend or backend or devops]"),
    part_of: Optional[str] = Form(None, description=f"""Options: {str([stack.name for stack in Stack.nodes.all()]).replace("'", "")}"""),
    image: Optional[str] = Form(None, description="Optional Stack's image url"), 
    current_user: UserReq = Depends(get_current_user)):
    """
    # Stack Registration

    This endpoint is used to register a new stack in the system. It requires the stack's name,
    and can optionally include a description of the stack. The stack's name will be validated and stored in
    lowercase format for consistency.

    # Flow:
    1. The user's bearer token is used to identify the existing user in the system.
    2. If the stack's name already exists in the system, an exception is raised.
    3. If the stack's name is unique, a new stack is created with the given name, image, description, stack type, and associated stack.
    4. If the stack creation process fails, an appropriate error message is returned.
    6. An asynchronous task is created to clear the 'comapanies' cache and refresh it with the updated list of all companies.
    7. The newly created stack is returned to the user.

    # Parameters:
    - name: The name of the stack.
    - description: An optional description of the stack.
    - part_of: An optional parent stack name.
    - image: Optional Stack's image url.

    # Returns:
        - The details of the newly added stack.

    # Errors:
        - 400: The stack already exists, the image file size exceeds the maximum limit, or the image file is not a valid image.
        - 401: Not authorized User.
        - 409: Only one parent stack can be added.
        - 500: An error was encountered while attempting to create the stack.


    # Usage:
    You can create a new stack by making a POST request to the endpoint and passing the required parameters. Here's an example using JavaScript:

    ```
        const url = "api/stack/add";

        const formData = new FormData();
        formData.append("name":..., "description":..., "part_of":..., "image":...);

        fetch(url, {
            method: 'POST',
            headers: {
                'accept': 'application/json',
                'Authorization': `Bearer ${jwt_token}`,
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('There was an error!', error));
    ```

    """
    if Stack.nodes.get_or_none(name=name.lower()):
        return JSONResponse(status_code=400, content={'detail':"Stack already exists."})
    if part_of:
        if len(part_of.split(",")) > 1:
            return JSONResponse(content={'detail':'List softwares problem encountered'}, status_code=400)
        else:
            part_of = part_of.lower()
    if stack_type:
        if stack_type not in ['database', 'frontend', 'backend', 'devops']:
            raise HTTPException(status_code=409, detail="Stack type must be one of ['database', 'frontend', 'backend', 'devops']")
        else:
            stack_type = stack_type.lower()
    try:
        stack_handler = StackHandler(name=name, description=description, stack_type=stack_type, part_of=part_of, image=image)
        result = await stack_handler.insert_obj()
        if result:
            return result
        else: 
            raise HTTPException(status_code=500, detail="Create stack problem encountered.")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Create stack problem encountered.")


@stacks_router.delete("/delete/{uid}",
    responses={
        200: {"detail": "Stack has been deleted"},
        401: {"detail": "Not authorized user."},
        404: {"detail": "Stack hasn't been found"},
        500: {"detail": "delete stack problem encountered"},
    },)
def stack_delete(uid: str, current_user: UserReq = Depends(is_superuser)): 
    """
    Delete a Stack

    This endpoint deletes a stack from the system based on the provided stack name. 

    # Flow:
    1. The user's bearer token is used to identify the existing user in the system.
    2. The stack uid is passed as a URL path parameter to this endpoint.
    3. The 'delete_obj' function is invoked, which deletes the stack node and all its relationships from the database.
    4. If the operation fails, an appropriate error message is returned.
    5. An asynchronous task is created to clear the 'companies' cache and refresh it with the updated list of all companies.
    3. If the operation is successful, a message 'stack has been deleted' is returned.

    # Parameters:
    - **name:** (str) The name of the stack to delete.

    # Returns:
        {'detail':'Stack has been deleted'}

    # Errors:
        - 401: Not authorized user.
        - 404: Stack hasn't been found.
        - 500: Delete stack problem encountered.

    # Note: 
        Only a superuser is allowed to delete stacks. If a non-superuser tries to delete a stack, a 403 error will be returned.    
    # Usage:

    You can delete a stack by making a DELETE request to the endpoint with the stack name you want to delete. Here's an example using JavaScript:

    ```javascript
        const url = "/api/stack/delete/STACK_UID_TO_DELETE";

        fetch(url, {
            method: 'DELETE',
            headers: {
                'accept': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('There was an error!', error));
    ```
    Replace `STACK_UID_TO_DELETE`, with the appropriate stack uid.
    """
    try:
        stack_handler = StackHandler(uid=uid)
        result = stack_handler.delete_obj()
        if result:
            return {'message':'stack has been deleted'}
        else: 
            raise HTTPException(status_code=404, detail="Stack hasn't been found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="delete stack problem encountered")

@stacks_router.patch("/update",
    responses={
        200: {"model": StackDetailed},
        401: {"detail": "Not authorized user."},
        404: {"detail": "Stack hasn't been found"},
        500: {"detail": "Update stack problem encountered"},
    },)
async def stack_update(
    uid: str = Form(None, description="The stack's uid"),
    name: Optional[str] = Form(None, description="The name of the stack"),
    description: Optional[str] = Form(None, description="Optional description of the stack"),
    stack_type: Optional[str] = Form(None, description="Options: ['database', 'frontend', 'backend', 'devops']]"),
    part_of: Optional[str] = Form(None, description=f"""Options: """),
    image: Optional[str] = Form(None, description=f"Stack Image Url"), 
    current_user: UserReq = Depends(get_current_user)): 
    """
    # Update Stack Information

    This endpoint allows authorized users to update a stack's information, including its name, description, image, and associated stack.


    # Flow:
    1. The user's bearer token is used to identify the existing user in the system..
    2. The user can provide the stack's name, along with the information to be updated.
    3. If part_of are provided, the relationships between the stack and the related stack will be updated. Invalid or non-existing stacks names will result in an error.
    4. If the update process fails, an appropriate error message is returned.
    5. An asynchronous task is created to clear the 'stacks' cache and refresh it with the updated list of all stacks.
    6. The updated details of the stack will be returned as a response.
    7. If any errors occur, appropriate error messages will be returned.

    # Parameters:
    - **uid:** str The stack uid has to be provided.
    - **name:** (Optional[str]) The name of the stack.
    - **description:** (Optional[str]) Optional description of the stack.
    - **stack_type:** (Optional[str]) A string containing the stacks type ['database', 'frontend', 'backend', 'devops'].
    - **part_of:** (Optional[str]) A string containing the this stack parent stack's name.
    - **image:** (Optional[str]) Image URL.
    - **current_user:** The authenticated user making the request.

    # Returns:
        - 200: `StackDetailed` model object if the update is successful.

    # Errors:
        - 401: Not authorized user.
        - 404: Stack hasn't been found.
        - 409: Only one parent stack can be added.
        - 409: Stack type must be one of ['database', 'frontend', 'backend', 'devops']
        - 500: Update stack problem encountered or other unexpected errors.

    # Usage:
    You can use JavaScript to make a PATCH request to this endpoint, providing the required parameters.

    ```
    const url = "/api/stack/update";

    const formData = new FormData();
    formData.append("uid":.., "name":.., "description":.., "stack_type":.., "part_of":.., "image":..);

    fetch(url, {
        method: 'PATCH',
        headers: {
            'authorization': `Bearer jwt_token`,
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('There was an error!', error));
    ```
    """
    if part_of: 
        if len(part_of.split(",")) > 1:
            raise HTTPException(status_code=409, detail="Only one parent stack can be added")
        else:
            part_of = part_of.lower()
    if stack_type:
        stack_type = stack_type.lower()
        if stack_type not in ['database', 'frontend', 'backend', 'devops']:
            raise HTTPException(status_code=409, detail="Stack type must be one of ['database', 'frontend', 'backend', 'devops']")
    try:
        stack_handler = StackHandler(uid=uid, name=name, description=description, stack_type=stack_type, image=image, part_of=part_of)
        result = await stack_handler.update_obj()
        if result:
            return result
        else: 
            raise HTTPException(status_code=500, detail="Update stack problem encountered")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Update stack problem encountered")


@stacks_router.get("/list",
    responses={
        200: {"model": List[StackDetailed]},
        401: {"detail": "Not authorized user."},
        500: {"detail": "List softwares problem encountered"},
    })
async def list_all_stack(current_user: UserReq = Depends(get_current_user)): 
    """
    # List All Stacks

    Retrieve a list of all stacks registered in the system.

    # Flow:
    1. The user's bearer token is used to authenticate the user and give access to this endpoint.
    2. The function `get_all` is called to retrieve all stacks from the system.
    3. The stacks are sorted based on their strength attribute.
    4. The details of each stack are retrieved using the `get_details` function.
    5. If a stack's details cannot be retrieved, that stack is skipped.
    6. If there's an exception during the process, an error is returned.
    7. Upon successful retrieval, a list of stack details is returned.

    # Returns:
        - A list of user details in the response body.

    # Errors:
        - 401: Not authorized user. 
        - 500: List stacks problem encountered. 

    # Usage:
    You can retrieve the list of stacks by making a GET request to the endpoint. Here's an example using JavaScript:

    ```javascript
        const url = "/api/stack/list";

        fetch(url, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
                'Authorization': `Bearer ${jwt_token}`,
            },
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('There was an error!', error));
    """
    try:
        stack_handler = StackHandler()
        result = await stack_handler.get_all()
        
        if result:
            return result 
        else:
            return JSONResponse(content={'detail':'List softwares problem encountered'}, status_code=500)
    except Exception as e:
        return JSONResponse(content={'detail':'List softwares problem encountered'}, status_code=500)


@stacks_router.get("/search",
    responses={
        200: {"model": List[StackDetailed]},
        401: {"detail": "Not authorized user."},
        404: {"detail": "No stack have been found"},
        500: {"detail": "Stack hasn't been found"},
    },)
async def search(users: str = Query(None, description="Value to search in name, email, and bio fields"),
                companies: str = Query(None, description="Value to search in name, description fields"),
                softwares: str = Query(None, description="Value to search in name, description fields"),
                stacks: str = Query(None, description="Value to search in name, description fields"),
                current_user: UserReq = Depends(get_current_user)):
    """
    # Stack Lookup

    This endpoint allows users to search for stacks based on various criteria such as their names,
    and descriptions, or based on their employees, software projects, or technology stacks
    they are associated with. stack

    # Flow:
    1. User must be authenticated to access this endpoint.
    2. The user can provide search criteria in the query parameters: `users`, `stacks`, `softwares`, and `stacks`.
    3. The `users` parameter is used to search for values in the name, email, and bio fields of users.
    4. The `stacks` parameter is used to search for values in the name and description fields of companies.
    5. The `softwares` parameter is used to search for values in the name and description fields of software projects.
    6. The `stacks` parameter is used to search for values in the name and description fields of technology stacks.
    7. If no search criteria are provided, the endpoint will return a list of user details.
    8. Multiple values can be provided separated by commas for each parameter.
    9. The endpoint then calls the `search` function with the provided search criteria and the `current_user`.
    10. The result is returned as a JSON response containing a list of detailed user information that matches the search criteria.
    
    # Parameters:
    - **users: **  A comma-separated list of values to search in the name, email, and bio fields of users.
    - **companies: **  A comma-separated list of values to search in the name and description fields of companies.
    - **softwares: **  A comma-separated list of values to search in the name and description fields of software projects.
    - **stacks: **  A comma-separated list of values to search in the name and description fields of technology stacks.

    # Returns:
        - 200: Returns a list of detailed stacks information that matches the search criteria.
        
    # Errors:    
        - 401: No authorized user.
        - 404: No stack have been found.
        - 500: Search stack problem encountered.

    # Note:
        - The search is case-insensitive. 
        - The search is performed using the `contains` operator, so the search criteria can be a substring of the actual value.
        - The search criteria can be a single value or multiple values separated by commas.
        - If multiple values are provided, the search will return results that match any of the values.
        - If no search criteria are provided, the endpoint will return a list of all stacks.

    # Observation:
    - Different weights are applied to search results based on their associations with the search criteria:
        - A weight of 1.0 is applied for direct user matches in the `stacks` parameter.
        - A weight of 0.8 is applied for matches in stacks, software projects, or technology stacks.
    - The current implementation returns a random list of user details if no search criteria are provided. This provides varied results.
    - In the future, more complex sorting criteria can be added to return stacks based on their similarities with the user making the request or other relevant criteria.

    # Usage:
    - To search for stacks with names or emails matching "company01", use:`/search?stacks=company01`
    - To search for stacks associated with employees named "John" or "Jane", use:  `/search?employees=john,jane`
    - To search for stacks associated with software projects named "Project A" or "Project B", use: `/search?softwares=project a,project b`
    - To search for stacks associated with technology stacks named "Python" or "JavaScript", use: `/search?stacks=python,javascript`
    - To search for stacks associated with companies named "company01" and software projects named "Project A" or "Project B", use: `/search?companies=company01&softwares=project a,project b`

    You can search for a stack by making a POST request to the endpoint and passing the required parameters. Here's an example using JavaScript:

    ```javascript
        const url = "api/stack/search?users=USERS&companies=COMPANIES&softwares=SOFTWARES&stacks=STACKS";

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
    Replace `USERS`, `COMPANIES`, `SOFTWARES`, and `STACKS` with the appropriate values.
    """
    try:
        users = users.split(",") if users else []
        companies = companies.split(",") if companies else []
        softwares = softwares.split(",") if softwares else []
        stacks = stacks.split(",") if stacks else []

        stack_handler = StackHandler()
        result = await stack_handler.search(stacks=stacks, softwares=softwares, users=users, companies=companies)
        if result:
            return result
        raise HTTPException(status_code=404, detail="No stack have been found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Search stack problem encountered")


@stacks_router.get("/{uid}",
    responses={
        200: {"model": StackDetailed},
        500: {"detail": "Stack hasn't been found"},
    },)
async def get_stack(uid: str, current_user: UserReq = Depends(get_current_user)): 
    """
    # Get Stack by Uid

    Retrieve detailed information about a stack by their uid.

    # Flow:
    1. The user's bearer token is used to authenticate the user and give access to this endpoint.
    2. The function `get_by_uid` is called to retrieve stack from the system.
    3. The details of the stack are retrieved using the `get_details` function.
    4. If there's an exception during the process, an error is returned.
    5. Upon successful retrieval, the stack's details is returned.

    # Parameters:
    - **uid** (str): The uid of the stack to retrieve details for.
   
    # Return:
        - If the stack is found, detailed information about the stack is returned.

    # Errors:
        - 401: Not authorized user.
        - 404: Stack not found.
        - 500: Search stack problem encountered.

    # Usage:

    You can retrieve the details of a stack by making a GET request to the endpoint with the stack's name. Here's an example using JavaScript:

    ```
        const url = `http://127.0.0.1:8000/api/stack/STACK_UID`;

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
        stack_handler = StackHandler(uid)
        result = await stack_handler.get_by_uid()
        if result:
            return result
        return JSONResponse(content={"message":"Stack hasn't been found"}, status_code=500) 
    except Exception as e:
        return JSONResponse(content={"message":"Stack hasn't been found"}, status_code=500)
