from collections import defaultdict
import random
from fastapi import HTTPException
from typing import List
from config.neo4j_connect import neo4j_driver as db
from models.request.detailed_schemas import StackDetailed
from config.models import Stack
from services import remove_image
import asyncio
from config.cache import update_cache, CACHE
from config.logger import logger 

class StackHandler:
    def __init__(self, 
                uid: str = None,
                name: str = None,   
                description: str = None,
                type: str = None,
                image: str = None,
                part_of: str = None,
    ):
        self.uid = uid
        self.name = name.lower() if name else None
        self.description = description
        self.type = type
        self.image = image
        self.part_of = part_of

        self.payload = {'name': self.name or None, 
                        'description': self.description or None, 
                        'type': self.type or None, 
                        'image': self.image or None, 
                        }

    async def get_details(self, uid: str) -> StackDetailed: 
        try:    
            # Find the stack by name   
            stack = Stack.nodes.get_or_none(uid=uid)
            if stack is not None:
                return await stack.full_dict()
        except Exception as e:
            return None


    async def insert_obj(self) -> bool: 
        try:
            stack_node = Stack.nodes.get_or_none(name=self.name)
            if stack_node is not None:
                raise HTTPException(status_code=400, detail="Stack already exists")
            stack = Stack(**self.payload)
            stack.save()
            
            if self.part_of:
                part_of_stack = Stack.nodes.get_or_none(name=self.part_of)
                if part_of_stack is None:
                    raise HTTPException(status_code=404, detail="Parent stack hasn't been found")
                stack.part_of.connect(part_of_stack)

            response = await self.get_details(stack.uid)
            if response is None:
                raise HTTPException(status_code=500, detail="Insert stack problem encountered")
            
            asyncio.create_task(update_cache('stacks', self.get_all))
            return response
        except HTTPException as e:
            logger.error(f"Error inserting stack: {e}")
            raise e
        except Exception as e: 
            logger.error(f"Error inserting stack: {e}")
            return False
            
    async def update_obj(self) -> bool:
        try:
            stack_node = Stack.nodes.get_or_none(uid=self.uid)
            if stack_node is None:
                raise HTTPException(status_code=404, detail="Stack hasn't been found")
            
            if self.part_of:
                part_of_stack = Stack.node.get_or_none(name=self.part_of.strip())
                if part_of_stack is None:
                    raise HTTPException(status_code=404, detail="Parent stack hasn't been found")
                stack_node.part_of.disconnect_all()
                stack_node.part_of.connect(part_of_stack)

            if self.description:
                stack_node.description = self.description
            if self.stack_type:
                stack_node.type = self.stack_type
            if self.image:
                stack_node.image = self.image
            stack_node.save()
            response = await self.get_details(self.uid)
            if response is None:
                raise HTTPException(status_code=500, detail="Update stack problem encountered")
            
            asyncio.create_task(update_cache('stacks', self.get_all))

            return response
        except HTTPException as e:
            logger.error(f"Error updating stack: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error updating stack: {e}")
            return False
        
    async def get_all(self) -> List[dict]:
        try:
            cache_key = 'stacks'
            result = await CACHE.get(cache_key)
            if result:
                return result
            stacks = Stack.nodes.all()
            sorted_stacks = sorted(stacks, key=lambda stack: stack.strenght, reverse=True)
            result = []
            for stack in sorted_stacks:
                stack_details = await self.get_details(stack.uid)
                if stack_details is not None:
                    result.append(stack_details)

            await CACHE.set(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Error getting all stacks: {e}")
            return False


    async def get_by_uid(self) -> dict:
        try:   
            return await self.get_details(self.uid)
        except Exception as e:
            logger.error(f"Error getting stack by uid: {e}")
            return False

    def delete_obj(self) -> bool: 
        try:
            stack = Stack.nodes.get_or_none(uid=self.uid)
            if stack is None:
                raise HTTPException(status_code=404, detail="Stack not found")
            image_path = stack.image
            # Remove all connections
            stack.known_by.disconnect_all()
            stack.builded_with_software.disconnect_all()
            stack.part_of.disconnect_all()
            
            # Delete the stack
            stack.delete()
            if image_path:
                remove_image(path=image_path)

            return True
        except HTTPException as e:
            logger.error(f"Error deleting stack: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error deleting stack: {e}")
            return False

    async def search(self, stacks: List[str] = [], softwares: List[str] = [], users: List[str] = [], companies: List[str] = []):
        try:
            if not users and not companies and not softwares and not stacks:
                s_list = Stack.nodes.all()
                random.shuffle(s_list)
                result = []
                for stack in s_list:
                    stack_details = await self.get_details(stack.uid)
                    if stack_details is not None:
                        result.append(stack_details)
                return result
            
            stack_scores = defaultdict(float)
            
            def query_and_extend(index_name, word_query, match):
                query = f"""CALL db.index.fulltext.queryNodes("{index_name}", $word_query) YIELD node as n, score as score
                        {match}
                        ORDER BY totalScore DESC"""
                params={'word_query': word_query}
                with db.session() as session:
                    result = session.run(query, parameters=params)
                    results = [{'node':record['name'], 'score': record['totalScore']} for record in result]
                db.close()
                for result in results:
                    node, score = result.values()
                    stack_scores[node] += score

            for stack in stacks:
                query = """RETURN n.name as name, score * 1 as totalScore"""
                query_and_extend("stack_Index", stack, query)

            for user in users:
                query = """MATCH (n)-[:KNOWS]-(st:Stack)
                        RETURN st.name as name, score * 0.8 as totalScore"""
                query_and_extend("user_Index", user, query)

            for software in softwares:
                query = """MATCH (n)-[:BUILDED_WITH]-(st:Stack)
                        RETURN st.name as name, score * 0.8 as totalScore"""
                query_and_extend("software_Index", software, query)

            for company in companies:
                query = """MATCH (s)-[:CREATED_BY]-(n)
                        MATCH (s:Software)-[:BUILDED_WITH]-(st:Stack)
                        RETURN st.name as name, score * 0.6 as totalScore"""
                query_and_extend("company_Index", company, query)

            sorted_stacks = sorted(stack_scores.items(), key=lambda item: item[1])
            response = []
            for name, _ in sorted_stacks:
                stack_details = await self.get_details(name)
                if stack_details is not None:
                    response.append(stack_details)
            if response is None:
                raise HTTPException(status_code=404, detail="No stack have been found")
            return response
        except Exception as e:
            logger.error(f"Error searching stacks: {e}")
            return False
        