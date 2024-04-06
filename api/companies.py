import json

from fastapi import Form, HTTPException

from fastapi import Depends, APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse

from typing import List, Optional
from models.request.detailed_schemas import CompanyDetailed
from models.request.schemas import CompanyReq, UserReq
from models.handlers.company import CompanyHandler

from security.secure import get_current_user, is_superuser


companies_router = APIRouter()

@companies_router.post("/add",
    responses={
            200: {"model": CompanyReq},
            400: {"detail": "Stack already exists"},
            401: {"detail": "Not authorized user."},
            500: {"detail": "Create user problem encountered"},
        },)
async def add_company(
    name: str = Form(...), 
    description: Optional[str] = Form(None), 
    softwares: Optional[str] = Form(None, description="List of Software Objects"),
    logo: Optional[str] = Form(None, description='Company Logo Url'), 
    locations: Optional[str] = Form(None, description='List of Location objects: \{"country":"...","city":"...","address...":""\}'), 
    users: Optional[str] = Form(None, description='List of users objects'), 
    current_user: UserReq = Depends(get_current_user)
):
    """
    # Company Registration

    This endpoint is used to register a new company in the system. It requires \
    the company's name, and can optionally include the company's: description, \
    logoand locations, as well as a list of softwares which have been created \
    by the company. The company's name will be validated and stored in lowercase \
    format for consistency.

    # Flow:
    1. The user's bearer token is used to identify the existing user in the system.
    2. If the company's name already exists in the system, an exception is raised.
    3. If the company's name is unique, a new company is created with the given name, logo, and description.
    4. If the company creation process fails, an appropriate error message is returned.
    5. If the company creation process is successful, the software's will be associated with the company.
    6. An asynchronous task is created to clear the 'comapanies' cache and refresh it with the updated list of all companies.
    7. The newly created company is returned to the user.

    # Parameters:
    - name: The name of the company.
    - logo: The logo of the company, an image file.
    - description: An optional description of the company.
    - softwares: An optional list of software names that has been developed by the company.

    # Returns:
        - The details of the newly added company.

    # Errors:
        - 400: The company already exists, the logo file size exceeds the maximum limit, or the logo file is not a valid image.
        - 401: Not authorized User.
        - 500: An error was encountered while attempting to create the company.

    # Notes:
    - The company's logo will be saved in '/static/images/logos/' with the filename being the company's name and the original file extension.
    - The company's logo will be removed from the system if the company creation process fails.
    
    # Usage:
    You can create a new company by making a POST request to the endpoint and passing the required parameters. Here's an example using JavaScript:

    ```javascript
        const url = "/api/company/add?name=COMPANY_NAME&description=DESCRIPTION&softwares=SOFTWARES";

        const formData = new FormData();
        formData.append("name", "COMPANY_NAME");
        formData.append("description", "DESCRIPTION");
        formData.append("softwares", "STRINGFIED LIST OF SOFTWARES UIDs");
        formData.append("logo", "LOGO_URL");

        fetch(url, {
            method: 'POST',
            headers: {
                'authorization': `Bearer ${token}`
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('There was an error!', error));
    ```
    Replace `COMPANY_NAME`, `DESCRIPTION`, and `SOFTWARES` with the appropriate values for the company you are creating.

    """

    try:
        users=[u['uid'] for u in json.loads(users) if u != '']
        softwares= [s['uid'] for s in json.loads(softwares) if s != '']
        locations=json.loads(locations)
        company_handler = CompanyHandler(name=name, description=description, logo=logo, softwares=softwares, users=users, locations=locations)
        result = await company_handler.insert_obj()
        if result:
            return result
        else: 
            raise HTTPException(status_code=500, detail="Create company problem encountered") 
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Create company problem encountered")


@companies_router.delete("/delete/{uid}",
    responses={
            200: {"detail": "Company has been deleted"},
            401: {"detail": "Not authorized user."},
            404: {"detail": "Company hasn't been found"},
            500: {"detail": "Delete company problem encountered"},
        },)
