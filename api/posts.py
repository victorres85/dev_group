from fastapi import Depends, APIRouter, Form, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
from models.handlers.post import PostHandler
from models.request.schemas import UserReq, PostReq, PostLikeReq, GetPostReq
from models.request.detailed_schemas import PostDetailed
from security.secure import get_current_user
import json

posts_router = APIRouter()

@posts_router.post(
    "/add",
    responses={
        200: {"model": PostDetailed},
        400: {"detail": "Stack already exists"},
        409: {"detail": "Only one parent stack can be added"},
        401: {"detail": "Not authorized user."},
        500: {"detail": "Create stack problem encountered"},
    },
)
async def add_post(
    post_data: PostReq,
    current_user: UserReq = Depends(get_current_user)):
    """
    # Post Creation

    This endpoint is used to create a new post in the system. It requires the post's text and can optionally include an image, a link with its title, description, and image, and tagged users.

    # Flow:
    1. The user must provide the post's text, and optionally an image, a link with its title, description, and image, and tagged users.
    2. The `insert_post` function is called with the provided parameters.
    3. The function checks if a post with the given parameters can be created in the system. If it can't, an exception is raised.
    4. If the post can be created, a new post is created with the given parameters.
    5. The new post is saved in the system and its details are returned.

    # Parameters:
    - text: The text of the post.
    - image: An optional image for the post.
    - link: An optional link for the post.
    - link_title: An optional title for the post's link.
    - link_description: An optional description for the post's link.
    - link_image: An optional image for the post's link.
    - tagged_users: An optional list of users tagged in the post.

    # Returns:
        - The details of the newly created post.

    # Errors:
        - 400: The post could not be created due to invalid input.
        - 401: Not authorized User.
        - 500: An error was encountered while attempting to create the post.

    # Usage:
    You can create a new post by making a POST request to the endpoint and passing the required parameters. Here's an example using JavaScript:

    ```
    const url = "api/post/add";

    const formData = new FormData();
    formData.append("text":..., "image":..., "link":..., "link_title":..., "link_description":..., "link_image":..., "tagged_users":...);


    fetch(url, {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer TOKEN'
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('There was an error!', error)
    );
    ```
    Replace `TOKEN` with the appropriate token.
    """
    try:
        post_data=post_data.dict()
        post_data['userUid'] = current_user['uid']
        post_handler = PostHandler(**post_data)

        result = await post_handler.insert_post()
        if result:
            return result
        else: 
            raise HTTPException(status_code=500, detail="Create post problem encountered.")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Create post problem encountered.")


@posts_router.delete("/delete/{uid}",
    responses={
        200: {"detail": "Stack has been deleted"},
        401: {"detail": "Not authorized user."},
        404: {"detail": "Stack hasn't been found"},
        500: {"detail": "delete stack problem encountered"},
    },)
