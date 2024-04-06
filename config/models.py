import os
from typing import List
from settings import PROTOCOL, NEO4J_PASSWORD, NEO4J_USERNAME, NEO4J_HOST, MARKDOWN
from neomodel import (config, StructuredNode, StructuredRel, StringProperty,
                      EmailProperty, BooleanProperty, RelationshipTo, IntegerProperty, RelationshipFrom, UniqueIdProperty, DateTimeProperty)
from config.neo4j_connect import neo4j_driver as db
from config.cache import CACHE, clear_cache
from config.logger import logger 
import inspect
from models.request.schemas import PostReq

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config.DATABASE_URL = f'{PROTOCOL}://{NEO4J_USERNAME}:{NEO4J_PASSWORD}@{NEO4J_HOST}'

def sortingObjects(objList):
            return sorted(objList, key=lambda x: x.strenght, reverse=True)

class PostOpenedRel(StructuredRel):
    has_opened = BooleanProperty(default=False)

class LikeCountRel(StructuredRel):
    like_count = IntegerProperty(default=0)


class User(StructuredNode):
    uid = UniqueIdProperty()
    email = EmailProperty(unique_index=True, required=True)
    name = StringProperty(index=True, required=True)
    preferred_name = StringProperty()
    role = StringProperty(default='')
    joined_at = StringProperty(default='01/01/2023')
    twitter = StringProperty(default='')
    linkedin = StringProperty(default='')
    github = StringProperty(default='')
    picture = StringProperty(default='/assets/img/users/questionFace.jpg')
    bio = StringProperty(index=True, default=MARKDOWN)
    password = StringProperty(default='')
    active = BooleanProperty(default=True)
    is_superuser = BooleanProperty(default=False)
    created_at = DateTimeProperty(default_now=True, immutable=True)
    updated_at = DateTimeProperty(default_now=True)

    # Relationships
    interested_on = RelationshipFrom('Topic', 'Interested_on')
    knows = RelationshipTo('Stack', 'KNOWS')
    works_for = RelationshipTo('Company', 'WORKS_FOR')
    worked_on = RelationshipTo('Software', 'WORKED_ON')
    liked_post = RelationshipTo('Post', 'POST_LIKED_BY') 
    liked_comment = RelationshipTo('Comment', 'COMMENT_LIKED_BY')
    commented_on_post = RelationshipTo('Post', 'COMMENTED_ON_POST')
    commented_on_comment = RelationshipTo('Comment', 'COMMENTED_ON_COMMENT')
    comments = RelationshipFrom('Comment', 'COMMENTS_BY')
    post = RelationshipFrom('Post', 'CREATED_BY')
    tagged_on_post = RelationshipTo('Post', 'POST_TAGGED_USER', model=PostOpenedRel)

    @property
    def strenght(self):
        try:
            strenght = len(self.knows.all()) + \
                len(self.works_for.all()) + \
                len(self.worked_on.all()) + \
                len(self.liked_post.all()) + \
                len(self.liked_comment.all()) + \
                len(self.commented_on_post.all()) + \
                len(self.commented_on_comment.all()) + \
                len(self.comments.all()) + \
                len(self.post.all()) + \
                len(self.tagged_on_post.all())
            return strenght
        except Exception as e:
            logger.error(f"Error getting user strenght: {e}")
            raise e
        
    async def remove_cache(self):
        await clear_cache(f'user_{self.uid}_basic_dict')
        await clear_cache(f'user_{self.uid}_simple_dict')

    async def basic_dict(self):
        try:
            cache_key = f"user_{self.uid}_basic_dict"
            cache_data = await CACHE.get(cache_key)
            if cache_data:
                return cache_data
            else:
                response = {
                    'uid':self.uid,
                    'name':self.name,
                    'picture':self.picture,
                    'created_at':str(self.created_at),
                    'updated_at':str(self.updated_at)
                }
                await CACHE.set(cache_key, response)
                return response
        except Exception as e:
            logger.error(f"Error getting user basic details: {e}")
            return None
        
    async def simple_dict(self):
        try:
            cache_key = f"user_{self.uid}_simple_dict"
            simple_dict = await CACHE.get(cache_key)
            if simple_dict:
                return simple_dict
            companies = get_list_objects(self.works_for.all())
            if inspect.iscoroutine(companies):
                companies = await companies
            company = companies[0] if companies else None
            basic_dict = await self.basic_dict()
            s_dict = {
                "preferred_name": self.preferred_name if self.preferred_name else '',
                "role": self.role if self.role else '',
                "joined_at": self.joined_at if self.joined_at else '',
                "twitter": self.twitter if self.twitter else '',
                "linkedin": self.linkedin if self.linkedin else '',
                "github": self.github if self.github else '',
                "bio": self.bio if self.bio else '',
                "company": company,
                "active": self.active if self.active else '',
                "strenght": self.strenght if self.strenght else 0,

                "is_superuser": self.is_superuser,
                "created_at": str(self.created_at) if self.created_at else '',
                "updated_at": str(self.updated_at) if self.updated_at else ''
            }
            s_dict.update(basic_dict)
            await CACHE.set(cache_key, s_dict)
            return s_dict
        except Exception as e:
            logger.error(f"Error getting user simple details: {e}")
            return None
        
    async def full_dict(self):
        posts = []
        for post in self.tagged_on_post:
            rels = self.tagged_on_post.all_relationships(post)
            for rel in rels:
                if rel.has_opened == False:
                    post_dict = await post.simple_dict()
                    posts.append(post_dict)
                    break
        

        simple_dict = await self.simple_dict()
        try:
            company = self.works_for.single()
            if company:
                company = await company.simple_dict()
            stacks = get_list_objects(self.knows.all())
            if inspect.iscoroutine(stacks):
                stacks = await stacks
            softwares = get_list_objects(self.worked_on.all())
            if inspect.iscoroutine(softwares):
                softwares = await softwares
            full_dict =  {
                "email": self.email if self.email else '',
                "count_notification": len(posts),
                "stacks": stacks,
                "company": company,
                "softwares": softwares,
                "posts": posts,
            }
            full_dict.update(simple_dict)
            return full_dict
        except Exception as e:
            logger.error(f"Error getting user full details: {e}")
            raise e
    

