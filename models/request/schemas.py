from fastapi import Depends
from pydantic import BaseModel,  EmailStr, validator, constr, Field
from typing import Optional, List
from datetime import datetime
from fastapi import Depends, APIRouter, Form, Query, HTTPException

class StackReq(BaseModel):
    uid: Optional[str]
    name: str
    description: Optional[str]
    image: Optional[str]
    type: Optional[str]
    part_of: Optional[str]

    @validator('name', 'type')
    def convert_to_lower(cls, value):
        if isinstance(value, str):
            return value.lower().strip()
        return value
    
    @validator('part_of')
    def convert_to_list(cls, value):
        if isinstance(value, str):
            return value.split(',')
        return value
    
    @validator('type')
    def type_validator(cls, value):
        if value not in ['database', 'devops', 'backend', 'frontend']:
            raise ValueError('Invalid stack type')
        return value
    

    def dict(self, **kwargs):
        return {k: v for k, v in super().dict(**kwargs).items() if v is not None}

    
    class Config:
        schema_extra = {
            "example": {
                "name": "Stack Name",
                "description": "Stack description",
                "image": "Stack Image Url",
                "type": "database/devops/backend/frontend",
                "part_of": "stringfied list of stacks uid",
            }
        }

class SoftwareReq(BaseModel):
    uid: Optional[str]
    name: str
    client: Optional[str]
    project_type: Optional[str]
    problem: Optional[str]
    solution: Optional[str]
    comments: Optional[str]
    link: Optional[str]
    image: Optional[str]
    users: Optional[List[str]]
    stacks: Optional[List[str]]
    company: Optional[str]

    @validator('name', 'client', 'project_type')
    def convert_to_lower(cls, value):
        if isinstance(value, str):
            return value.lower().strip()
        return value
    
    def to_dict(self):
        try:
            softwares_dict= {
            "uid": self.uid if self.uid else None,
            "name": self.name if self.name else None,
            "image": self.image if self.image else None,
            "client": self.client if self.client else None,
            "project_type": self.project_type if self.project_type else None,
            "problem": self.problem if self.problem else None,
            "solution": self.solution if self.solution else None,
            "comments":  self.comments if self.comments else None,
            "link": self.link if self.link else None,
        }
            return softwares_dict
        except Exception as e:
            raise e

    @classmethod
    def from_record(cls, record):
        uid = record.get("uid", None)
        name = record.get("name", None)
        image = record.get("image", None)
        client = record.get("client", None)
        project_type = record.get("project_type", None)
        problem = record.get("problem", None)
        solution = record.get("solution", None)
        comments = record.get("comments", None)
        link = record.get("link", None)

        return cls(uid=uid, name=name, image=image, client=client, 
                   project_type=project_type, problem=problem, solution=solution, 
                   comments=comments, link=link)


    def dict(self, **kwargs):
        return {k: v for k, v in super().dict(**kwargs).items() if v is not None}

    class Config:
        schema_extra = {
            "example": {
                "uid": "Software Uid",
                "name": "Software Name",
                "description": "Software Description",
                "client": "Client Name",
                "project_type": "Project Type",
                "problem": "Problem Description",
                "solution": "Solution Description",
                "comments": "Comments",
                "link": "http://example.com",
            }
        }

class CompanyReq(BaseModel):
    uid: Optional[str]
    name: Optional[str]
    description: Optional[str]
    logo: Optional[str]
    softwares: Optional[List[str]]
    users: Optional[List[str]]

    @validator('name')
    def convert_to_lower(cls, value):
        if isinstance(value, str):
            return value.lower().strip()
        return value
    
    def to_dict(self):
        try:
            company_dict = {
            "uid": self.uid if self.uid else None,
            "name": self.name  if self.name else None,
            "description": self.description if self.description else None,
            "softwares": [software.to_dict() for software in self.softwares] if self.softwares else None
        }
            return company_dict
        except Exception as e:
            raise e


    def dict(self, **kwargs):
        return {k: v for k, v in super().dict(**kwargs).items() if v is not None}

    class Config:
        schema_extra = {
            "example": {
                "uid": "Company UID",
                "name": "Company Name",
                "logo": "Company Logo",
                "softwares": "Softwares' names separeted by comma",
            }
        }


class PostReq(BaseModel):
    uid: Optional[str]
    text: Optional[str]
    image: Optional[str]
    link: Optional[str]
    link_title: Optional[str]
    link_description: Optional[str]
    link_image: Optional[str]
    tagged_users: Optional[List[str]]
    tagged_companies: Optional[str]
    tagged_softwares: Optional[str]
    tagged_stacks: Optional[str]


    @validator('tagged_users')
    def convert_to_list(cls, value):
        if isinstance(value, str):
            return value.split(',')
        return value
    

    def dict(self, **kwargs):
        return {k: v for k, v in super().dict(**kwargs).items() if v is not None}

    class Config:
        schema_extra = {
            "example": {
                "uid": "Post Uid",
                "text": "Post Text",
                "image": "Post Image",
                "link": "http://example.com",
                "link_title": "Link Title",
                "link_description": "Link Description",
                "link_image": "Link Image",
                "tagged_users": "stringfied list of users uid",
            }
        }