def delete_obj_by_uid(uid: str, current_user: UserReq = Depends(is_superuser)): 
    """
    # Delete a Company

    This endpoint deletes a company from the system based on the provided company name. 

    # Flow:
    1. The user's bearer token is used to identify the existing user in the system.
    2. The company uid is passed as a URL path parameter to this endpoint.
    3. The 'delete_obj' function is invoked, which deletes the company node and all relationships (such as 'has_employees' and 'created_software') from the database.
    4. If the operation fails, an appropriate error message is returned.
    5. An asynchronous task is created to clear the 'companies' cache and refresh it with the updated list of all companies.
    3. If the operation is successful, a message 'Company has been deleted' is returned.

    # Returns:
        {'detail':'Company has been deleted'}

    # Errors:
        - 401: Not authorized user.
        - 404: Company hasn't been found.
        - 500: Delete company problem encountered.

    # Note:
        Only a superuser is allowed to delete companies. If a non-superuser tries to delete a company, a 403 error will be returned.

    # Usage:

    You can delete a company by making a DELETE request to the endpoint with the company uid you want to delete. Here's an example using JavaScript:

    ```
        const url = "/api/company/delete/COMPANY_UID_TO_DELETE";

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
    
    Replace `COMPANY_UID_TO_DELETE`, with the appropriate company name.

    """
    try:
        result = CompanyHandler(uid=uid).delete_obj()
        if result:
            return {'detail':'company has been deleted'}
        else: 
            raise HTTPException(status_code=500, detail="Delete company problem encountered")
    except Exception as e:
        raise e


@companies_router.patch("/update",
    responses={
            200: {"model": CompanyDetailed},
            401: {"detail": "Not authorized user."},
            404: {"detail": "Company hasn't been found"},
            500: {"detail": "Update company problem encountered"},
        },)
async def company_update(
    uid: str = Form(..., description=""),
    name: Optional[str] = Form(None, description=""),
    logo: Optional[str] = Form(None, description='Company Logo Url'), 
    description: Optional[str] = Form(None, description="s"),
    users: Optional[str] = Form(None, description='List of users uids'), 
    locations: Optional[str] = Form(None, description='List of Location objects: \{"country":"...","city":"...","address...":""\}'), 
    softwares: Optional[str] = Form(None, description="List of Software uids"),
    current_user: UserReq = Depends(get_current_user)
    ):
    """
    # Update Company Information

    This endpoint allows authorized users to update a company's information, including its name, description, logo, and associated softwares.

    # Flow:
    1. The user's bearer token is used to identify the existing user in the system..
    2. The user can provide the company's name, description, a new logo url and a list of associated software uids.
    3. If softwares are provided, the relationships between the company and the software will be updated. Invalid or non-existing software names will result in an error.
    4. If users are provided, the relationships between the company and the users will be updated. Invalid or non-existing user names will result in an error.
    5. If locations are provided, the relationships between the company and the locations will be updated. Invalid or non-existing location names will result in an error.
    6. If the update process fails, an appropriate error message is returned.
    7. An asynchronous task is created to clear the 'companies' cache and refresh it with the updated list of all companies.
    8. The updated details of the company will be returned as a response.
    6. If any errors occur, appropriate error messages will be returned.

    # Parameters:
    - **name:** (Optional[str]) The name of the company.
    - **description:** (Optional[str]) Optional description of the company.
    - **softwares:** (Optional[str]) A string containing the software names associated with the user, separated by commas.
    - **logo:** (UploadFile) Optional uploaded file representing the company's logo.
    - **current_user:** The authenticated user making the request.

    # Returns:
        - 200: Company object.

    # Errors:
        - 401: Not authorized user.
        - 404: Company hasn't been found.
        - 500: Update company problem encountered or other unexpected errors.

    # Usage:
    You can use JavaScript to make a PATCH request to this endpoint, providing the required parameters.

    ```javascript
    const url = "/api/company/update?name=COMPANY_NAME&description=DESCRIPTION&softwares=SOFTWARES";

    const formData = new FormData();
    formData.append("name", "COMPANY_NAME");
    formData.append("description", "DESCRIPTION");
    formData.append("softwares", "STRINGFIED LIST OF SOFTWARES UIDs");
    formData.append("users", "STRINGFIED LIST OF USERS UIDs");
    formData.append("locations", "STRINGFIED LIST OF LOCATION OBJECTS");
    formData.append("logo", "LOGO_URL");

    fetch(url, {
        method: 'PATCH',
        headers: {
            'authorization': `Bearer Token`
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('There was an error!', error));
    ```

    Replace `COMPANY_NAME`, `DESCRIPTION`, and `SOFTWARES` with the appropriate values for the company you are updating.
    """
    try:
        users=[u['uid'] for u in json.loads(users) if u != '']
        softwares= [s['uid'] for s in json.loads(softwares) if s != '']
        locations=json.loads(locations)
        company_handler = CompanyHandler(uid=uid, name=name, description=description, logo=logo, softwares=softwares, users=users, locations=locations)
        result = await company_handler.update_obj()
        if result:
            return result
        else:
            raise HTTPException(status_code=500, detail="Update company problem encountered")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Update company problem encountered")