async def post_delete(uid: str, current_user: UserReq = Depends(get_current_user)): 
    """
    Delete a Post

    This endpoint deletes a post from the system based on the provided post uid. 

    # Flow:
    1. The post uid is passed as a URL path parameter to this endpoint.
    2. The 'delete_obj' function is invoked, which deletes the post node and all relationships (such as 'has_employees' and 'created_software') from the database.
    3. If the operation is successful, a message 'Post has been deleted' is returned.
    4. If the operation fails, an appropriate error message is returned.

    # Parameters:
    - **name:** (str) The name of the post to delete.

    # Returns:
        {'detail':'Post has been deleted'}

    # Errors:
        - 401: Not authorized user.
        - 404: Post hasn't been found.
        - 500: Delete post problem encountered.

    # Note: 
        Only a superuser is allowed to delete posts. If a non-superuser tries to delete a post, a 403 error will be returned.    
    
    # Usage:

    You can delete a post by making a DELETE request to the endpoint with the post uid you want to delete. Here's an example using JavaScript:

    ```
        const url = "/api/post/delete/POST_UID_TO_DELETE";

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
    """
    try:
        post_handler = PostHandler(uid=uid)
        result = await post_handler.delete_obj()
        if result:
            return {'message':'Post has been deleted'}
        else: 
            raise HTTPException(status_code=404, detail="Post hasn't been found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="delete post problem encountered")

@posts_router.patch("/update",
    responses={
        200: {"model": PostDetailed},
        401: {"detail": "Not authorized user."},
        404: {"detail": "Post hasn't been found"},
        500: {"detail": "Update post problem encountered"},
    },)
async def post_update(
    uid: str = Form(None, description="The post's uid"),
    text: Optional[str] = Form(None, description="Post text"), 
    image: Optional[str] = Form(None, description="Post image"), 
    link: Optional[str] = Form(None, description="Post link"),
    link_title: Optional[str] = Form(None, description="Post link title"),
    link_description: Optional[str] = Form(None, description="Post link description"),
    link_image: Optional[str] = Form(None, description="Post link image"),
    tagged_users: Optional[str] = Form(None, description="Post tagged users"),
    current_user: UserReq = Depends(get_current_user)): 
    """
    # Update Post Information

    This endpoint allows authorized users to update a post's information, including its text, image, link, link title, link description, link image, and tagged users.

    # Flow:
    1. The user must be authorized to access this endpoint.
    2. The user can provide the post's uid, text, image, link, link title, link description, link image, and tagged users.
    3. If an image is provided, it will be uploaded and the path will be stored. The image must be a valid image and not exceed the maximum file size of 2 MB.
    4. The updated details of the post will be saved and returned as a response.
    5. If any errors occur, appropriate error messages will be returned.

    # Parameters:
    - **uid:** str The uid of the post.
    - **text:** (Optional[str]) The text of the post.
    - **image:** (Optional[str]) The image of the post.
    - **link:** (Optional[str]) The link of the post.
    - **link_title:** (Optional[str]) The title of the link.
    - **link_description:** (Optional[str]) The description of the link.
    - **link_image:** (Optional[str]) The image of the link.
    - **tagged_users:** (Optional[str]) The users tagged in the post.
    - **current_user:** The authenticated user making the request.

    # Returns:
        - 200: `PostDetailed` model object if the update is successful.

    # Errors:
        - 401: Not authorized user.
        - 404: Post hasn't been found.
        - 500: Update post problem encountered or other unexpected errors.

    # Usage:
    You can use JavaScript to make a PATCH request to this endpoint, providing the required parameters.

    ```javascript
    const url = "/api/post/update";

    const formData = new FormData();
    formData.append("uid":..., "text":..., "image":..., "link":..., "link_title":..., "link_description":..., "link_image":..., "tagged_users":...);

    fetch(url, {
        method: 'PATCH',
        headers: {
            'accept': 'application/json
            'Authorization': 'Bearer TOKEN'
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('There was an error!', error));
    ```

    """
    try:
        list_of_users=[u['uid'] for u in json.loads(tagged_users) if u != ''] if tagged_users else []
        post_handler = PostHandler(userID=current_user.uid, image=image, link=link, link_title=link_title, link_description=link_description, link_image=link_image, tagged_users=list_of_users, text=text)
        result = await post_handler.insert_post()
        if result:
            return result
        else: 
            raise HTTPException(status_code=500, detail="Update stack problem encountered")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Update stack problem encountered")


@posts_router.post("/list",
    responses={
        200: {"model": List[PostDetailed]},
        401: {"detail": "Not authorized user."},
        404: {"detail": "No Posts have been found"},
        500: {"detail": "List softwares problem encountered"},
    })
async def list_post(
    data : GetPostReq,
    current_user: UserReq = Depends(get_current_user)): 
    """
    # List Posts

    Retrieve a list of posts registered in the system, based on the skip and limit parameters.

    # Parameters:
    - **skip:** (Optional[int]) The number of posts to be skipped.
    - **limit:** (Optional[int]) The number of posts to be returned.
    - **current_user:** The authenticated user making the request.

    # Returns:
        - A list of post details in the response body.

    # Errors:
        - 401: Not authorized user. 
        - 500: List posts problem encountered. 

    # Usage:
    You can retrieve the list of posts by making a GET request to the endpoint. Here's an example using JavaScript:

    ```
    const url = "/api/post/list";

    fetch(url, {
        method: 'GET',
        headers: {
            'accept': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('There was an error!', error));
    """
    try:
        data = data.dict()
        post_handler = PostHandler(skip=data['skip'], limit=data['limit'])
        result = await post_handler.get_posts()
        if result:
            return result
        else:
            return JSONResponse(content={'detail':'No Posts have been found'}, status_code=404)
    except Exception as e:
        return JSONResponse(content={'detail':'List softwares problem encountered'}, status_code=500)


@posts_router.post("/like",
    responses={
        200: {"model": PostDetailed},
        401: {"detail": "Not authorized user."},
        404: {"detail": "Post hasn't been found"},
        500: {"detail": "Like post problem encountered"},
    },)
def like_post(post : PostLikeReq, 
              current_user: UserReq = Depends(get_current_user)):
    """
    # Like/Unlike a Post

    This endpoint allows users to like or unlike a post.

    # Flow:
    1. The user must be authenticated to access this endpoint.
    2. The user must provide the post's uid, the user's uid, and a boolean value indicating whether to like or unlike the post.
    3. The endpoint calls the `like_post` function with the provided parameters.
    4. If the operation is successful, the post's details are returned.
    5. If the operation fails, an appropriate error message is returned.

    # Parameters:
    - **post_uid:** (str) The uid of the post to like/unlike.
    - **user_uid:** (str) The uid of the user liking/unliking the post.
    - **like:** (bool) A boolean value indicating whether to like or unlike the post.

    # Returns:
        - 200: Returns the post's details if the operation is successful.

    # Errors:
        - 401: Not authorized user.
        - 404: Post hasn't been found.
        - 500: Like post problem encountered.

    # Usage:
    You can like/unlike a post by making a GET request to the endpoint and passing the required parameters. Here's an example using JavaScript:

    ```
        javascript
        const url = "/api/stack/like";

        const formData = new FormData();
        formData.append("post_uid":..., "user_uid":..., "like":...);

        fetch(url, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
                'Authorization': 'Bearer TOKEN'
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('There was an error!', error));
    ```
        """
    try:
        postDict = post.dict()
        like = postDict.pop('like')
        post_handler = PostHandler(userUid=postDict['user_uid'], uid=postDict['post_uid']) 
        result = post_handler.like_post(like=like)
        if result:
            return result
        else: 
            raise HTTPException(status_code=500, detail="Like post problem encountered")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Like post problem encountered")



@posts_router.get("/search",
    responses={
        200: {"model": List[PostDetailed]},
        401: {"detail": "Not authorized user."},
        404: {"detail": "No stack have been found"},
        500: {"detail": "Stack hasn't been found"},
    },)
async def search(users: str = Query(None, description="Value to search in name, email, and bio fields"),
           queries: str = Query(None, description="Value to search in name, description fields"),
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
        result = await PostHandler.search(users=users, queries=queries)
        if result:
            return result
        raise HTTPException(status_code=404, detail="No stack have been found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Search stack problem encountered")


@posts_router.get("/{uid}",
    responses={
        200: {"model": PostDetailed},
        500: {"detail": "Stack hasn't been found"},
    },)
async def get_post(uid: str, current_user: UserReq = Depends(get_current_user)): 
    """
    # Get Stack by Uid

    Retrieve detailed information about a stack by their name.

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
        post_handler = PostHandler(userUid=current_user['uid'], uid=uid)
        result = await post_handler.get_by_uid()
        if result:
            return result
        return JSONResponse(content={"message":"Stack hasn't been found"}, status_code=500) 
    except Exception as e:
        return JSONResponse(content={"message":"Stack hasn't been found"}, status_code=500)