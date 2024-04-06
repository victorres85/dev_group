import asyncio
from collections import defaultdict
from typing import Dict, Any, List
import json
from config.neo4j_connect import neo4j_driver as db
from models.request.schemas import  UserReq
from fastapi import HTTPException
import random
from config.models import Company, Software, Stack, User
from passlib.context import CryptContext
import asyncio
from datetime import datetime
from config.cache import update_cache, CACHE
from config.logger import logger 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserHandler:
    def __init__(self, 
                 uid: str = None,
                    name: str = None,
                    email: str = None,
                    role: str = None,
                    joined_at: str = None,
                    password: str = None,
                    active: bool = None,
                    picture: str = None,
                    bio: str = None,
                    twitter: str = None,
                    github: str = None,
                    linkedin: str = None,
                    preferred_name: str = None,
                    is_superuser: bool = None,
                    is_active: bool = True,
                    stacks: List[str] = [],
                    softwares: List[str] = [],
                    company_uid: str = None,


    ):
        self.uid = uid
        self.name = name.lower() if name else None
        self.email = email.lower() if email else None
        self.role = role.lower() if role else None
        self.joined_at = joined_at
        self.password = password
        self.active = active
        self.picture = picture
        self.bio = bio
        self.twitter = twitter
        self.github = github
        self.linkedin = linkedin
        self.preferred_name = preferred_name.lower() if preferred_name else None
        self.is_superuser = is_superuser
        self.is_active = is_active
        self.stacks = stacks
        self.softwares = softwares
        self.company_uid = company_uid
        self.payload = {'name': self.name or None, 
                        'email': self.email or None, 
                        'role': self.role or None, 
                        'joined_at': self.joined_at or None, 
                        'password': self.password or None, 
                        'active': self.active or None, 
                        'picture': self.picture or None, 
                        'bio': self.bio or None, 
                        'twitter': self.twitter or None, 
                        'github': self.github or None, 
                        'linkedin': self.linkedin or None, 
                        'preferred_name': self.preferred_name or None, 
                        'is_superuser': self.is_superuser or None,
                        'is_active': self.is_active,
                        }
        
    async def get_details(self, uid: str) -> dict:
        try:
            # Find the user by uid
            user = User.nodes.get_or_none(uid=uid)
            if user is None:
                return None
            user_data = await user.full_dict()
            return user_data
        except Exception as e:
            logger.error(f"Error getting user details: {e}")
            return None

    def insert_obj(self) -> bool: 
        try:
            # Check if email has been previously registered
            existing_user = User.nodes.get_or_none(email=self.email)
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")
            # Create new User 
            password = pwd_context.hash('1234')
            payload = self.payload
            payload['password'] = password
            new_user = User(**payload)
            new_user.save()
            asyncio.create_task(update_cache('users', self.get_all))

            return True
        except HTTPException as e: 
            logger.error(f"Error inserting user: {e}")
            return False
            
    def insert_obj_from_oauth(self) -> bool: 
        try:
            # Check if email has been previously registered
            existing_user = User.nodes.get_or_none(email=self.email)
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")
            # Create new User 
            new_user = User(email=self.email, name=self.name, picture=self.picture, active=True)
            new_user.save()
            asyncio.create_task(update_cache('users', self.get_all))
            return True
        except HTTPException as e: 
            logger.error(f"Error inserting user: {e}")
            return None

    async def update_obj(self) -> dict: 
        try:
            # Find the User node by uid
            user_node = User.nodes.get_or_none(uid=self.uid)
            if user_node is None:
                raise HTTPException(status_code=404, detail="User not found")
            for key, value in self.payload.items():
                if value is not None:
                    setattr(user_node, key, value)
            user_node.updated_at = datetime.now()
            user_node.save()

            self.patchUserConnections(user_node=user_node, stacks=self.stacks, softwares=self.softwares, company_uid=self.company_uid)

            asyncio.create_task(update_cache('users', self.get_all))
            return await self.get_details(self.uid)
        
        except HTTPException as e:
            logger.error(f"Error updating user: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False

    def patchUserConnections(self, user_node: User, company_uid: str = None, stacks:List[str] = [], softwares:List[str] = []):
        try:
            # Handle user relationships
            if company_uid is not None:
                company = Company.nodes.get_or_none(uid=company_uid.strip())
                if company is None:
                    raise HTTPException(status_code=404, detail="Company not found")
                user_node.works_for.disconnect_all()
                user_node.works_for.connect(company)

            if stacks is not None and stacks != ['null']:
                user_node.knows.disconnect_all()
                for st in stacks:
                    stack = Stack.nodes.get_or_none(uid=st.strip())
                    if stack is None:
                        raise HTTPException(status_code=404, detail="Stack not found")  
                    user_node.knows.connect(stack)
            if softwares is not None and softwares != ['null']:
                user_node.worked_on.disconnect_all()
                for s in softwares:
                    software = Software.nodes.get_or_none(uid=s.strip())
                    if software is None:
                        raise HTTPException(status_code=404, detail="Software not found")    
                    user_node.worked_on.connect(software)
                
        except Exception as e:
            logger.error(f"Error patching user connections: {e}")
            pass


    async def get_all(self) -> List:
        try:
            cache_key = 'users'
            result = await CACHE.get(cache_key)
            if result is not None:
                return result
            users = User.nodes.all()
            sorted_users = sorted(users, key=lambda user: user.strenght)
            result = []
            for user in sorted_users:
                user_data = await user.full_dict()
                result.append(user_data)

            await CACHE.set(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return None

    def delete_obj(self) -> bool:
        try:
            # Find the user by email
            user = User.nodes.get_or_none(email=self.email)
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            # Disconnect all relationships
            user.knows.disconnect_all()
            user.works_for.disconnect_all()
            user.worked_on.disconnect_all()

            # Delete the user node
            user.delete()

            return True
        except HTTPException as e:
            logger.error(f"Error deleting user: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return None

    async def get_by_uid(self) -> dict:
        try:
            user = User.nodes.get_or_none(uid=self.uid)
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            return await self.get_details(self.uid)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Error getting user by uid: {e}")
            return False

    async def search(self, users: List[str] = [], companies: List[str] = [], softwares: List[str] = [], stacks: List[str] = [], current_user: UserReq = None):
        try:
            if not users and not companies and not softwares and not stacks:
                u_list = User.nodes.all()
                random.shuffle(u_list)
                result = []
                for user in u_list:
                    user_data = await user.full_dict()
                    result.append(user_data)
                return result

            user_scores = defaultdict(float)
            
            def query_and_extend(index_name, word_query, match):
                query = f"""CALL db.index.fulltext.queryNodes("{index_name}", $word_query) YIELD node as n, score as score
                        {match}
                        ORDER BY totalScore DESC"""
                params={'word_query': f"*{word_query}*"}
                with db.session() as session:
                    result = session.run(query, parameters=params)
                    results = [{'node':record['email'], 'score': record['totalScore']} for record in result]
                db.close()
                for result in results:
                    node, score = result.values()
                    user_scores[node] += score
            
            for user in users:
                query = """RETURN n.email as email, score * 1 as totalScore"""
                query_and_extend("user_Index", user, query)

            for company in companies:
                query = """MATCH (u:User)-[:WORKS_FOR]-(n)
                        RETURN u.email as email, score * 0.8 as totalScore"""
                query_and_extend("company_Index", company, query)

            for software in softwares:
                query = """MATCH (u:User)-[:WORKED_ON]-(n)
                        RETURN u.email as email, score * 0.8 as totalScore"""
                query_and_extend("software_Index", software, query)

            for stack in stacks:
                query = """MATCH (u:User)-[:KNOWS]-(n)
                        RETURN u.email as email, score * 0.8 as totalScore"""
                query_and_extend("stack_Index", stack, query)

            sorted_users = sorted(user_scores.items(), key=lambda item: item[1], reverse=True)
            result = []
            for uid, _ in sorted_users:
                user_data = self.get_details(uid)
                if user_data is not None:
                    result.append(user_data)
            return result

        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return False


    def get_user_tagged_posts(self) -> List[dict]:
        try:
            user = User.nodes.get_or_none(uid=self.uid)
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            posts = user.tagged_on_post.all()[:10]
            return json.dumps([{'uid': p.uid, 'created_at':str(p.created_at),'created_by': p.created_by[0].name} for p in posts])
        except Exception as e:
            logger.error(f"Error getting user tagged posts: {e}")
            return None