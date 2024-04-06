from services import upload_image

from fastapi import Form, HTTPException, UploadFile, File

from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse

from models.request.schemas import UserReq

from security.secure import get_current_user
from config.logger import logger
import random

images_router = APIRouter()


@images_router.post("/image",
responses={
    201: {"detail": "Image uploaded successfully."},
    401: {"detail": "Not authorized user."},
    500: {"detail": "Upload image problem encountered"},
},
)
async def upload_img(image: UploadFile = File(...), directory: str = Form(...),
                     current_user: UserReq = Depends(get_current_user)):
    """    
    # Software Registration

    This endpoint is used to upload new images into the system.

    # Flow:
    1. Users uploads the image file.
    2. This function will save the image in the correct directory and return the url in which the image will be found.

    # Parameters:
    - name: The name of the image.
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

    # Notes:
    - The software's image will be saved in '/static/images/softwares/' with the filename being the software's name and the original file extension.
    - The software's image will be removed from the system if the software creation process fails.
    
    # Usage:
    You can create a new software by making a POST request to the endpoint and passing the required parameters. Here's an example using JavaScript:

    ```javascript
        const url = "api/software/add?<SOFTWARE_NAME>, <SOFTWARE_DESCRIPTION>, <COMPANY_NAME_>";

        const formData = new FormData();
        formData.append("image", new File(["/path/to/your/image.png"], "image.png", { type: "image/png" }));

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
    Replace <SOFTWARE_NAME>, <SOFTWARE_DESCRIPTION>, <COMPANY_NAME_> (name of the company which has created the Software)with the appropriate values for the software you are creating.
    """
    try:
        hash = random.getrandbits(12)
        name = ''
        if directory == 'users':
            name = current_user['name'].lower().replace(" ", "_") + str(hash) + ".jpg"
        else:
            name = image.filename.lower().replace(" ", "_").split('.')[0] + str(hash) +".jpg"
        # Pass the bytes to the upload_image function
        img_url = await upload_image(image, name, directory, current_user['uid'])
        if img_url:
            logger.info(f"Image uploaded successfully: {name}")
            return JSONResponse(status_code=201, content={"imgUrl": img_url})
        else:
            logger.info(f"Error uploading image: {name}")
            raise HTTPException(status_code=500, detail="Upload image problem encountered")
    except HTTPException as e:
        logger.error(f"Error uploading image: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(status_code=500, detail="Upload image problem encountered")
