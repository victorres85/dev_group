from fastapi import Depends, APIRouter, Form, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from models.handlers.software import SoftwareHandler
from models.request.schemas import SoftwareReq, UserReq
from models.request.detailed_schemas import SoftwareDetailed
from config.logger import logger 

from security.secure import get_current_user, is_superuser

softwares_router = APIRouter()


@softwares_router.post("/add",
    responses={
        200: {"model": SoftwareDetailed},
        400: {"detail": "Software already exists"},
        401: {"detail": "Not authorized user."},
        500: {"detail": "Create software problem encountered"},
    },
)
async def add_software(
                name: str = Form(..., description="Software's name"),
                client: str = Form(None, description="Software's client"),
                type: str = Form(None, description="Software's type"),
                contributor_uid: str = Form(None, description="Software's contributor uid"),
                problem: str = Form(None, description="Software's problem"),
                solution: str = Form(None, description="Software's solution"),
                comments: str = Form(None, description="Software's comments"),
                link: str = Form(None, description="Software's link"),
                stacks: List[str] = Form(None, description="Software's stacks uids"),
                image: str = Form(None, description="Software's image url"),
                company: str = Form(None, description="Uid of the company which has created the software"),
                current_user: UserReq = Depends(get_current_user)):
    """    
    # Software Registration

    This endpoint is used to register a new software in the system. It requires the software's name and an image file,
    and can optionally include a description of the software. The software's name will be validated and stored in
    lowercase format for consistency.

    # Flow:
    1. The user's bearer token is used to authenticate the user and give access to this endpoint.
    2. The user must provide the software's name.
    3. If the software's name already exists in the system, an exception is raised.
    4. If the software's name is unique, a new software is created with the given information.
    5. If the software creation process fails, an appropriate error message is returned.
    6. If the software creation process is successful, the software's will be associated with a given company and any given stack.
    7. An asynchronous task is created to clear the 'softwares' cache and refresh it with the updated list of all softwares.
    8. The newly created software is returned to the user.

        
    # Parameters:
    - name: The name of the software.
    - image: The image of the software, an image file.
    - description: An optional description of the software.
    - company: the company name that have developed the software.

    # Returns:
        - The details of the newly added software.

    # Errors:
        - 400: Software  already exists, the image file size exceeds the maximum limit, or the image file is not a valid image.
        - 401: Not authorized User.
        - 409: Only one parent software can be added.
        - 500: An error was encountered while attempting to create the software.

    # Usage:
    You can create a new software by making a POST request to the endpoint and passing the required parameters. Here's an example using JavaScript:

    ```
        const url = "api/software/add";

        const formData = new FormData();
        formData.append("name", "Software Name");
        formData.append("client", "Software Client");
        formData.append("type", "Software Type");
        formData.append("problem", "Software Problem");
        formData.append("solution", "Software Solution");
        formData.append("comments", "Software Comments");
        formData.append("link", "Software Link");
        formData.append("image", "path/to/your/image.png");
        formData.append("company", "Company Uid");
        formData.append("stacks", "Stringfied list of stacks uids");

        fetch(url, {
            method: 'POST',
            headers: {
                'authorization': `Bearer token`,
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('There was an error!', error));
    ```
    Replace <SOFTWARE_NAME>, <SOFTWARE_DESCRIPTION>, <COMPANY_NAME_> (name of the company which has created the Software)with the appropriate values for the software you are creating.
    """
    try:
        software_handler = SoftwareHandler(name=name, client=client, project_type=type, problem=problem, solution=solution, comments=comments, image=image, link=link, stacks=stacks[0].split(','), companyUid=company, contributorUid=contributor_uid)
        result = await software_handler.insert_obj()
        if result:
            return result
        else:
            raise HTTPException(status_code=500, detail="Create software problem encountered")
    except HTTPException as e:
        return JSONResponse(content={'detail': e.detail}, status_code=e.status_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Create software problem encountered")

@softwares_router.delete("/delete/{uid}",
    responses={
        200: {"detail": "Software has been deleted"},
        401: {"detail": "Not authorized user."},
        404: {"detail": "Software hasn't been found"},
        500: {"detail": "Delete software problem encountered"},
    },)
async def software_delete(uid: str, current_user: UserReq = Depends(is_superuser)): 
    """
    Delete a Software

    This endpoint deletes a software from the system based on the provided software name. 

    # Flow:
    1. The user's bearer token is used to identify the existing user in the system.
    2. The software uid is passed as a URL path parameter to this endpoint.
    3. The 'delete_obj' function is invoked, which deletes the software node and all its relationships from the database.
    4. If the operation fails, an appropriate error message is returned.
    5. An asynchronous task is created to clear the 'softewares' cache and refresh it with the updated list of all softewares.
    3. If the operation is successful, a message 'Software has been deleted' is returned.

    # Parameters:
    - **uid:** (str) The uid of the software to delete.

    # Returns:
        {'detail':'Software has been deleted'}

    # Errors:
        - 401: Not authorized user.
        - 404: Software hasn't been found.
        - 500: Delete software problem encountered.

    # Note: 
        Only a superuser is allowed to delete softwares. If a non-superuser tries to delete a stack, a 403 error will be returned.    
    # Usage:

    You can delete a software by making a DELETE request to the endpoint with the software uid you want to delete. Here's an example using JavaScript:

    ```
        const url = "/api/software/delete/`SOFTWARE_UID`";

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
    Replace `SOFTWARE_UID`, with the appropriate software uid.
    """
    try:
        software_handler = SoftwareHandler(uid=uid)
        result = await software_handler.delete_obj()
        if result:
            return {'detail':'Software has been deleted'}
        else: 
            return JSONResponse(content={'detail':'Delete software problem encountered'}, status_code=500) 
    except HTTPException as e:
        return JSONResponse(content={'detail':f'{e.detail}'}, status_code=404)

@softwares_router.patch("/update",
    responses={
        200: {"model": SoftwareDetailed},
        401: {"detail": "Not authorized user."},
        404: {"detail": "Software hasn't been found"},
        500: {"detail": "Update software problem encountered"},
    },)
async def software_update(
            uid: str = Form(..., description="Software uid"),
            name: str = Form(None, description="The name of the software"),
            client: str = Form(None, description="The client of the software"),
            project_type: str = Form(None, description="The project type of the software"),
            problem: str = Form(None, description="The problem of the software"),
            solution: str = Form(None, description="The solution of the software"),
            comments: str = Form(None, description="The comments of the software"),
            link: str = Form(None, description="The link of the software"),
            image:  str = Form(None, description="The software's image url"),
            company: str = Form(None, description="The Uid of the company which has created the software"),
            stacks: str = Form(None, description="List of all stacks used to create the software"),
            current_user: UserReq = Depends(get_current_user)): 
    """
    # Update Software Information

    This endpoint allows authorized users to update a software's information, including its name, description, image, and associated company.

    # Flow:
    1. The user's bearer token is used to identify the existing user in the system..
    2. The user can provide the software details to be updated.
    3. If stacks are provided, the relationships between the software and the stacks will be updated. Invalid or non-existing software names will result in an error.
    4. If comapany are provided, the relationships between the software and the company will be updated. Invalid or non-existing user names will result in an error.
    6. If the update process fails, an appropriate error message is returned.
    7. An asynchronous task is created to clear the 'softwares' cache and refresh it with the updated list of all softwares.
    8. The updated details of the software will be returned as a response.
    6. If any errors occur, appropriate error messages will be returned.

    
    # Parameters:
    - **name:** (Optional[str]) The name of the software.
    - **description:** (Optional[str]) Optional description of the software.
    - **company:** (Optional[str]) A string containing the company name associated with the software.
    - **image:** (UploadFile) Optional uploaded file representing the software's image.
    - **current_user:** The authenticated user making the request.

    # Returns:
        - 200: `SoftwareDetailed` model object if the update is successful.

    # Errors:
        - 401: Not authorized user.
        - 404: Software hasn't been found.
        - 500: Update software problem encountered or other unexpected errors.

    # Usage:
    You can use JavaScript to make a PATCH request to this endpoint, providing the required parameters.

    ```
    const url = "/api/software/update";

    const formData = new FormData();
    formData.append("name", "Software Name");
    formData.append("client", "Software Client");
    formData.append("type", "Software Type");
    formData.append("problem", "Software Problem");
    formData.append("solution", "Software Solution");
    formData.append("comments", "Software Comments");
    formData.append("link", "Software Link");
    formData.append("image", "path/to/your/image.png");
    formData.append("company", "Company Uid");
    formData.append("stacks", "Stringfied list of stacks uids");

    fetch(url, {
        method: 'PATCH',
        headers: {
            'authorization': `Bearer token`,
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('There was an error!', error));
    ```    
    """
    try:

        stacks = stacks.split(',') if stacks else []
        software_handler = SoftwareHandler(uid=uid, name=name, client=client, project_type=project_type, problem=problem, solution=solution, comments=comments, link=link, image=image, stacks=stacks, companyUid=company)
        result = await software_handler.update_obj()
        if result:
            return result
        else: 
            return JSONResponse(content={'detail':'Update software problem encountered'}, status_code=500) 
    except HTTPException as e:
        return JSONResponse(content={'detail':f'{e.detail}'}, status_code=404)


@softwares_router.get("/list",
    responses={
        200: {"model": List[SoftwareDetailed]},
        401: {"detail": "Not authorized user."},
        500: {"detail": "List softwares problem encountered"},
    })
async def list_all_software(current_user: UserReq = Depends(get_current_user)): 
    """
    # List All Softwares

    Retrieve a list of all softwares registered in the system.
    
    # Flow:
    1. The user's bearer token is used to authenticate the user and give access to this endpoint.
    2. The function `get_all` is called to retrieve all softwares from the system.
    3. The softwares are sorted based on their strength attribute.
    4. The details of each software are retrieved using the `get_details` function.
    5. If a software's details cannot be retrieved, that software is skipped.
    6. If there's an exception during the process, an error is returned.
    7. Upon successful retrieval, a list of software details is returned.

    # Returns:
        - A list of user details in the response body.

    # Errors:
        - 401: Not authorized user. 
        - 500: List softwares problem encountered. 

    # Usage:
    You can retrieve the list of softwares by making a GET request to the endpoint. Here's an example using JavaScript:

    ```
        const url = "/api/software/list";

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
        
        software_handler = SoftwareHandler()
        result = await software_handler.get_all()

        if result:
            return result
        else:
            return [] #JSONResponse(content={'detail':'No Software Found'}, status_code=200)
    except HTTPException as e:
        return JSONResponse(content={'detail':f'{e.detail}'}, status_code={e.status_code})


@softwares_router.get("/search",
    responses={
        200: {"detail": "Successful operation", "model": SoftwareDetailed},
        401: {"detail": "Not authorized user."},
        404: {"detail": "No stack have been found"},
        500: {"detail": "user not found"},
    },)
async def search(softwares: List[str] = Query([], description="Value to search in name, description fields"),
                companies: List[str] = Query([], description="Value to search in name, description fields"),
                stacks: List[str] = Query([], description="Value to search in name, description fields"),
                users: List[str] = Query([], description="Value to search in name, email, and bio fields"),
                current_user: UserReq = Depends(get_current_user)): 
    """
    # Software Lookup

    This endpoint allows users to search for softwares based on various criteria such as their names,
    and descriptions, or based on their employees, software projects, or technology stacks
    they are associated with. software

    # Flow:
    1. The user's bearer token is used to authenticate the user and give access to this endpoint.
    
    2. The user can provide search criteria in the query parameters: `users`, `softwares`, `softwares`, and `stacks`.
    3. The `users` parameter is used to search for values in the name, email, and bio fields of users.
    4. The `softwares` parameter is used to search for values in the name and description fields of companies.
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
        - 200: Returns a list of detailed softwares information that matches the search criteria.
        
    # Errors:    
        - 401: No authorized user.
        - 404: No software have been found.
        - 500: Search software problem encountered.

    # Note:
        - The search is case-insensitive. 
        - The search is performed using the `contains` operator, so the search criteria can be a substring of the actual value.
        - The search criteria can be a single value or multiple values separated by commas.
        - If multiple values are provided, the search will return results that match any of the values.
        - If no search criteria are provided, the endpoint will return a list of all softwares.

    # Observation:
    - Different weights are applied to search results based on their associations with the search criteria:
        - A weight of 1.0 is applied for direct user matches in the `softwares` parameter.
        - A weight of 0.8 is applied for matches in softwares, software projects, or technology stacks.
    - The current implementation returns a random list of user details if no search criteria are provided. This provides varied results.
    - In the future, more complex sorting criteria can be added to return softwares based on their similarities with the user making the request or other relevant criteria.

    # Usage:
    - To search for softwares with names or emails matching "company01", use:`/search?softwares=company01`
    - To search for softwares associated with employees named "John" or "Jane", use:  `/search?employees=john,jane`
    - To search for softwares associated with software projects named "Project A" or "Project B", use: `/search?softwares=project a,project b`
    - To search for softwares associated with technology stacks named "Python" or "JavaScript", use: `/search?stacks=python,javascript`
    - To search for softwares associated with companies named "company01" and software projects named "Project A" or "Project B", use: `/search?companies=company01&softwares=project a,project b`

    You can search for a software by making a POST request to the endpoint and passing the required parameters. Here's an example using JavaScript:

    ```
    javascript
        const url = "api/software/search?users=KEY_WORDS_FOR_USERS_SEPARETED_BY_COMA&companies=KEY_WORDS_FOR_COMPANIES_SEPARETED_BY_COMA&softwares=KEY_WORDS_FOR_SOFTWARES_SEPARETED_BY_COMA&stacks=KEY_WORDS_FOR_STACKS_SEPARETED_BY_COMA";

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
        software_handler = SoftwareHandler()
        result = await software_handler.search(users=users, companies=companies, softwares=softwares, stacks=stacks, current_user=current_user)
        return result
    except HTTPException as e:
        logger.error(f"Error searching software: {e}")
        return JSONResponse(content={'detail':f'{e.detail}'}, status_code={e.status_code})


@softwares_router.get("/{uid}",
    responses={
        200: {"model": SoftwareDetailed},
        401: {"detail": "Not authorized user."},
        404: {"detail": "Software hasn't been found"},
    },)
async def get_software(uid: str, current_user: UserReq = Depends(get_current_user)): 
    """
        # Get Software by uid

    Retrieve detailed information about a software by their uid.

    # Flow:
    1. The user's bearer token is used to authenticate the user and give access to this endpoint.
    2. The function `get_by_uid` is called to retrieve software from the system.
    3. The details of the software are retrieved using the `get_details` function.
    4. If there's an exception during the process, an error is returned.
    5. Upon successful retrieval, the software's details is returned.

    # Parameters:
    - **uid** (str): The uid of the software to retrieve details for.
   
    # Return:
        - If the software is found, detailed information about the software is returned.

    # Errors:
        - 401: Not authorized user.
        - 404: Software not found.
        - 500: Search software problem encountered.

    # Usage:

    You can retrieve the details of a software by making a GET request to the endpoint with the software's name. Here's an example using JavaScript:

    ```
        const url = `http://127.0.0.1:8000/api/software/SOFTWARE_UID`;

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
        software_handler = SoftwareHandler(uid=uid)
        result = await software_handler.get_by_uid()
        if result:
            return result
        else:
            return JSONResponse(content={'detail':'Software has not been found'}, status_code=404)
    except HTTPException as e:
        return JSONResponse(content={'detail':f'{e.detail}'}, status_code={e.status_code})