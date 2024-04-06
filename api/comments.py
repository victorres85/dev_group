from fastapi import Depends, APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
from models.handlers.comment import CommentHandler
from models.request.detailed_schemas import CommentDetailed 
from models.request.schemas import UserReq, CommentReq
from security.secure import get_current_user, is_superuser

comments_router = APIRouter()


@comments_router.post(
    "/add",
    responses={
        200: {"model": CommentDetailed},
        400: {"detail": "comment already exists"},
        409: {"detail": "Only one parent comment can be added"},
        401: {"detail": "Not authorized user."},
        500: {"detail": "Create comment problem encountered"},
    },
)
async def add_comment(
    comment: CommentReq,
    # comment: str = Form(None, description="comment text"), 
    # object_uid: str = Form(None, description="comment/post object uid"),
    # obj: str = Form(None, description="comment or post"),
    current_user: UserReq = Depends(get_current_user)):
    """
    # Add Comment

    This endpoint is used to add a new comment to a post or another comment in the system. It requires the comment text, the unique identifier (UID) of the object the comment is associated with, and the type of the object (either 'comment' or 'post').

    # Flow:
    1. The user must provide the comment text, the UID of the object the comment is associated with, and the type of the object.
    2. A Comment node is created with the provided comment text and saved to the database.
    3. The `patchCommentConnections` function is called to create the necessary connections between the new comment, the user who created it, and the object it's associated with.
    4. The `get_details` function is called to retrieve the details of the newly created comment.
    5. If the comment details are successfully retrieved, they are returned to the user. If not, an HTTPException is raised with a status code of 500 and a detail message of "Insert stack problem encountered".

    # Parameters:
    - **comment:** (str) The text of the new comment.
    - **object_uid:** (str) The UID of the object the comment is associated with.
    - **obj:** (str) The type of the object the comment is associated with (either 'comment' or 'post').

    # Returns:
    - The details of the newly added comment.

    # Errors:
    - 500: An error was encountered while attempting to create the comment or retrieve its details.

    # Usage:
    You can add a new comment by making a POST request to the endpoint and passing the required parameters. Here's an example using JavaScript:

    ```
    const url = "api/comment/add";
    const formData = new FormData();
    formData.append("comment", "Your comment text");
    formData.append("object_uid", "UID of the object");
    formData.append("obj", "comment or post");

    fetch(url, {
        method: 'POST',
        headers: {
            'accept': 'application/json',
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('There was an error!', error));
    ```
    """
    try:
        comment.user_uid = current_user['uid']
        comment_dict = comment.dict()
        comment_handler = CommentHandler(**comment_dict)
        result = await comment_handler.insert_obj()
        if result:
            return result
        else: 
            raise HTTPException(status_code=500, detail="Create comment problem encountered.")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Create comment problem encountered.")



@comments_router.get("/{uid}",
    responses={
        200: {"model": CommentDetailed},
        500: {"detail": "comment hasn't been found"},
    },)
async def get_comment(uid: str, current_user: UserReq = Depends(get_current_user)): 
    """
    # Get comment by Uid

    Retrieve detailed information about a comment by their uid.

    # Parameters:
    - **uid** (str): The uid of the comment to retrieve details for.
   
    # Return:
        - If the comment is found, detailed information about the comment is returned.

    # Errors:
        - 401: Not authorized user.
        - 404: Comment not found.
        - 500: Search comment problem encountered.

    # Usage:

    You can retrieve the details of a comment by making a GET request to the endpoint with the comment's uid. Here's an example using JavaScript:

    ```javascript
        const url = `http://127.0.0.1:8000/api/comment/COMMENT_UID`;

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
    Replace `COMMENT_UID`, with the appropriate comment uid.
    """
    try:
        comment_handler = CommentHandler(uid=uid)
        result = await comment_handler.get_by_uid(uid)
        if result:
            return result
        return JSONResponse(content={"message":"Comment hasn't been found"}, status_code=500) 
    except HTTPException as e:
        return HTTPException(status_code=500, detail="comment problem encountered")


@comments_router.delete("/delete/{uid}",
    responses={
        200: {"detail": "comment has been deleted"},
        401: {"detail": "Not authorized user."},
        404: {"detail": "comment hasn't been found"},
        500: {"detail": "delete comment problem encountered"},
    },)