class Location(StructuredNode):
    uid = UniqueIdProperty()
    country = StringProperty()
    city = StringProperty()
    address = StringProperty()

    # Relationships
    company = RelationshipFrom('Company', 'COMPANY_LOCATION')

    def save(self, *args, **kwargs):
        # Replace <br/> with newline in address
        if self.address and '<br/>' in self.address:
            self.address = self.address.replace('<br/>', '  \n')
        super(Location, self).save(*args, **kwargs)

    
    async def remove_cache(self):
        await clear_cache(f'location_{self.uid}_simple_dict')

    async def simple_dict(self):
        try:
            cache_key = f"location_{self.uid}_simple_dict"
            simple_dict = await CACHE.get(cache_key)
            if simple_dict:
                return simple_dict
            
            simple_dict = {
                "uid": self.uid,
                "country": self.country,
                "city": self.city,
                "address": self.address,
            }
            await CACHE.set(cache_key, simple_dict)
            return simple_dict
        except Exception as e:
            logger.error(f"Error getting location simple details: {e}")
            raise e
    
    async def full_dict(self):
        try:
            simple_dict = await self.simple_dict()
            companies = get_list_objects(self.company.all())
            if inspect.iscoroutine(companies):
                companies = await companies
            company = companies[0] if companies else None
            full_dict = {
                "company": company,
            }
            full_dict.update(simple_dict)
            return full_dict
        except Exception as e:
            logger.error(f"Error getting location full details: {e}")
            raise e