class GetPostReq(BaseModel):
    skip: Optional[str] = '0'
    limit: Optional[str] = '10'

    def get_slice(self,) -> slice:
        return slice(int(self.skip), int(self.limit))
    



    # @validator('skip', 'limit')
    # def convert_to_list(cls, value):
    #     if isinstance(value, str):
    #         return int(value)

class PostLikeReq(BaseModel):
    user_uid: str
    like: str
    post_uid: str


    @validator('like')
    def convert_to_list(cls, value):
        if isinstance(value, str):
            match = value.lower().strip()
            if match not in ['true', 'false']:
                raise ValueError('Invalid liked value')
            if match == 'true':
                return True
            return False
        return value


    def dict(self, **kwargs):
        return {k: v for k, v in super().dict(**kwargs).items() if v is not None}

    class Config:
        schema_extra = {
            "example": {
                "uid": "Post Uid",
                "text": "Post Text",
                "image": "Post Image",
                "link": "http://example.com",
                "link_title": "Link Title",
                "link_description": "Link Description",
                "link_image": "Link Image",
                "tagged_users": "stringfied list of users uid",
            }
        }



class LocationReq(BaseModel):
    uid: Optional[str]
    country: Optional[str]
    city: Optional[str]
    address: Optional[str]

    def to_dict(self):
        try:
            location_dict = {
            "uid": self.uid if self.uid else None,
            "country": self.country if self.country else None,
            "city": self.city if self.city else None,
            "address": self.address if self.address else None,
        }
            return location_dict
        except Exception as e:
            raise e
        

    def validate(self):
        if not self.country and not self.city and not self.address:
            raise ValueError("At least one of the fields must be filled")
       
    @validator('country', 'city', 'address')
    def convert_to_lower(cls, value):
        if isinstance(value, str):
            return value.lower().strip()
        return value
        
    def dict(self, **kwargs):
        return {k: v for k, v in super().dict(**kwargs).items() if v is not None}

class UserReq(BaseModel):
    uid: Optional[str]
    email: Optional[EmailStr]
    name: Optional[str]
    preferred_name: Optional[str]
    role: Optional[str]
    joined_at: Optional[str]
    picture: Optional[str]
    twitter: Optional[str]
    linkedin: Optional[str]
    github: Optional[str]
    bio: Optional[str]
    active: Optional[bool]
    is_superuser: Optional[bool]
    password: Optional[str]

    @classmethod
    def from_record(cls, record):
        uid = record.get("uid", None)
        email = record.get("email", None)
        name = record.get("name", None)
        picture = record.get("picture", None)
        bio = record.get("bio", None)
        role = record.get("role", None)
        joined_at = record.get("joined_at", None)
        return cls(email=email, name=name, picture=picture, bio=bio)

    def to_dict(self):
        try:
            user_dict = {
            "uid": self.uid if self.uid else None,
            "email": self.email if self.email else None,
            "name": self.name if self.name else None,
            "picture": self.picture if self.picture else None,
            "bio": self.bio if self.bio else None,
            "role": self.role if self.role else None,
            "joined_at": self.joined_at if self.joined_at else None,
        }
            return user_dict
        except Exception as e:
            raise e
    class Config:
        schema_extra = {
            "example": {
                "email": "UserEmail",
                "name": "UserName",
                "picture": "UserPicture",
                "bio": "UserBio",
            }
        }
    
    @validator('email', 'name', 'preferred_name', 'role')
    def convert_to_lower(cls, value):
        if isinstance(value, str):
            return value.lower().strip()
        return value


    def dict(self, **kwargs):
        return {k: v for k, v in super().dict(**kwargs).items() if v is not None}

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    email: Optional[EmailStr]

class UserCreate(BaseModel):
    email: EmailStr
    is_superuser: bool = False

    @validator('email')
    def convert_to_lower(cls, value):
        if isinstance(value, str):
            return value.lower().strip()
        return value
    

class UserPasswordChange(BaseModel):
    password: str
    new_password: str
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('passwords do not match')
        return v

class CommentReq(BaseModel):
    user_uid: Optional[str]
    comment: str
    obj: str
    object_uid: str

    @validator('obj')
    def convert_to_lower(cls, value):
        if isinstance(value, str):
            values = ['comment', 'post']
            value = value.lower().strip()
            if value not in values:
                raise ValueError('Invalid obj value')
            return value
        return value
    
    class Config:
        schema_extra = {
            "example": {
                "user_uid": "User's Uid",
                "comment": "Comment Text",
                "obj": "comment/post",
                "object_uid": "Object's Uid",
            }
        }
    
    def dict(self, **kwargs):
        return {k: v for k, v in super().dict(**kwargs).items() if v is not None}