@companies_router.get("/list",
    responses={
            200: {"model": List[CompanyDetailed]},
            401: {"detail": "Not authorized user."},
            500: {"detail": "List company problem encountered"},
        },)
async def list_all_company(current_user: UserReq = Depends(get_current_user)): 
    """
    # List All Companies

    Retrieve a list of all companies registered in the system.


    # Flow:
    1. The user's bearer token is used to authenticate the user and give access to this endpoint.
    2. The function `get_all` is called to retrieve all companies from the system.
    3. The companies are sorted based on their strength attribute.
    4. The details of each company are retrieved using the `get_details` function.
    5. If a company's details cannot be retrieved, that company is skipped.
    6. If there's an exception during the process, an error is returned.
    7. Upon successful retrieval, a list of company details is returned.

    # Returns:
        - A list of user details in the response body.

    # Errors:
        - 401: Not authorized user. 
        - 500: List companies problem encountered. 

    # Usage:
    You can retrieve the list of companies by making a GET request to the endpoint. Here's an example using JavaScript:

    ```javascript
        const url = "/api/company/list";

        fetch(url, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
                'authorization': `Bearer Token',
            },
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('There was an error!', error));

    """
    try:
        company_handler = CompanyHandler()
        result = await company_handler.get_all()
        if result:
            return result
        raise HTTPException(status_code=500, detail="List company problem encountered")
    except Exception as e:
        raise e
    
@companies_router.post("/search",
    responses={
            200: {"model": List[CompanyDetailed]},
            401: {"detail": "Not authorized user."},
            404: {"detail": "No company have been found."},
            500: {"detail": "List company problem encountered"},
        },)