class Company(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)
    logo = StringProperty()
    description = StringProperty(index=True)
    created_at = DateTimeProperty(default_now=True, immutable=True)
    updated_at = DateTimeProperty(default_now=True)

    # Relationships
    company_topics = RelationshipFrom('Topic', 'company_topic')
    has_employees = RelationshipFrom('User', 'WORKS_FOR')
    created_software = RelationshipFrom('Software', 'CREATED_BY')
    locations = RelationshipTo('Location', 'COMPANY_LOCATION')
    post = RelationshipTo('Post', 'TAGGED_COMPANY')

    @property
    def strenght(self):
        try:
            strenght =  len(self.has_employees) + \
                        len(self.created_software) + \
                        len(self.locations)
            return strenght
        except Exception as e:
            logger.error(f"Error getting company strenght: {e}")
            raise e
        
    async def remove_cache(self):
        await clear_cache(f'company_{self.uid}_simple_dict')

    async def simple_dict(self):
        try:
            cache_key = f"company_{self.uid}_simple_dict"
            simple_dict = await CACHE.get(cache_key)
            if simple_dict:
                return simple_dict
            simple_dict = {
                "uid": self.uid if self.uid else '',
                "name": self.name if self.name else '',
                "logo": self.logo if self.logo else '',
                "description": self.description if self.description else '',
                "strenght": self.strenght if self.strenght else 0,
                "created_at": str(self.created_at) if self.created_at else '',
                "updated_at": str(self.updated_at) if self.updated_at else '',
            }
            await CACHE.set(cache_key, simple_dict)
            return simple_dict
        except Exception as e:
            logger.error(f"Error getting company simple details: {e}")
            raise e
    
    async def full_dict(self):
        async def getStacks(uid):
            try:
                query = f"""
                        MATCH (s:Stack)<-[:KNOWS]-(u:User)-[:WORKS_FOR]->(c:Company)
                        WHERE c.uid = '{uid}'
                        RETURN DISTINCT s.uid
                        """
                with db.session() as session:
                    result = session.run(query)
                    stacks = []
                    for record in result:
                        st = Stack.nodes.get_or_none(uid=record['s.uid'])
                        if st:
                            s_dict = await st.simple_dict()
                            stacks.append(s_dict)
                    return stacks
            except Exception as e:
                logger.error(f"Error getting stacks: {e}")

        try:
            simple_dict = await self.simple_dict()
            softwares = get_list_objects(self.created_software.all())
            if inspect.iscoroutine(softwares):
                softwares = await softwares
            users = get_list_objects(self.has_employees.all())
            if inspect.iscoroutine(users):
                users = await users
            locations = get_list_objects(self.locations.all())
            if inspect.iscoroutine(locations):
                locations = await locations
            
            stacks = await getStacks(self.uid)
            full_dict = {
                "users": users,
                "strenght": self.strenght or 0,
                "softwares": softwares,
                "stacks": stacks,
                "locations": locations,
            }
            full_dict.update(simple_dict)
            return full_dict
        except Exception as e:
            logger.error(f"Error getting company full details: {e}")
            raise e

    def save(self, *args, **kwargs):
        self.name = self.name.lower() if self.name else None
        self.logo = self.logo.lower() if self.logo else None
        super(Company, self).save(*args, **kwargs)


class Software(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)
    client = StringProperty()
    project_type = StringProperty()
    problem = StringProperty()
    solution = StringProperty()
    comments = StringProperty()
    link = StringProperty()
    image = StringProperty()
    created_at = DateTimeProperty(default_now=True, immutable=True)
    updated_at = DateTimeProperty(default_now=True)
    
    # Relationships
    software_topics = RelationshipFrom('Topic', 'software_topic')
    created_by = RelationshipTo('Company', 'CREATED_BY')
    builded_with = RelationshipTo('Stack', 'BUILDED_WITH')
    worked_on_by = RelationshipFrom('User', 'WORKED_ON')
    post = RelationshipTo('Post', 'TAGGED_SOFTWARE')

    @property
    def strenght(self):
        try:
            strenght = len(self.created_by) + \
                len(self.builded_with) + \
                len(self.worked_on_by)
            return strenght
        except Exception as e:
            logger.error(f"Error getting software strenght: {e}")
            raise e

    def save(self, *args, **kwargs):
        self.name = self.name.lower() if self.name else None
        self.client = self.client.lower() if self.client else None
        self.project_type = self.project_type.lower() if self.project_type else None if self.link else None
        super(Software, self).save(*args, **kwargs)


    async def remove_cache(self):
        await clear_cache(f'software_{self.uid}_simple_dict')

    async def simple_dict(self):
        try:
            cache_key = f"software_{self.uid}_simple_dict"
            simple_dict = await CACHE.get(cache_key)
            if simple_dict:
                return simple_dict
            simple_dict = {
                "uid": self.uid if self.uid else '',
                "name": self.name if self.name else '',
                "client": self.client if self.client else '',
                "project_type": self.project_type if self.project_type else '',
                "problem": self.problem if self.problem else '',
                "solution": self.solution if self.solution else '',
                "comments": self.comments if self.comments else '',
                "link": self.link if self.link else '',
                "image": self.image if self.image else '',
                "created_at": str(self.created_at) if self.created_at else '',
                "updated_at": str(self.updated_at) if self.updated_at else '',
                "strenght": self.strenght if self.strenght else 0,
            }
            await CACHE.set(cache_key, simple_dict)
            return simple_dict
        except Exception as e:
            logger.error(f"Error getting software simple details: {e}")
            raise e
    
    async def full_dict(self):
        try:
            simple_dict = await self.simple_dict()

            company = self.created_by.single()
            company = await company.simple_dict()
            stacks =  get_list_objects(self.builded_with.all())
            if inspect.iscoroutine(stacks):
                stacks = await stacks
            users =  get_list_objects(self.worked_on_by.all())
            if inspect.iscoroutine(users):
                users = await users
            posts =  get_list_objects(self.post.all())
            if inspect.iscoroutine(posts):
                posts = await posts
            
            full_dict = {
                "company": company,
                "stacks": stacks,
                "users": users,
                "posts": posts,                
            }
            full_dict.update(simple_dict)
            return full_dict
        except Exception as e:
            logger.error(f"Error getting software full details: {e}")
            raise e


