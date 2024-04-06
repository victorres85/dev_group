import tracemalloc

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from models.handlers.company import CompanyHandler 
from models.handlers.software import SoftwareHandler
from models.handlers.user import UserHandler
from models.handlers.stack import StackHandler
from models.handlers.post import PostHandler
from config.cache import *
import asyncio

from starlette.requests import Request
from starlette.responses import HTMLResponse
from models.request.schemas import UserReq
from security.secure import get_current_user
from api.companies import companies_router
from api.login import login_router
from api.users import users_router
from api.softwares import softwares_router
from api.stacks import stacks_router
from api.images import images_router
from api.posts import posts_router
from api.comments import comments_router

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from api.login import google_login, logout
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from config.logger import logger

tracemalloc.start()

app = FastAPI()

# Set all CORS enabled origins
app.add_middleware(SessionMiddleware, secret_key="YEIwR!8YgdkmEWl8f%:T~2dp,i1K46f)@a?e[FzXBOL@pnmZ>J(r}L!MdS0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
# static files setup config
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(login_router, prefix='/api/auth')
app.include_router(users_router, prefix='/api/user', tags=['Users'])
app.include_router(companies_router, prefix='/api/company', tags=['Companies'])
app.include_router(softwares_router, prefix='/api/software', tags=['Softwares'])
app.include_router(stacks_router, prefix='/api/stack', tags=['Stacks'])
app.include_router(posts_router, prefix='/api/post', tags=['Posts'])
app.include_router(comments_router, prefix='/api/comment', tags=['Comments'])
app.include_router(images_router, prefix='/api/upload', tags=['Images'])

@app.get('/', include_in_schema=False)
def home(request: Request):
    try:
        logger.info("Home page accessed")
        return HTMLResponse('<a href="/api/auth/google_login">login</a>')
    except Exception as e:
        logger.error(f"Error accessing home page: {e}")
        raise HTTPException(status_code=500, detail="Home page problem encountered")
    
@app.get('/api/search', tags=['search'],
        summary="Search for users, companies, softwares, and stacks",
        description="Search for users, companies, softwares, and stacks",
        responses={
            400: {'detail': 'Invalid search option, please choose between user, company, software or stack'},
            401: {'detail': 'Not authorized user'},
            500: {'detail': 'Search problem encountered'},
            })
def search(on: str = Query(..., regex="^(?i)(user|company|software|stack|post)$", description="Options: user, company, software, stack, post"), 
        users: str = Query(None, description="Value to search in name, email, and bio fields"),
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
    1. User must be authenticated to access this endpoint.
    2. The user have to provide the object type to search for in the `on` parameter. Options: `user`, `company`, `software`, `stack`.
    3. The user can provide search criteria in the query parameters: `users`, `companies`, `softwares`, and `stacks`.
    4. The `users` parameter is used to search for values in the name, email, and bio fields of users.
    5. The `companies` parameter is used to search for values in the name and description fields of companies.
    6. The `softwares` parameter is used to search for values in the name and description fields of software projects.
    7. The `stacks` parameter is used to search for values in the name and description fields of technology stacks.
    8. If no search criteria are provided, the endpoint will return a list of user/company/software/stack details.
    9. Multiple values can be provided separated by commas for each parameter.
    10. The result is returned as a JSON response containing a list of detailed object information that matches the search criteria.
    
    # Parameters:
    - **on: **  The type of search to perform. Options: `user`, `company`, `software`, `stack`.
    - **employees: **  A comma-separated list of values to search in the name, email, and bio fields of users.
    - **companies: **  A comma-separated list of values to search in the name and description fields of companies.
    - **softwares: **  A comma-separated list of values to search in the name and description fields of software projects.
    - **stacks: **  A comma-separated list of values to search in the name and description fields of technology stacks.

    # Returns:
        - 200: Returns a list of detailed object information that matches the search criteria.
        
    # Errors:    
        - 401: No authorized user.
        - 404: No user/company/software/stack have been found.
        - 500: Search problem encountered.

    # Note:
        - The search is case-insensitive. 
        - The search is performed using the `contains` operator, so the search criteria can be a substring of the actual value.
        - The search criteria can be a single value or multiple values separated by commas.
        - If multiple values are provided, the search will return results that match any of the values.
        - If no search criteria are provided, the endpoint will return a list of all companies.

    # Observation:
    - Different weights are applied to search results based on their associations with the search criteria:
        - A weight of 1.0 is applied for direct matches.
        - A weight of 0.8 is applied for 2nd layer matches.
        - A weight of 0.6 is applied for 3rd layer matches.

    # Usage:
    - To search for companies with names or emails matching "company01", use:`/search?companies=company01`
    - To search for companies associated with users named "John" or "Jane", use:  `/search?users=john,jane`
    - To search for companies associated with software projects named "Project A" or "Project B", use: `/search?softwares=project a,project b`
    - To search for companies associated with technology stacks named "Python" or "JavaScript", use: `/search?stacks=python,javascript`
    - To search for companies associated with companies named "company01" and software projects named "Project A" or "Project B", use: `/search?companies=company01&softwares=project a,project b`

    You can search for a company by making a POST request to the endpoint and passing the required parameters. Here's an example using JavaScript:

    ```javascript
        const url = "api/search?users=USERS&companies=COMPANIES&softwares=SOFTWARES&stacks=STACKS";

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
        if on not in ['user', 'company', 'software', 'stack', 'post']:
            raise HTTPException(status_code=400, detail="Invalid search option, please choose between user, company, software or stack")
        users = users.split(",") if users else []
        companies = companies.split(",") if companies else []
        softwares = softwares.split(",") if softwares else []
        stacks = stacks.split(",") if stacks else []
        if on == 'user':
            return UserHandler.search(users=users, companies=companies, softwares=softwares, stacks=stacks, current_user=current_user)
        if on == 'software':
            return SoftwareHandler.search(users=users, companies=companies, softwares=softwares, stacks=stacks, current_user=current_user)
        if on == 'company':
            return CompanyHandler.search(users=users, companies=companies, softwares=softwares, stacks=stacks, current_user=current_user)
        if on == 'stack':
            return StackHandler.search(users=users, companies=companies, softwares=softwares, stacks=stacks, current_user=current_user)
        if on == 'post':
            return PostHandler.search(users=users, companies=companies, softwares=softwares, stacks=stacks, current_user=current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Search problem encountered")


@app.get("/api/fetch-meta-tags", include_in_schema=False)
def fetch_meta_tags(request: Request, url: str = Query(None)):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        tags = {'title':'', 'description':'', 'site_name':'', 'image':'', 'image_width':0, 'image_height':0}
        accepted_tags = [ 'og:title', 'og:description', 'og:site_name', 'og:image', 'og:image:width', 'og:image:height']
        with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) as browser:
            browser.get(url)
            wait = WebDriverWait(browser, 1)
            meta_tags = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'meta')))
            for t in meta_tags:
                if t.get_attribute('property') and t.get_attribute('property') in accepted_tags:
                    tags[t.get_attribute('property').replace('og:','').replace(':','_')] = t.get_attribute('content')
            print(tags)              
    except Exception as e:
        print(e)

    return tags

def custom_openapi():
    try:
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="",  
            description="Dev Community API",
            version="1.0.0",
            routes=app.routes,
        )
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    except Exception as e:
        raise e

app.openapi = custom_openapi
asyncio.set_event_loop(asyncio.new_event_loop())
