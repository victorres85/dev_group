from pydantic import BaseModel,  EmailStr, validator
from typing import Optional, List, Dict
from .schemas import *
from datetime import datetime

class CompanyDetailed(BaseModel):
    uid: Optional[str]
    name: str
    logo: Optional[bytes]
    description: Optional[str]
    employees: Optional[List[str]]
    softwares: Optional[List[str]]
    stacks: Optional[List[str]]
    locations: Optional[List[str]]

    @validator('name', 'logo')
    def convert_to_lower(cls, value):
        if isinstance(value, str):
            return value.lower().strip()
        return value
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Company Name",
                "logo": "Company Logo",
                "description": "Company Description",
                "employees": [
                    {"name": "Employee Name",
                     "email": "Employee Email"}
                    ],
                "softwares": [{
                            "name": "Software User Worked On",
                            }],
                "stacks": [
                    {"name": "Stack User Knows"}
                    ],
                "locations": [
                    {"country": "",
                     "city": "",
                     "address": ""}
                    ],
            }
        }
    def to_dict(self):
        try:
            company_dict ={
            'uid': self.uid if self.uid else None,
            'name': self.name if self.name else None,
            'logo': self.logo if self.logo else None,
            'description': self.description if self.description else None,
            'employees': [employee.to_dict() for employee in self.employees] if self.employees else None,
            'softwares': [software.to_dict() for software in self.softwares] if self.softwares else None,
            'stacks': [stack.to_dict() for stack in self.stacks] if self.stacks else None,
            'locations': [location.to_dict() for location in self.locations] if self.locations else None,
        }
            return company_dict
        except Exception as e:
            raise e


class StackDetailed(BaseModel):
    uid: Optional[str]
    name: str
    description: Optional[str]
    type: Optional[str]
    image: Optional[str]
    part_of: Optional[StackReq]
    users: Optional[List[UserReq]]
    softwares: Optional[List[SoftwareReq]]
    companies: Optional[List[CompanyReq]]

    def to_dict(self):
        try:
            stack_dict= {
            'uid': self.uid if self.uid else None,
            'name': self.name if self.name else None,
            'description': self.description if self.description else None,
            'type': self.type if self.type else None,
            'image': self.image if self.image else None,
            'part_of': self.part_of.to_dict() if self.part_of else None,
            'users': [user.to_dict() for user in self.users] if self.users else None,
            'softwares': [software.to_dict() for software in self.softwares] if self.softwares else None,
            'companies': [company.to_dict() for company in self.companies] if self.companies else None
        }
            return stack_dict
        except Exception as e:
            raise e

    class Config:
        schema_extra = {
            "example": {
                "name": "Stack Name",
                "description": "Stack description",
                "type": "database/devops/backend/frontend",
                "part_of": "Language it has been build upon",
                "employees": [
                    {"name": "Employee Name",
                     "email": "Employee Email"}
                    ],
                "softwares": [{
                            "name": "Software User Worked On",
                            }],
                "companies": [
                    {"name": "Company Name"}
                    ],

            }
        }

    @validator('name', 'type')
    def convert_to_lower(cls, value):
        if isinstance(value, str):
            return value.lower().strip()
        return value

class StackUpdate(BaseModel):
    uid: Optional[str]
    name: str
    description: Optional[str]
    image: Optional[str]
    type: Optional[str]
    part_of: Optional[StackReq]
    # posts: Optional[List[PostReq]]

    class Config:
        schema_extra = {
            "example": {
                "name": "Stack Name",
                "description": "Stack description",
                "type": "database/frotend/backend/devops",
                "part_of": "Language it has been build upon",
            }
        }

    @validator('name', 'type')
    def convert_to_lower(cls, value):
        if isinstance(value, str):
            return value.lower().strip()
        return value

    def to_dict(self):
        try:
            stack_dict = {
            'uid': self.uid if self.uid else None,
            'name': self.name   if self.name else None,
            'description': self.description if self.description else None,
            'image': self.image if self.image else None,
            'type': self.type if self.type else None,
            'part_of': self.part_of.to_dict() if self.part_of else None
            }
            return stack_dict
        except Exception as e:
            raise e