class Stack(StructuredNode):
    ALLOWED_TYPES = ["devops", "frontend", "backend", "database"]
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)
    description = StringProperty(index=True)
    type = StringProperty()
    image = StringProperty() 
    created_at = DateTimeProperty(default_now=True, immutable=True)
    updated_at = DateTimeProperty(default_now=True)

    # Relationships
    stack_topics = RelationshipFrom('Topic', 'stack_topic')
    known_by = RelationshipFrom('User', 'KNOWS')
    builded_with_software = RelationshipFrom('Software', 'BUILDED_WITH')
    part_of = RelationshipTo('Stack', 'PART_OF')
    inner_stack = RelationshipFrom('Stack', 'PART_OF')
    post = RelationshipTo('Post', 'TAGGED_STACK')

    @property
    def strenght(self):
        try:
            strenght = len(self.known_by) + \
                len(self.builded_with_software) + \
                len(self.part_of) + \
                len(self.post)
            return strenght
        except Exception as e:
            logger.error(f"Error getting stack strenght: {e}")
            raise e


    def save(self, *args, **kwargs):
        self.name = self.name.lower() if self.name else None
        self.type = self.type.lower() if self.type else None
        self.image = self.image if self.image else None

        if self.type not in self.ALLOWED_TYPES:
            raise ValueError(f"Invalid type: {self.type}. Allowed types are: {', '.join(self.ALLOWED_TYPES)}")

        super(Stack, self).save(*args, **kwargs)

    async def remove_cache(self):
        await clear_cache(f'stack_{self.uid}_simple_dict')

    async def simple_dict(self):
        try:
            cache_key = f"stack_{self.uid}_simple_dict"
            simple_dict = await CACHE.get(cache_key)
            if simple_dict:
                return simple_dict
            simple_dict = {
                "uid": self.uid if self.uid else '',
                "name": self.name if self.name else '',
                "description": self.description if self.description else '',
                "type": self.type if self.type else '',
                "image": self.image if self.image else '',
                "created_at": str(self.created_at) if self.created_at else '',
                "updated_at": str(self.updated_at) if self.updated_at else '',
                "strenght": self.strenght if self.strenght else 0,
            }
            await CACHE.set(cache_key, simple_dict)
            return simple_dict
        
        except Exception as e:
            logger.error(f"Error getting stack simple details: {e}")
            raise e
    
    async def full_dict(self):
        async def getCompanies(uid):
            try:
                query = f"""
                        MATCH (s:Stack)<-[:KNOWS]-(u:User)-[:WORKS_FOR]->(c:Company)
                        WHERE s.uid = '{uid}'
                        RETURN DISTINCT c.uid as uid
                        """
                with db.session() as session:
                    result = session.run(query)
                    company_list = [Company.nodes.get_or_none(uid=record['uid']) for record in result if Company.nodes.get_or_none(uid=record['uid']) is not None]
                    companies = []
                    for company in company_list:
                        companies.append(await company.simple_dict())
                    return companies
            except Exception as e:
                logger.error(f"Error getting companies: {e}")
                pass
        
        try:
            simple_dict = await self.simple_dict()
            users = get_list_objects([node for node in self.known_by])
            if inspect.iscoroutine(users):
                users = await users
            softwares = get_list_objects([node for node in self.builded_with_software])
            if inspect.iscoroutine(softwares):
                softwares = await softwares
            companies = getCompanies(self.uid)
            if inspect.iscoroutine(companies):
                companies = await companies
            posts = get_list_objects([node for node in sortingObjects(self.post)])
            if inspect.iscoroutine(posts):
                posts = await posts
            part_of = get_list_objects([node for node in self.part_of])
            if inspect.iscoroutine(part_of):
                part_of = await part_of  
            
            full_dict = {
                "users": users or None,
                "softwares": softwares or None,
                "part_of": part_of or None,
                "posts": posts or None,
                "companies": companies or None,
                "strenght": self.strenght if self.strenght else 0,
            }
            full_dict.update(simple_dict)
            return full_dict
        except Exception as e:
            raise e
        
