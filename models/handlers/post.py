import datetime
import json
from fastapi import HTTPException
from typing import List, Optional
from config.neo4j_connect import neo4j_driver as db
from models.request.schemas import  UserReq, GetPostReq
from models.request.detailed_schemas import PostDetailed
from config.models import Post, User, Company, Software, Stack
import asyncio
import boto3
from concurrent import futures
from config.cache import CACHE
import inspect

from config.logger import logger 
import datetime
import json
from fastapi import HTTPException
from typing import List, Optional
from config.neo4j_connect import neo4j_driver as db
from models.request.schemas import  UserReq
from models.request.detailed_schemas import PostDetailed
from config.models import Post, User, Company, Software, Stack
import asyncio
import boto3
from concurrent import futures
from config.cache import CACHE

class PostHandler:
    def __init__(self, 
                 uid: Optional[str] = None,
                 userUid: Optional[str] = None,
                 image: Optional[str] = None,
                 link: Optional[str] = None,
                 link_title: Optional[str] = None,
                 link_description: Optional[str] = None,
                 link_image: Optional[str] = None,
                 tagged_users: Optional[str] = None,
                 text: Optional[str] = None,
                 skip: Optional[str] = '0',
                 limit: Optional[str] = '10',) -> None:
        self.uid = uid
        self.userUid = userUid
        self.image = image
        self.link = link
        self.link_title = link_title
        self.link_description = link_description
        self.link_image = link_image
        self.tagged_users = tagged_users
        self.text = text
        self.skip = int(skip)
        self.limit = int(limit)


    async def get_posts(self) -> List[dict]:
        """
        # Get Posts

        This function retrieves a list of posts from the database. The posts are ordered by their update time in descending order. 
        Pagination is supported through the `skip` and `limit` parameters.

        # Parameters:
        - **skip:** (int) The number of posts to skip. This is used for pagination.
        - **limit:** (int) The maximum number of posts to return. This is used for pagination.

        # Returns:
        - A list of `PostDetailed` objects representing the posts. Each `PostDetailed` object contains detailed information about a post.

        # Errors:
        - If an error occurs during the retrieval of the posts, the function will return `False`.

        # Usage:
        This function can be used to retrieve a list of posts for display on a webpage or for processing in other functions.

        ```
        python
        posts = get_posts(skip=0, limit=10)
        for post in posts:
            print(post.text)
        ```
        """
        try:
            posts = Post.nodes.order_by('-updated_at')[self.skip:self.limit]
            result = []
            for post in posts:
                post_node = Post.nodes.get_or_none(uid=post.uid)
                if post_node:
                    result.append(await post_node.full_dict())

            return result
        except Exception as e:
            logger.error(f"Error getting posts: {e}")
            return False

    def cache_key_builder(self):
        return f"posts:{self.skip}:{self.limit}"


    def like_post(self, like: bool = True) -> bool:
        try:
            post = Post.nodes.get_or_none(uid=self.uid)
            if post is None:
                raise HTTPException(status_code=404, detail="Post not found")
            user = User.nodes.get_or_none(uid=self.userUid)
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            if like:
                post.liked_by.connect(user)
            else:
                post.liked_by.disconnect(user)
            return True
        except HTTPException as e:
            logger.error(f"Error liking post: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error liking post: {e}")
            return False
        
    def get_by_uid(self) -> PostDetailed:
        post = Post.nodes.get_or_none(uid=self.uid)
        user = User.nodes.get_or_none(uid=self.userUid)
        rels = user.tagged_on_post.all_relationships(post)
        for rel in rels:
            if rel.has_opened == False:
                rel.has_opened = True 
                rel.save()
        try:   
            return self.get_details(post.uid)
        except Exception as e:
            logger.error(f"Error getting post by uid: {e}")
            return False

    async def delete_obj(self) -> bool: 
        try:
            
            post = Post.nodes.get_or_none(uid=self.uid)
            if post is None:
                raise HTTPException(status_code=404, detail="Post not found")
            image_path = post.image
        
            post.created_by.disconnect_all()
            post.tagged_users.disconnect_all()
            post.tagged_softwares.disconnect_all()
            post.tagged_companies.disconnect_all()
            post.tagged_stacks.disconnect_all()
            post.liked_by.disconnect_all()
            post.commented_by.disconnect_all()
            post.comments.disconnect_all()

            cache_key = f"post_{self.uid}_simple_dict"
            await CACHE.delete(cache_key)
            
            # Delete the stack
            post.delete()

            return True
        except HTTPException as e:
            logger.error(f"Error deleting post: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error deleting post: {e}")
            return False

    async def patchPostConnections(self, post_node: Post):
        try:
            
            if post_node:
                lowerTxt = self.text.lower() if self.text else ''
                lowerLinkDescription = self.link_description.lower() if self.link_description else ''
                combinedTxt = lowerTxt + ' ' + lowerLinkDescription
                
                if combinedTxt:
                    tagged_stacks = []
                    for stack in Stack.nodes.all():
                        if stack.name.lower() in combinedTxt:
                            tagged_stacks.append(stack.uid)
                    
                    tagged_softwares = []
                    for software in Software.nodes.all():
                        if software.name.lower() in combinedTxt:
                            tagged_softwares.append(software.uid)

                    tagged_companies = []
                    for company in Company.nodes.all():
                        if company.name.lower() in combinedTxt:
                            tagged_companies.append(company.uid)        

                if self.tagged_users:
                    post_node.tagged_users.disconnect_all()
                    if 'all' in self.tagged_users:
                        self.tagged_users = [u.uid for u in User.nodes.all()]
                    for userUid in self.tagged_users:
                        user_node = User.nodes.get_or_none(uid=userUid)
                        if user_node:
                            post_node.tagged_users.connect(user_node)
                        
                if tagged_softwares:
                    post_node.tagged_softwares.disconnect_all()
                    for softwareUid in tagged_softwares:
                        software_node = Software.nodes.get_or_none(uid=softwareUid)
                        if software_node:
                            post_node.tagged_softwares.connect(software_node)

                if tagged_companies:
                    post_node.tagged_companies.disconnect_all()
                    for companyUid in tagged_companies:
                        company_node = Company.nodes.get_or_none(uid=companyUid)
                        if company_node:
                            post_node.tagged_companies.connect(company_node)

                if tagged_stacks:
                    post_node.tagged_stacks.disconnect_all()
                    for stackUid in tagged_stacks:
                        stack_node = Stack.nodes.get_or_none(uid=stackUid)
                        if stack_node:
                            post_node.tagged_stacks.connect(stack_node)

                
                result = await self.get_details(post_node.uid)
            else:
                raise HTTPException(status_code=404, detail="Post not found")

        except Exception as e:
            logger.error(f"Error patching post connections: {e}")
            pass


    async def notify_users(tagged_users: List[str], post_obj: PostDetailed):
        appsync = boto3.client('appsync', region_name='eu-west-1')
        try:
            for user_id in tagged_users:
                user = User.nodes.get_or_none(uid=user_id)
                stacks = json.dumps([s.name for s in post_obj.tagged_stacks])
                softwares = json.dumps([s.name for s in post_obj.tagged_softwares])
                companies = json.dumps([s.name for s in post_obj.tagged_companies])
                if user:
                    # Send a createNotification mutation to the AppSync API
                    mutation = """
                    mutation CreateNotification($userId: ID!, $postId: ID!) {
                    createNotification(userId: $userId, postId: $postId, stacks: $stacks, softwares: $softwares, companies: $companies) {
                        userId
                        postId
                        stacks
                        softwares
                        companies
                    }
                    }
                    """
                    variables = {
                        'userId': user_id,
                        'postId': post_obj.uid,
                        'stacks': stacks,
                        'softwares': softwares,
                        'companies': companies,
                    }
                    response = appsync.graphql(
                        apiId='ylv6q4oyxbfktjhq5w5ouh2mv4', 
                        operationName='CreateNotification',
                        query=mutation,
                        variables=variables,
                    )
                    print(f"Notification created for user {user_id}: {response}")
        except Exception as e:
            logger.error(f"Error notifying users: {e}")
            pass

    async def search(self, users: str = [], queries: str = [], current_user: UserReq = None):
        try:
            if not users and not queries:
                raise HTTPException(status_code=404, detail="No search criteria has been sent.")
            
            scores = []

            def run_queries(tx, query, params):
                result = tx.run(query, params)
                return [record for record in result]
            
            def convert_date(timestamp):
                return datetime.datetime.fromtimestamp(timestamp)

            post_query = """
                CALL db.index.fulltext.queryNodes("post_Index", $word_query) YIELD node as n, score as sPost
                WITH n, sPost, datetime().epochSeconds - n.created_at AS seconds_diff
                RETURN n, sPost - floor(seconds_diff / (3 * 24 * 60 * 60)) * 0.3 AS score
                """
            post_params = {'word_query': queries}

            user_query = """
                CALL db.index.fulltext.queryNodes("user_Index"
                    , $users) YIELD node as u, score as sUser
                MATCH (n:Post)-[:CREATED_BY]-(u)
                WITH n, sUser, datetime().epochSeconds - n.created_at AS seconds_diff
                RETURN n, sUser - floor(seconds_diff / (3 * 24 * 60 * 60)) * 0.3 AS score
                """
            
            user_params = {'users': users}

            with db.session() as session:
                with futures.ThreadPoolExecutor(max_workers=2) as executor:
                    results = []
                    if queries:
                        results.append(executor.submit(session.execute_read, run_queries, post_query, post_params))
                    if users:
                        results.append(executor.submit(session.execute_read, run_queries, user_query, user_params))
                    for r in futures.as_completed(results):
                        scores.extend(r.result())

            records = []

            # Iterate over the list
            for record in scores:
                uid = record.get('n').get('uid')
                existing_record = next((r for r in records if r['uid'] == uid), None)
                
                if existing_record:
                    existing_record['score'] += record['score']
                else:
                    records.append({'uid': uid, 'score': record['score'], 'node': record['n']})

            sorted_posts = sorted(records, key=lambda item: item['score'])
         
            response = []
            for pair in sorted_posts[:10]:
                post = Post.nodes.get_or_none(uid=pair['uid'])
                if post:
                    response.append(await post.full_dict())

            if len(response) == 0:
                raise HTTPException(status_code=404, detail="No post have been found")
            return response
        except Exception as e:
            logger.error(f"Error searching posts: {e}")
            return False
        
    async def insert_post(self) -> bool: 
        try:
            post_node = Post(text=self.text, link=self.link, image=self.image, link_title=self.link_title, link_description=self.link_description, link_image=self.link_image)
            post_node.save()    

            if self.userUid:
                user_node = User.nodes.get_or_none(uid=self.userUid)
                if user_node:
                    post_node.created_by.connect(user_node)   

            await self.patchPostConnections(post_node)

            response = await self.get_details(post_node.uid)

            if response is None:
                raise HTTPException(status_code=500, detail="Insert stack problem encountered")
            return response
        except HTTPException as e:
            logger.error(f"Error inserting post: {e}")
            raise e
        except Exception as e: 
            logger.error(f"Error inserting post: {e}")
            return False
            
    async def update_obj(self) -> bool: 
        try:
            post_node = Post.nodes.get_or_none(uid=self.uid)
            if post_node is None:
                raise HTTPException(status_code=404, detail="Post not found")
            post_node.text = self.text
            post_node.image = self.image
            post_node.link = self.link
            post_node.link_title = self.link_title
            post_node.link_description = self.link_description
            post_node.link_image = self.link_image
            post_node.save()
            CACHE.delete(f"post_{self.uid}_simple_dict")

            asyncio.create_task(self.patchPostConnections(post_node))

            response = await self.get_details(post_node.uid)
            if response is None:
                raise HTTPException(status_code=500, detail="Insert stack problem encountered")

            return response
        except HTTPException as e:
            raise e
        except Exception as e: 
            return False
        
    async def get_details(self, uid) -> dict: 
        try:    
            post = Post.nodes.get_or_none(uid=uid)
            if post is not None:
                return await post.full_dict()
        except Exception as e:
            return None
        
    
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
    