class SoftwareDetailed(BaseModel):
    uid: Optional[str]
    name: str
    image: Optional[str]
    client: Optional[str]
    project_type: Optional[str]
    problem: Optional[str]
    solution: Optional[str]
    comments: Optional[str]
    link: Optional[str]


    users: Optional[List[UserReq]]
    stacks: Optional[List[StackReq]]
    company: Optional[CompanyReq]
    # posts: Optional[List[PostReq]]

    @validator('name')
    def convert_to_lower(cls, value):
        if isinstance(value, str):
            return value.lower().strip()
        return value


    class Config:
        schema_extra = {
            "example": {
                "uid": "Software's Uid",
                "name": "Software's Name",
                "image": "Software's image",
                "client": "Software's client",
                "project_type": "Software's Type",
                "problem": "Software's problem",
                "solution": "Software's solution",
                "comments": "Software's comments",
                "link": "Software's link",
                "users": [
                    {"name": "User Name",
                     "email": "User Email"}
                    ],
                "company": {
                            "name": "Software User Worked On",
                            },
                "stacks": [
                    {"name": "Stack User Knows"}
                    ],
            }
        }
    
    def to_dict(self):
        try:
            software_dict = {
            'uid': self.uid if self.uid else None,
            'name': self.name if self.name else None,
            'image': self.image if self.image else None,
            'client': self.client if self.client else None,
            'project_type': self.project_type if self.project_type else None,
            'problem': self.problem if self.problem else None,
            'solution': self.solution if self.solution else None,
            'comments': [comment.to_dict() for comment in self.comments] if self.comments else None,
            'link': self.link if self.link else None,
            'users': [user.to_dict() for user in self.users] if self.users else None,
            'stacks': [stack.to_dict() for stack in self.stacks] if self.stacks else None,
            'company': self.company.to_dict() if self.company else None
        }
            return software_dict
        except Exception as e:
            raise e

class SoftwareUpdate(BaseModel):
    uid: Optional[str]
    name: str
    description: Optional[str]
    companies: Optional[CompanyReq]
    # posts: Optional[List[PostReq]]

    @validator('name')
    def convert_to_lower(cls, value):
        if isinstance(value, str):
            return value.lower().strip()
        return value
    
    def to_dict(self):
        try:
            software_dict = {
            'uid': self.uid if self.uid else None,
            'name': self.name if self.name else None,
            'description': self.description if self.description else None,
            'companies': [company.to_dict() for company in self.companies] if self.companies else None,
            }
            return software_dict
        except Exception as e:
            raise e

    class Config:
        schema_extra = {
            "example": {
                "name": "Software Name",
                "description": "Software Description",
                "company": {
                            "name": "Software User Worked On",
                            },
            }
        }
    

class PostDetailed(BaseModel):
    uid: Optional[str]
    posted_by: Optional[str]
    created_by: Optional[dict]
    text: Optional[str]
    image: Optional[str]
    link: Optional[str]
    link_title: Optional[str]
    link_description: Optional[str]
    link_image: Optional[str]
    created_at: Optional[str]
    tagged_users: Optional[List] 
    tagged_softwares: Optional[List]
    tagged_stacks: Optional[List]
    tagged_companies: Optional[List]
    like_by: Optional[List]
    commented_by: Optional[List]
    comments: Optional[List]
    created_at: Optional[str]
    updated_at: Optional[str]
    comment_count: Optional[int]
    likes_count: Optional[int]

    class Config:
        schema_extra = {
            "example": {
                "uid": "Post Uid",
                "text": "Post Text",
                "image": "Post Image",
                "tagged_users": "Post tagged users",
                "tagged_softwares": "Post tagged softwares",
                "tagged_stacks": "Post tagged stacls",
                "likes": "Post Likes",
                "comments": 'Post Comments'
            }
        }
    def to_dict(self):
        try:
            post_dict = {
            'uid': self.uid if self.uid else None,
            'posted_by': self.posted_by if self.posted_by else None,
            'created_by': self.created_by if self.created_by else None,
            'text': self.text if self.text else None,
            'image': self.image if self.image else None,
            'link': self.link if self.link else None,
            'link_title': self.link_title if self.link_title else None,
            'link_description': self.link_description if self.link_description else None,
            'link_image': self.link_image if self.link_image else None,
            'tagged_users': [user.to_dict() for user in self.tagged_users] if self.tagged_users else None,
            'tagged_softwares': [software.to_dict() for software in self.tagged_softwares] if self.tagged_softwares else None,
            'tagged_stacks': [stack.to_dict() for stack in self.tagged_stacks] if self.tagged_stacks else None,
            'tagged_companies': [company.to_dict() for company in self.tagged_companies] if self.tagged_companies else None,
            'like_by': self.like_by.to_dict() if self.like_by else None,
            'commented_by': self.commented_by.to_dict() if self.commented_by else None,
            'comments': [comment.to_dict() for comment in self.comments],
            'created_at': self.created_at if self.created_at else None,
            'updated_at': self.updated_at if self.updated_at else None,
            'comment_count': self.comment_count if self.comment_count else None,
            'likes_count': self.likes_count if self.likes_count else None,
        }
            return post_dict
        except Exception as e:
            raise e


    class Config:
        schema_extra = {
            "example": {
                "title": "Post Title",
                "subtitle": "Post Subtitle",
                "text": "Post Text",
                "image": "Post Image",
                "users": [
                    {"name": "User Name",
                     "email": "User Email"}
                    ],
                "stacks": [
                    {"name": "Stack User Knows"}
                    ],
                "softwares": [{
                            "name": "Software User Worked On",
                            }],
            }
        }
    