class Topic(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)

    # Relationships
    posts = RelationshipTo('Post', 'TAGGED_TOPIC')
    users = RelationshipTo('User', 'Interested_on')
    companies = RelationshipTo('Company', 'company_topic')
    stacks = RelationshipTo('Stack', 'stack_topic')
    softwares = RelationshipTo('Software', 'software_topic') 

    @property
    def strenght(self):
        try:
            strenght = len(self.posts) + \
                len(self.users) + \
                len(self.companies) + \
                len(self.stacks) + \
                len(self.softwares)
            return strenght
        except Exception as e:
            raise e

    async def remove_cache(self):
        await clear_cache(f'topic_{self.uid}_simple_dict')

    async def simple_dict(self):
        try:
            cache_key = f"topic_{self.uid}_simple_dict"
            simple_dict = await CACHE.get(cache_key)
            if simple_dict:
                return simple_dict
            simple_dict = {
                "uid": self.uid if self.uid else '',
                "name": self.name if self.name else '',
                "strenght": self.strenght if self.strenght else 0,
            }
            await CACHE.set(cache_key, simple_dict)
            return simple_dict
        except Exception as e:
            raise e
    
    async def full_dict(self):
        posts = get_list_objects([p for p in self.posts]) 
        if inspect.iscoroutine(posts):
            posts = await posts
        users = get_list_objects([u for u in self.users]) 
        if inspect.iscoroutine(users):
            users = await users
        companies = get_list_objects([c for c in sortingObjects(self.companies)])
        if inspect.iscoroutine(companies):
            companies = await companies
        stacks = get_list_objects([s for s in sortingObjects(self.stacks)]) 
        if inspect.iscoroutine(stacks):
            stacks = await stacks
        softwares = get_list_objects([c for c in self.softwares]) 
        if inspect.iscoroutine(softwares):
            softwares = await softwares
                
        try:
            simple_dict = await self.simple_dict()
            full_dict = {
                "posts": posts or None,
                "users": users or None,
                "companies": companies or None,
                "stacks": stacks or None,
                "softwares": softwares or None,
            }
            full_dict.update(simple_dict)
            return full_dict
        except Exception as e:
            raise e