async def search(employees: str = Query(None, description="Value to search in name, email, and bio fields"),
                companies: str = Query(None, description="Value to search in name, description fields"),
                softwares: str = Query(None, description="Value to search in name, description fields"),
                stacks: str = Query(None, description="Value to search in name, description fields"),
                current_user: UserReq = Depends(get_current_user)):
    """
    # Company Lookup

    This endpoint allows users to search for companies based on various criteria such as their names,
    and desccriptions, or based on their employees, software projects, or technology stacks
    they are associated with.

    # Flow:
    1. The user's bearer token is used to identify the existing user in the system.
    2. The user can provide search criteria in the query parameters: `users`, `companies`, `softwares`, and `stacks`.
    3. The `users` parameter is used to search for values in the name, email, and bio fields of users.
    4. The `companies` parameter is used to search for values in the name and description fields of companies.
    5. The `softwares` parameter is used to search for values in the name and description fields of software projects.
    6. The `stacks` parameter is used to search for values in the name and description fields of technology stacks.
    7. If no search criteria are provided, the endpoint will return a list of user details.
    8. Multiple values can be provided separated by commas for each parameter.
    9. The endpoint then calls the `search` function with the provided search criteria and the `current_user`.
    10. The result is returned as a JSON response containing a list of detailed user information that matches the search criteria.
    
    # Parameters:
    - **employees: **  A comma-separated list of values to search in the name, email, and bio fields of users.
    - **companies: **  A comma-separated list of values to search in the name and description fields of companies.
    - **softwares: **  A comma-separated list of values to search in the name and description fields of software projects.
    - **stacks: **  A comma-separated list of values to search in the name and description fields of technology stacks.

    # Returns:
        - 200: Returns a list of detailed companies information that matches the search criteria.
        
    # Errors:    
        - 401: No authorized user.
        - 404: No company have been found.
        - 500: Search company problem encountered.

    # Note:
        - The search is case-insensitive. 
        - The search is performed using the `contains` operator, so the search criteria can be a substring of the actual value.
        - The search criteria can be a single value or multiple values separated by commas.
        - If multiple values are provided, the search will return results that match any of the values.
        - If no search criteria are provided, the endpoint will return a list of all companies.

    # Observation:
    - Different weights are applied to search results based on their associations with the search criteria:
        - A weight of 1.0 is applied for direct user matches in the `companies` parameter.
        - A weight of 0.8 is applied for matches in companies, software projects, or technology stacks.
    - The current implementation returns a random list of user details if no search criteria are provided. This provides varied results.
    - In the future, more complex sorting criteria can be added to return companies based on their similarities with the user making the request or other relevant criteria.

    # Usage:
    - To search for companies with names or emails matching "company01", use:`/search?companies=company01`
    - To search for companies associated with employees named "John" or "Jane", use:  `/search?employees=john,jane`
    - To search for companies associated with software projects named "Project A" or "Project B", use: `/search?softwares=project a,project b`
    - To search for companies associated with technology stacks named "Python" or "JavaScript", use: `/search?stacks=python,javascript`
    - To search for companies associated with companies named "company01" and software projects named "Project A" or "Project B", use: `/search?companies=company01&softwares=project a,project b`

    You can search for a company by making a POST request to the endpoint and passing the required parameters. Here's an example using JavaScript:

    ```javascript
        const url = "api/company/search?employees=KEY_WORDS_FOR_USERS_SEPARETED_BY_COMA&companies=KEY_WORDS_FOR_COMPANIES_SEPARETED_BY_COMA&softwares=KEY_WORDS_FOR_SOFTWARES_SEPARETED_BY_COMA&stacks=KEY_WORDS_FOR_STACKS_SEPARETED_BY_COMA";

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
        employees = employees.split(",") if employees else []
        companies = companies.split(",") if companies else []
        softwares = softwares.split(",") if softwares else []
        stacks = stacks.split(",") if stacks else []
        company_handler = CompanyHandler(companies=companies, softwares=softwares, stacks=stacks, users=employees, current_user=current_user)
        result = await company_handler.search()
        if result:
            return result
        raise HTTPException(status_code=500, detail="Search company problem encountered.")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Search company problem encountered.")
    
@companies_router.get("/{uid}",
    responses={
            200: {"model": CompanyDetailed},
            404: {"detail": "No company have been found found."},
            500: {"detail": "Search company problem encountered."},
        },)
async def get_company(uid: str, current_user: UserReq = Depends(get_current_user)):     
    """
    # Get Company by Name

    Retrieve detailed information about a company by their name.

    # Flow:
    1. The user's bearer token is used to authenticate the user and give access to this endpoint.
    2. The function `get_by_uid` is called to retrieve company from the system.
    3. The details of the company are retrieved using the `get_details` function.
    4. If there's an exception during the process, an error is returned.
    5. Upon successful retrieval, the company's details is returned.

    # Parameters:
    - **name** (str): The name of the company to retrieve details for.
   
    # Return:
        - If the company is found, detailed information about the company is returned.

    # Errors:
        - 401: Not authorized user.
        - 404: Company not found.
        - 500: Search company problem encountered.

    # Usage:

    You can retrieve the details of a company by making a GET request to the endpoint with the company's uid. Here's an example using JavaScript:

    ```javascript
        const url = `http://127.0.0.1:8000/api/company/COMPANY_UID`;

        fetch(url, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
                'authorization': `Bearer Token`,
            },
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('There was an error!', error));
    ```
    Replace `COMPANY_UID`, with the appropriate company uid.
    """
    try:
        company_handler = CompanyHandler(uid=uid)
        result = await company_handler.get_by_uid()
        if not result:
            return JSONResponse(content={'detail':'company not found'}, status_code=500)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Search company problem encountered")
    

@companies_router.get("/{uid}/stacks",
responses={
        200: {"model": CompanyDetailed},
        404: {"detail": "No company have been found found."},
        500: {"detail": "Search company problem encountered."},
    },)
async def company_stacks(uid: str, current_user: UserReq = Depends(get_current_user)):     
    """
    # Get Company by Name

    Retrieve detailed information about a company by their name.

    # Flow:
    1. The user's bearer token is used to identify the existing user in the system.
    2. The function first receives a company's unique identifier (uid) as an argument.
    3. It then runs a Cypher query on the Neo4j database to find all the technology \
    stacks (`st:Stack`) known by users (`u:User`) who work for the company (`c:Company`) with the given uid.
    4. The query returns the uid, name, description, and type of each technology stack.
    5. The results of the query are then formatted into a list of dictionaries, \
    where each dictionary represents a technology stack and contains its uid, name, description, and type.
    6. If the query and formatting are successful, the function returns the list of technology stacks.
    7. If any exception occurs during the above steps, the function catches the exception and returns False.

    # Parameters:
    - **name** (str): The name of the company to retrieve details for.
   
    # Return:
        - If the company is found, detailed information about the company is returned.

    # Errors:
        - 401: Not authorized user.
        - 404: Company not found.
        - 500: Search company problem encountered.

    # Usage:

    You can retrieve the details of a company by making a GET request to the endpoint with the company's uid. Here's an example using JavaScript:

    ```javascript
        const url = `http://127.0.0.1:8000/api/company/COMPANY_UID`;

        fetch(url, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
                'authorization': `Bearer Token
            },
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('There was an error!', error));
    ```
    Replace `COMPANY_UID`, with the appropriate company uid.
    """
    try:
        company_handler = CompanyHandler(uid=uid)
        result = await company_handler.get_company_stacks()
        if not result:
            return JSONResponse(content={'detail':'company not found'}, status_code=500)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Search company problem encountered")