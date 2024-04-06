from collections import defaultdict
from typing import Dict, Any, List
from config.neo4j_connect import neo4j_driver as db
from models.request.schemas import UserReq
from models.request.detailed_schemas import SoftwareDetailed
from config.models import User, Company, Software, Stack
import random
from fastapi import HTTPException
from services import remove_image
import asyncio
from config.cache import CACHE, update_cache
from config.logger import logger 


class SoftwareHandler:
    def __init__(self, 
                uid: str = None,
                name: str = None,
                client: str = None,
                project_type: str = None,
                problem: str = None,
                solution: str = None,
                comments: str =None,
                link: str = None,
                image:  str = None,
                company: str = None,
                stacks: List[str] = None,
                companyUid: str = None,
                contributorUid: str = None,
    ):
        self.uid = uid
        self.name = name.lower() if name else None
        self.client = client
        self.project_type = project_type
        self.problem = problem
        self.solution = solution
        self.comments = comments
        self.link = link
        self.image = image
        self.company = company
        self.stacks = stacks
        self.companyUid = companyUid
        self.contributorUid = contributorUid

        self.payload = {'name': self.name or None, 
                        'client': self.client or None, 
                        'project_type': self.project_type or None, 
                        'problem': self.problem or None, 
                        'solution': self.solution or None, 
                        'comments': self.comments or None, 
                        'link': self.link or None, 
                        'image': self.image or None
                        }

    async def get_details(self, uid: str) -> SoftwareDetailed:
        try:
            software_node = Software.nodes.get(uid=uid)
            if software_node is not None:
                result = await software_node.full_dict()
                return result
        except Exception as e:
            logger.error(f"Error getting software details: {e}")
            return None


    async def insert_obj(self) -> SoftwareDetailed: 
        try:
            # Check if name has been previously registered
            software = Software.nodes.get_or_none(name=self.name)
            if software is not None:
                raise HTTPException(status_code=400, detail="Software already exists")
            data = self.payload
            software_node = Software(**data)
            software_node.save()
            if self.stacks:
                for stackUid in self.stacks:
                    stack = Stack.nodes.get_or_none(uid=stackUid)
                    if stack is None:
                        raise HTTPException(status_code=404, detail="Stack not found")
                    software_node.builded_with.connect(stack)
            if self.companyUid is not None:
                company = Company.nodes.get_or_none(uid=self.companyUid)
                if company is not None:
                    software_node.created_by.connect(company)
            if self.contributorUid is not None:
                user = User.nodes.get_or_none(uid=self.contributorUid)
                if user is not None:
                    user.worked_on.connect(software_node)

            
            response = await self.get_details(software_node.uid)
            if response is None:
                raise HTTPException(status_code=500, detail="Insert software problem encountered")
            
            asyncio.create_task(update_cache('softwares', self.get_all))
            return response
        except HTTPException as e:
            logger.error(f"Error inserting software: {e}")
            if data.image:
                remove_image(path=data.image)
            raise e
        except Exception as e:
            logger.error(f"Error inserting software: {e}")
            if data.image:
                remove_image(path=data.image)   
            return False
        

    async def update_obj(self) -> SoftwareDetailed:
        try:
            software_node = Software.nodes.get_or_none(uid=self.uid)
            if software_node is None:
                raise HTTPException(status_code=404, detail="Software hasn't been found")
            for key, value in self.payload.items():
                if value and hasattr(software_node, key):
                    setattr(software_node, key, value)
                software_node.save()
            if self.stacks:
                for stackUid in self.stacks:
                    stack = Stack.nodes.get_or_none(uid=stackUid)
                    if stack is None:
                        raise HTTPException(status_code=404, detail="Stack not found")
                    software_node.builded_with.connect(stack)
            if self.companyUid:
                company = Company.nodes.get_or_none(uid=self.companyUid)
                if company:
                    software_node.created_by.disconnect_all()
                    software_node.created_by.connect(company)
            response = await self.get_details(self.uid)
            if response is None:
                raise HTTPException(status_code=500, detail="Update software problem encountered")
            
            asyncio.create_task(update_cache('softwares', self.get_all))
            return response
        except HTTPException as e:
            logger.error(f"Error updating software: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error updating software: {e}")
            return False
        
    async def get_all(self) -> List[dict]:
        try:
            cache_key = 'softwares'
            result = await CACHE.get(cache_key)
            if result:
                return result
            softwares = Software.nodes.all()
            if softwares:
                result = []
                for software in softwares:
                    software_dict = await software.full_dict()
                    result.append(software_dict)

                await CACHE.set(cache_key, result)
                return result
            else:
                return False
        except Exception as e:
            logger.error(f"Error getting all softwares: {e}")
            return False


    async def get_by_uid(self) -> SoftwareDetailed:
        try:
            return await self.get_details(self.uid)
        except Exception as e:
            logger.error(f"Error getting software by uid: {e}")
            return False


    def delete_obj(self) -> bool: 
        try:
            # Get the software node
            software_node = Software.nodes.get_or_none(uid=self.uid)
            if software_node is None:
                raise HTTPException(status_code=404, detail="Software hasn't been found")
            image_path = software_node.image
            # Remove all conections
            software_node.created_by.disconnect_all()
            software_node.builded_with.disconnect_all()
            software_node.worked_on_by.disconnect_all()

            # Delete the software node
            software_node.delete()
            if image_path:
                remove_image(path=image_path)

            return True
        except HTTPException as e:
            logger.error(f"Error deleting software: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error deleting software: {e}")
            return False


    async def search(self, users: List[str] = [], companies: List[str] = [], softwares: List[str] = [], stacks: List[str] = []):
        try:
            if not users and not companies and not softwares and not stacks:
                s_list = Software.nodes.all()
                random.shuffle(s_list)
                result = []
                for software in s_list:
                    software_details = await self.get_details(software.uid)
                    if software_details is not None:
                        result.append(software_details)
                return result

            software_scores = defaultdict(float)
            
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
                    software_scores[node] += score

            for software in self.softwares:
                query = """ RETURN n.name as name, score * 1 as totalScore"""
                query_and_extend("software_Index", software, query)

            for stack in self.stacks:
                query = """MATCH (s:Software)-[:BUILDED_WITH]-(n)
                        RETURN s.name as name, score * 0.8 as totalScore"""
                query_and_extend("stack_Index", stack, query)

            for user in self.users:
                query = """MATCH (n)-[:WORKED_ON]-(s:Software)
                        RETURN s.name as name, score * 0.8 as totalScore"""
                query_and_extend("user_Index", user, query)

            for company in self.companies:
                query = """MATCH (s:Software)-[:CREATED_BY]-(n)
                        RETURN s.name as name, score * 0.8 as totalScore"""
                query_and_extend("company_Index", company, query)

            sorted_softwares = sorted(software_scores.items(), key=lambda item: item[1], reverse=True)
            response = []
            for uid, _ in sorted_softwares:
                software_details = await self.get_details(uid)
                if software_details is not None:
                    response.append(software_details)
            if response is None:
                raise HTTPException(status_code=404, detail="No software have been found")
            return response
        except Exception as e:
            logger.error(f"Error searching softwares: {e}")
            return False
        