class Post(StructuredNode):
    uid = UniqueIdProperty()
    title = StringProperty()
    text = StringProperty(index=True, required=True)
    image = StringProperty()
    link = StringProperty()
    link_title = StringProperty()
    link_description = StringProperty()
    link_image = StringProperty()
    tags = StringProperty()
    created_at = DateTimeProperty(default_now=True, immutable=True)
    updated_at = DateTimeProperty(default_now=True)


    # Relationships
    topics = RelationshipFrom('Topic', 'TAGGED_TOPIC')
    created_by = RelationshipFrom('User', 'CREATED_BY')
    
    tagged_users = RelationshipFrom('User', 'POST_TAGGED_USER', model=PostOpenedRel)
    tagged_softwares = RelationshipFrom('Software', 'TAGGED_SOFTWARE')
    tagged_stacks = RelationshipFrom('Stack', 'TAGGED_STACK')
    tagged_companies = RelationshipFrom('Company', 'TAGGED_COMPANY')
    
    liked_by = RelationshipTo('User', 'POST_LIKED_BY')

    commented_by = RelationshipTo('User', 'COMMENTED_BY')
    comments = RelationshipFrom('Comment', 'COMMENTS_ON_POST') 
    
    @property
    def comment_count(self):
        return len(self.comments)
    
    @property
    def likes_count(self):
        return len(self.liked_by)
    
    @property
    def strenght(self):
        try:
            strenght = len(self.topics) + \
                len(self.tagged_users) + \
                len(self.tagged_softwares) + \
                len(self.tagged_stacks) + \
                len(self.tagged_companies) + \
                len(self.comments) + \
                len(self.liked_by) + \
                len(self.commented_by)
            return strenght
        except Exception as e:
            raise e


    async def remove_cache(self):
        await clear_cache(f'post_{self.uid}_simple_dict')

    async def simple_dict(self):
        try:
            cache_key = f"post_{self.uid}_simple_dict"
            simple_dict = await CACHE.get(cache_key)
            if simple_dict:
                return simple_dict

            comments = get_list_objects(self.comments.all())
            if inspect.iscoroutine(comments):
                comments = await comments
            if not simple_dict:
                simple_dict =  {
                    "uid": self.uid if self.uid else '',
                    "text": self.text if self.text else '',
                    "image": self.image if self.image else '',
                    "link": self.link if self.link else '',
                    "link_title": self.link_title if self.link_title else '',
                    "link_description": self.link_description if self.link_description else '',
                    "link_image": self.link_image if self.link_image else '',
                    "created_at": str(self.created_at) or '',
                    "updated_at": str(self.updated_at) or '',
                    "comment_count": self.comment_count if self.comment_count else 0,
                    "likes_count": self.likes_count if self.likes_count else 0,
                    "tags": self.tags if self.tags else "",
                    "strenght": self.strenght if self.strenght else 0,
                    "comments": comments,
                }
                created_by =  await self.created_by.single().simple_dict() if self.created_by.single() else None
                simple_dict['created_by'] = created_by
                await CACHE.set(cache_key, simple_dict)
            return simple_dict
        except Exception as e:
            raise e
    
    async def full_dict(self):
        try:
            simple_dict = await self.simple_dict()
            tagged_users =  get_list_objects(self.tagged_users.all())
            tagged_softwares =  get_list_objects(self.tagged_softwares.all())
            tagged_stacks =  get_list_objects(self.tagged_stacks.all())
            tagged_companies =  get_list_objects(self.tagged_companies.all())
            comments = get_list_objects(self.comments.all())
            if inspect.iscoroutine(comments):
                comments = await comments
            simple_dict["comment_count"]= self.comment_count if self.comment_count else 0,
            simple_dict["comments"]= comments or None
            f_dict = {
                "tagged_users": await tagged_users,
                "tagged_softwares": await tagged_softwares,
                "tagged_stacks": await tagged_stacks,
                "tagged_companies": await tagged_companies,
            }
            f_dict.update(simple_dict)
            return f_dict
        except Exception as e:
            raise e
    
