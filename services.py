import os
import io
from pathlib import Path
from PIL import Image, UnidentifiedImageError
import glob
from config.models import User
from fastapi import  HTTPException
from aiohttp_sendgrid import Sendgrid
import random
from fastapi import HTTPException
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
from config.models import Company, Software, Stack
from config.logger import logger

load_dotenv('.env')

api_key = os.getenv('SENDGRID_API_KEY')
from_email = os.getenv('SENDGRID_FROM_EMAIL')
mailer = Sendgrid(api_key=api_key)
ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
SECRET_KEY = os.getenv('AWS_SECRET_KEY')
REGION = os.getenv('AWS_REGION')

ROOT_DIR = Path(__file__).parent
MAX_FILE_SIZE = 20 * 1024  # 2MB

async def send_email_verification(email: str, password: str) -> None:
    """
    _summary_

    Args:
        email (str): _description_
        verification_code (str): _description_

    Returns:
        None
    """
    to = email
    sender = from_email
    subject = '''Welcome to Dev Group'''
    content = f'''
    <h1>You can access the your account with the password below</h1>
    <h3>{password}<h3>'''
    await mailer.send(to, sender, subject, content)


def generate_password():
    """
    Creates a new 10 digit password, symbols optional.

    :return
        (string): unique string password.
    """

    characters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '@', '#', '$', '%', '&', '?']

    pwd = ''

    for i in range(10):  # one iteration per password char
        pwd += random.choice(characters)

    return pwd


def connect_nodes(user_node, items, getter_method, not_found_detail, disconnect_method, connect_method):
    if items is not None:
        for item in items:
            node = getter_method(name=item.name)
            if node is None:
                raise HTTPException(status_code=404, detail=not_found_detail)
        disconnect_method()
        for item in items:
            node = getter_method(name=item.name)
            connect_method(node, force_create=True)


def update_obj_connections(user, user_node):
    connect_nodes(user_node, user.company, Company.nodes.get_or_none, "Company not found", 
                  user_node.works_for.disconnect_all, user_node.works_for.connect)

    connect_nodes(user_node, user.stacks, Stack.nodes.get_or_none, "Stack not found", 
                  user_node.knows.disconnect_all, user_node.user_knows)

    connect_nodes(user_node, user.softwares, Software.nodes.get_or_none, "Software not found", 
                  user_node.worked_on.disconnect_all, user_node.user_worked_on)
    


async def upload_image(image: bytes, name: str, directory: str, uid: str) -> None:
    try:
        
        image_path = f'assets/img/{directory}/{name}'
        image_bytes = await image.read()
        full_path = 'https://teamnet-company01.s3.eu-west-2.amazonaws.com/' + image_path
        try:
            img = Image.open(io.BytesIO(image_bytes))
        except UnidentifiedImageError:
            logger.error("The file is not a valid image.")
            raise HTTPException(status_code=400, detail="The file is not a valid image.")
        
        
        # Resize the image
        if directory == 'softwares':
            max_size = (600, 1200)
        else:
            max_size = (300, 300)
        img.thumbnail(max_size)

        # Convert the image back to bytes
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG')
        image_bytes = byte_arr.getvalue()

        s3 = boto3.client(
            's3',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION
        )
        try:
            s3.put_object(Body=image_bytes, Bucket='teamnet-company01', Key=image_path)
        except NoCredentialsError:
            logger.error("AWS credentials not available")
            raise HTTPException(status_code=500, detail="AWS credentials not available")

        if directory == 'users':
            user = User.nodes.get_or_none(uid=uid)
            user.picture = full_path
            user.save()
        logger.info(f"Image uploaded: {full_path}")
        return full_path
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(status_code=500, detail=f"{e}")


def remove_image(path : str = None, name: str = None, directory: str = None) -> None:

    # Search for any image files that match the name in the given directory
    image_paths = path 
    if image_paths:
        try:
            os.remove(image_paths)
            return None
        except Exception as e:
            pass

    image_paths = glob.glob(str(ROOT_DIR / 'static' / 'images' / directory / f"{name.strip().replace(' ', '')}.*"))
    for image_path in image_paths:
        if image_path and os.path.exists(image_path) and os.path.isfile(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                pass