async def comment_delete(uid: str, current_user: UserReq = Depends(get_current_user)): 
    """
    Delete a comment

    This endpoint deletes a comment from the system based on the provided comment name. 

    # Flow:
    1. The comment name is passed as a URL path parameter to this endpoint.
    2. The 'delete_obj' function is invoked, which deletes the comment node and all relationships (such as 'has_employees' and 'created_software') from the database.
    3. If the operation is successful, a message 'comment has been deleted' is returned.
    4. If the operation fails, an appropriate error message is returned.

    # Parameters:
    - **name:** (str) The name of the comment to delete.

    # Returns:
        {'detail':'comment has been deleted'}

    # Errors:
        - 401: Not authorized user.
        - 404: comment hasn't been found.
        - 500: Delete comment problem encountered.

    # Note: 
        Only a superuser is allowed to delete comments. If a non-superuser tries to delete a comment, a 403 error will be returned.    
    # Usage:

    You can delete a comment by making a DELETE request to the endpoint with the comment name you want to delete. Here's an example using JavaScript:

    ```javascript
        const url = "/api/comment/delete/comment_NAME_TO_DELETE";

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
    Replace `comment_NAME_TO_DELETE`, with the appropriate comment name.
    """
    try:
        comment_handler = CommentHandler(uid=uid)
        result = await comment_handler.delete_obj()
        if result:
            return {'message':'comment has been deleted'}
        else: 
            raise HTTPException(status_code=404, detail="comment hasn't been found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="delete comment problem encountered")

@comments_router.patch("/update",
    responses={
        200: {"model": CommentDetailed},
        401: {"detail": "Not authorized user."},
        404: {"detail": "comment hasn't been found"},
        500: {"detail": "Update comment problem encountered"},
    },)
async def comment_update(
    commentUid: Optional[str] = Form(None, description="comment/post object uid"),
    comment: Optional[str] = Form(None, description="comment text"), 
    current_user: UserReq = Depends(get_current_user)): 
    """
    # Update comment Information

    This endpoint allows authorized users to update a comment's information, including its name, description, image, and associated comment.

    # Flow:
    1. The user must be authorized to access this endpoint.
    2. The user can provide the comment's name, description, a new image file, and an associated comment name.
    3. If a image is provided, it will be uploaded and the path will be stored. The image must be a valid image and not exceed the maximum file size of 2 MB.
    4. If part_of is provided, the relationships between the comment and the parent's comment will be updated. Invalid or non-existing software names will result in an error.
    5. The updated details of the comment will be saved and returned as a response.
    6. If any errors occur, appropriate error messages will be returned.

    # Parameters:
    - **name:** (Optional[str]) The name of the comment.
    - **description:** (Optional[str]) Optional description of the comment.
    - **comment_type:** (Optional[str]) A string containing the comments type ['database', 'frontend', 'backend', 'devops'].
    - **part_of:** (Optional[str]) A string containing the this comment parent comment's name.
    - **image:** (UploadFile) Optional uploaded file representing the comment's image.
    - **current_user:** The authenticated user making the request.

    # Returns:
        - 200: `CommentDetailed` model object if the update is successful.

    # Errors:
        - 401: Not authorized user.
        - 404: comment hasn't been found.
        - 409: Only one parent comment can be added.
        - 409: comment type must be one of ['database', 'frontend', 'backend', 'devops']
        - 500: Update comment problem encountered or other unexpected errors.

    # Usage:
    You can use JavaScript to make a PATCH request to this endpoint, providing the required parameters.

    ```javascript
    const url = "/api/comment/update?name=<comment_NAME>,description=<comment_DESCRIPTION>,comment_type=<comment_TYPE>,part_of=<PART_OF>";

    const formData = new FormData();
    formData.append("image", new File(["/path/to/your/image.png"], "image.png", { type: "image/png" }));

    fetch(url, {
        method: 'PATCH',
        headers: {
            'accept': 'application/json',
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('There was an error!', error));
    ```

    Replace <comment_NAME>,<comment_DESCRIPTION>,<comment_TYPE>,<PART_OF> with the appropriate values for the comment you are updating.
    """
    try:
        comment_handler = CommentHandler(uid=commentUid, comment=comment)
        result = await comment_handler.update_obj()
        if result:
            return result
        else: 
            raise HTTPException(status_code=500, detail="Update comment problem encountered")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Update comment problem encountered")

@comments_router.post("/like",
    responses={
        200: {"model": CommentDetailed},
        401: {"detail": "Not authorized user."},
        404: {"detail": "comment hasn't been found"},
        500: {"detail": "Like comment problem encountered"},
    },)
async def like_comment(user_uid: str = Form(...), comment_uid: str = Form(...), like: bool = Form(...), current_user: UserReq = Depends(get_current_user)):
    """
    # Like/Unlike a comment

    This endpoint allows users to like or unlike a comment.

    # Flow:
    1. The user must be authenticated to access this endpoint.
    2. The user must provide the comment's uid, the user's uid, and a boolean value indicating whether to like or unlike the comment.
    3. The endpoint calls the `like_comment` function with the provided parameters.
    4. If the operation is successful, the comment's details are returned.
    5. If the operation fails, an appropriate error message is returned.

    # Parameters:
    - **comment_uid:** (str) The uid of the comment to like/unlike.
    - **user_uid:** (str) The uid of the user liking/unliking the comment.
    - **like:** (bool) A boolean value indicating whether to like or unlike the comment.

    # Returns:
        - 200: Returns the comment's details if the operation is successful.

    # Errors:
        - 401: Not authorized user.
        - 404: comment hasn't been found.
        - 500: Like comment problem encountered.

    # Usage:
    You can like/unlike a comment by making a GET request to the endpoint and passing the required parameters. Here's an example using JavaScript:

    ```javascript
        const url = "/api/comment/like?comment_uid=comment_UID&user_uid=USER_UID&like=LIKE";

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
    Replace `comment_UID`, `USER_UID`, and `LIKE` with the appropriate values.
    """
    try:
        comment_handler = CommentHandler(uid=comment_uid, user_uid=user_uid, liked=like)
        result = await comment_handler.comment_like()
        if result:
            return result
        else: 
            raise HTTPException(status_code=500, detail="Like comment problem encountered")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Like comment problem encountered")