class Comment(StructuredNode):
    uid = UniqueIdProperty()
    comment = StringProperty(required=True)
    created_at = DateTimeProperty(default_now=True, immutable=True)
    updated_at = DateTimeProperty(default_now=True)

    # Relationships
    created_by = RelationshipFrom('User', 'COMMENTS_BY')
    c_liked_by = RelationshipTo('User', 'COMMENT_LIKED_BY')
    c_commented_by = RelationshipTo('User', 'COMMENTED_ON_COMMENT')
    c_on_post = RelationshipTo('Post', 'COMMENTS_ON_POST')
    c_on_comment = RelationshipTo('Comment', 'COMMENTS_ON_COMMENT')
    c_comments = RelationshipFrom('Comment', 'COMMENTS_ON_COMMENT')

    @property
    def comment_count(self):
        return len(self.c_comments)
    
    @property
    def likes_count(self):
        return len(self.c_liked_by)

    async def remove_cache(self):
        await clear_cache(f'comment_{self.uid}_simple_dict')

    async def simple_dict(self):
        try:
            cache_key = f"commment_{self.uid}_simple_dict"
            simple_dict = await CACHE.get(cache_key)
            if simple_dict:
                return simple_dict
            simple_dict = {
                "uid": self.uid if self.uid else '',
                "comment": self.comment if self.comment else '',
                "created_by": await self.created_by[0].simple_dict() if self.created_by else None,
                "comment_count": self.comment_count if self.comment_count else 0,
                "likes_count": self.likes_count if self.likes_count else 0,
                "created_at": str(self.created_at) if self.created_at else '',
                "updated_at": str(self.updated_at) if self.updated_at else '',
            }
            await CACHE.set(cache_key, simple_dict)
            return simple_dict
        except Exception as e:
            return None

    async def full_dict(self):
        try:
            comments = get_list_objects([c for c in self.c_comments])
            if inspect.iscoroutine(comments):
                comments = await comments

            simple_dict = await self.simple_dict()
            full_dict = {
                "c_on_post": await self.c_on_post.single().simple_dict() if self.c_on_post.single() else None,
                "c_on_comment": await self.c_on_comment.single().simple_dict() if self.c_on_comment.single() else None,
                "c_on_c_on_post": await self.c_on_comment.single().c_on_post.single().simple_dict() if self.c_on_comment.single() else None,
                "c_comments": comments or None,
            }
            full_dict.update(simple_dict)
            return full_dict
        except Exception as e:
            raise e
        

async def get_list_objects(objects):
    try:
        objs = []
        for obj in objects:
            simple_dict_func = obj.simple_dict

            # Check if simple_dict_func is an asynchronous function
            if inspect.iscoroutinefunction(simple_dict_func):
                simple_dict_result = await simple_dict_func()
            else:
                simple_dict_result = simple_dict_func()

            objs.append(simple_dict_result)

        return objs
    except Exception as e:
        raise e
    
async def clear_all_cache():
    try:
        posts = Post.nodes.all()
        for post in posts:
            await post.remove_cache()
        users = User.nodes.all()
        for user in users:
            await user.remove_cache()
        companies = Company.nodes.all()
        for company in companies:
            await company.remove_cache()
        softwares = Software.nodes.all()
        for software in softwares:
            await software.remove_cache()
        stacks = Stack.nodes.all()
        for stack in stacks:
            await stack.remove_cache()
        topics = Topic.nodes.all()
        for topic in topics:
            await topic.remove_cache()
        locations = Location.nodes.all()
        for location in locations:
            await location.remove_cache()
        comments = Comment.nodes.all()
        for comment in comments:
            await comment.remove_cache()
        other_keys = ['softwares', 'users', 'companies', 'stacks', 'topics', 'locations','post_deeb73a86dd44cb98d634e6f63396aa8_basic_dict']
        for key in other_keys:
            await clear_cache(key)
        return 'Cache cleared successfully'
    except Exception as e:
        logger.error(f"Error clearing all cache: {e}")
        raise e
    



def patchUserConnections(user_node: User, company_uid: str = None, stacks:List[str] = [], softwares:List[str] = []):
        try:
            # Handle user relationships
            if company_uid is not None:
                company = Company.nodes.get_or_none(uid=company_uid.strip())
                if company is None:
                    raise "Company not found"
                user_node.works_for.disconnect_all()
                user_node.works_for.connect(company)

            if stacks is not None and stacks != ['null']:
                user_node.knows.disconnect_all()
                for st in stacks:
                    stack = Stack.nodes.get_or_none(uid=st.strip())
                    if stack is None:
                        raise "Stack not found"
                    user_node.knows.connect(stack)
            if softwares is not None and softwares != ['null']:
                user_node.worked_on.disconnect_all()
                for s in softwares:
                    software = Software.nodes.get_or_none(uid=s.strip())
                    if software is None:
                        raise "Software not found"   
                    user_node.worked_on.connect(software)
                
        except Exception as e:
            logger.error(f"Error patching user connections: {e}")
            pass