class CommentDetailed(BaseModel):
    uid: Optional[str]
    comment: str
    created_by: Optional[UserReq]
    commented_by: Optional[UserReq]
    commented_on_post: Optional[PostReq]
    commented_on_comment: Optional[CommentReq]
    likes_count: Optional[int]
    comment_count: Optional[int]
    comments: Optional[List]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    def to_dict(self):
        try:
            comment_dict = {
            'uid': self.uid if self.uid else None,
            'comment': self.comment if self.comment else None,
            'created_by': self.created_by.to_dict() if self.created_by else None,
            'commented_by': self.commented_by.to_dict() if self.commented_by else None,
            'commented_on_post': self.commented_on_post.to_dict() if self.commented_on_post else None,
            'commented_on_comment': self.commented_on_comment.to_dict() if self.commented_on_comment else None,
            'likes_count': self.likes_count if self.likes_count else None,
            'comment_count': self.comment_count if self.comment_count else None,
            'comments': [comment.to_dict() for comment in self.comments] if self.comments else None,
            'created_at': self.created_at if self.created_at else None,
            'updated_at': self.updated_at if self.updated_at else None,
        }
            return comment_dict
        except Exception as e:
            raise e

class LikeDetailed(BaseModel):
    uid: Optional[str]
    created_at: str
    updated_at: str
    comment: Optional[CommentReq]
    post: Optional[PostReq]
    liked_by: Optional[UserReq]

    def to_dict(self):
        try:
            like_dict = {
            'uid': self.uid if self.uid else None,
            'created_at': self.created_at if self.created_at else None,
            'updated_at': self.updated_at if self.updated_at else None,
            'comment': self.comment if self.comment else None,
            'post': self.post.to_dict() if self.post else None,
            'liked_by': self.liked_by.to_dict() if self.liked_by else None
        }
            return like_dict
        except Exception as e:
            raise e

class EventDetailed(BaseModel):
    uid: Optional[str]
    title: str
    subtitle: Optional[str]
    text: Optional[str]
    image: List[str]
    date: Optional[datetime]
    time: Optional[datetime]
    created_by: Optional[UserReq]
    attending: Optional[List[Dict[UserReq, CompanyReq]]]

    class Config:
        schema_extra = {
            "example": {
                "title": "Event Title",
                "subtitle": "Event Subtitle",
                "text": "Event Text",
                "image": "Event Image",
                "date": "dd/mm/YYYY",
                "time": "hh:mm",
                "created_by": "User name",
                "attendees": [
                    {"name": "Attendee Name",
                     "company": "Company Attendee works for"}
                    ]
            }
        }
    def to_dict(self):
        try:
            event_dict = {
            'uid': self.uid if self.uid else None,
            'title': self.title if self.title else None,
            'subtitle': self.subtitle if self.subtitle else None,
            'text': self.text if self.text else None,
            'image': self.image if self.image else None,
            'date': self.date if self.date else None,
            'time': self.time if self.time else None,
            'created_by': self.created_by.to_dict() if self.created_by else None,
            'attending': self.attending if self.attending else None
        }
            return event_dict
        except Exception as e:
            raise e

class ManagerDetailed(BaseModel):
    uid: Optional[str]
    name: Optional[str]
    email: Optional[EmailStr]


class UserDetailed(BaseModel):
    uid: Optional[str]
    email: Optional[EmailStr]
    name: Optional[str]
    role: Optional[str]
    preferred_name: Optional[str]
    joined: Optional[str]
    twitter: Optional[str]
    linkedin: Optional[str]
    github: Optional[str]
    picture: Optional[str]
    bio: Optional[str]
    company: Optional[CompanyReq]
    posts: Optional[List[PostDetailed]]
    softwares: Optional[List[SoftwareReq]]
    stacks: Optional[List[StackReq]]
    active: Optional[bool]

    class Config:
        schema_extra = {
            "example": {
                "name": "UserName",
                "picture": "UserPicture",
                "bio": "UserBio",
                "company": {
                            "name": "Company User Works for",
                            },
                "softwares": [{
                            "name": "Software User Worked On",
                            }],
                "stacks": [
                    {"name": "Stack User Knows",
                     "type": "database/devops/frontend/backend"}
                    ],
                "active": True
            }
        }

    @validator('email', 'name', 'picture')
    def convert_to_lower(cls, value):
        if isinstance(value, str):
            return value.lower().strip()
        return value

    def to_dict(self):
        try:
            user_dict = {
                'uid': self.uid if self.uid else None,
                'email': self.email if self.email else None,
                'name': self.name if self.name else None,
                'role': self.role if self.role else None,
                'preferred_name': self.preferred_name if self.preferred_name else None,
                'joined': self.joined if self.joined else None,
                'twitter': self.twitter if self.twitter else None,
                'linkedin': self.linkedin if self.linkedin else None,
                'github': self.github if self.github else None,
                'picture': self.picture if self.picture else None,
                'bio': self.bio if self.bio else None,
                'company': self.company if self.company else None,
                'posts': [post.to_dict() for post in self.posts] if self.posts else None,
                'softwares': [software.to_dict() for software in self.softwares] if self.softwares else None,
                'stacks': [stack.to_dict() for stack in self.stacks] if self.stacks else None,
                'active': self.active if self.active else None,
            }
            return user_dict
        except Exception as e:
            raise e