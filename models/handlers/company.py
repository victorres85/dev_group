from collections import defaultdict
import random
import asyncio
from services import remove_image
from typing import List
from config.neo4j_connect import neo4j_driver as db
from config.logger import logger 

from models.request.schemas import UserReq
from models.request.detailed_schemas import CompanyDetailed
from config.models import Company, Software, User, Location
from fastapi import HTTPException
import asyncio
from config.cache import CACHE, update_cache


class CompanyHandler:
    def __init__(self, 
                uid: str = None, 
                name: str = None, 
                description: str = None, 
                logo: str = None, 
                softwares: List[str] = None, 
                users: List[str] = None, 
                locations: List[str] = None,
                companies: List[str] = None,
                stacks: List[str] = None
    ):
        self.uid = uid
        self.name = name.lower() if name else None
        self.description = description
        self.logo = logo
        self.softwares = softwares
        self.users = users
        self.locations = locations
        self.companies = companies
        self.stacks = stacks


    async def get_details(self, uid) -> CompanyDetailed:
        try: 
            # Get the company node
            company = Company.nodes.get_or_none(uid=uid)
            if company is not None:
                result = await company.full_dict()
                return result
        except Exception as e:
            logger.error(f"Error getting company details: {e}")
            return e


    async def insert_obj(self) -> bool: 
        try:
            # Check if name has been previously registered 
            company = Company.nodes.get_or_none(name=self.name)
            if company is not None:
                raise HTTPException(status_code=400, detail="Company already exists")
            data = {
                "name": self.name,
                "description": self.description,
                "logo": self.logo
            }
            company_node = Company(**data)
            company_node.save()
            if self.softwares:
                for softwareUid in self.softwares:
                    software_node = Software.nodes.get_or_none(uid=softwareUid)
                    if software_node is not None:
                        company_node.created_software.connect(software_node)
                    else:
                        company_node.delete()
                        raise HTTPException(status_code=400, detail=f"Company hasn't been created, software doesn't exist")
            if self.users:
                for userUid in self.users:
                    user_node = User.nodes.get_or_none(uid=userUid)
                    if user_node is not None:
                        user_node.works_for.disconnect_all()
                        user_node.works_for.connect(company_node)
                    else:
                        company_node.delete()
                        raise HTTPException(status_code=400, detail=f"Company hasn't been created, user doesn't exist")
            if self.locations:
                company_node.locations.disconnect_all()
                for location in self.locations:
                    node_location = Location(**location)
                    node_location.save()
                    company_node.locations.connect(node_location)
                    
            result = await self.get_details(company_node.uid)
            if result is None:
                raise HTTPException(status_code=500, detail="Create company problem encountered")
            
            asyncio.create_task(update_cache('companies', self.get_all))
            return result
        except HTTPException as e:
            logger.error(f"Error inserting company: {e}")
            raise e
        except Exception as e: 
            logger.error(f"Error inserting company: {e}")
            raise e
            
    async def update_obj(self) -> dict:
        try:
            # Check if uid has been previously registered 
            company = Company.nodes.get_or_none(uid=self.uid)
            if company is None:
                raise HTTPException(status_code=400, detail=f"Company not Found")
            # Update company details
            if self.name:
                company.name = self.name
            if self.logo:
                company.logo = self.logo
            if self.description:
                company.description = self.description
            company.save()
            company.created_software.disconnect_all()
            if self.softwares:
                for softwareUid in self.softwares:
                    software_node = Software.nodes.get_or_none(uid=softwareUid)
                    if software_node:
                        company.created_software.connect(software_node)
                    else:
                        raise HTTPException(status_code=400, detail=f"Company hasn't been updated, {software_node.name} doesn't exist")
            company.has_employees.disconnect_all()
            if self.users:
                for usersUid in self.users:
                    user_node = User.nodes.get_or_none(uid=usersUid)
                    if user_node:
                        user_node.works_for.disconnect_all()
                        user_node.works_for.connect(company)
                    else:
                        raise HTTPException(status_code=400, detail=f"Company hasn't been updated, {user_node.name} doesn't exist")
            company.locations.disconnect_all()
            if self.locations:
                for l in self.locations: 
                    location = Location.nodes.get_or_none(address=l['address'])
                    if location is None:
                        location = Location(**l)
                        location.save()
                    company.locations.connect(location)
            
            asyncio.create_task(update_cache('companies', self.get_all))

            return await self.get_details(self.uid)
        except HTTPException as e:
            logger.error(f"Error updating company: {e}")
            return e
        except Exception as e: 
            logger.error(f"Error updating company: {e}")
            return False


    async def get_all(self) -> List:
        try:
            cache_key = 'companies'
            result = await CACHE.get(cache_key)
            if result:
                return result
            companies = Company.nodes.all()
            sorted_companies = sorted(companies, key=lambda company: company.strenght)
            result = []
            for company in sorted_companies:
                company = await company.full_dict()
                result.append(company)

            await CACHE.set(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Error getting all companies: {e}")
            return str(e)


    async def get_by_uid(self) -> CompanyDetailed:
        try:
            return await self.get_details(self.uid)
        except Exception as e:
            logger.error(f"Error getting company by uid: {e}")
            return None

    def delete_obj(self) -> bool: 
        try:
            # Get the company node
            company = Company.nodes.get_or_none(uid=self.uid)
            if company is None:
                raise HTTPException(status_code=404, detail="Company doesn't exist")
            logo_path = company.logo
            # Remove all related nodes
            company.has_employees.disconnect_all()
            company.created_software.disconnect_all()

            # Delete the company node
            company.delete()

            # Remove the logo file from the system
            if logo_path:
                remove_image(path=logo_path)

            return True
        except HTTPException as e:
            logger.error(f"Error deleting company: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error deleting company: {e}")
            return False

    async def search(self):
        try:
            if not self.users and not self.companies and not self.softwares and not self.stacks:
                c_list = Company.nodes.all()
                random.shuffle(c_list)
                result = []
                for company in c_list:
                    company = await company.full_dict()
                    result.append(company)
                return result
            
            company_scores = defaultdict(float)
            
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
                    company_scores[node] += score

            for company in self.companies:
                query = """RETURN n.name as name, score * 1 as totalScore"""
                query_and_extend("company_Index", company, query)

            for user in self.users:
                query = """MATCH (n)-[:WORKS_FOR]-(c:Company)
                        RETURN c.name as name, score * 0.8 as totalScore"""
                query_and_extend("user_Index", user, query)

            for software in self.softwares:
                query = """MATCH (n)-[:CREATED_BY]-(c:Company)
                        RETURN c.name as name, score * 0.8 as totalScore"""
                query_and_extend("software_Index", software, query)

            for stack in self.stacks:
                query = """
                MATCH (n)<-[:KNOWS]-(u:User)-[:WORKS_FOR]->(c:Company)
                RETURN c.uid as c.uid as uid, score * 0.6 as totalScore
                """
                query_and_extend("stack_Index", stack, query)


            sorted_companies = sorted(company_scores.items(), key=lambda item: item[1], reverse=True)
            response = []
            for uid, _ in sorted_companies:
                company = await self.get_details(uid)
                if company:
                    response.append(company)
            if response:
                return response
            raise HTTPException(status_code=404, detail="No company have been found")
        except Exception as e:
            logger.error(f"Error searching companies: {e}")
            raise e
    

    def get_company_stacks(self) -> dict:
        try:
            query = """
            MATCH (st:Stack)<-[:KNOWS]-(u:User)-[:WORKS_FOR]->(c:Company {uid: $company_uid})
            RETURN st.uid as uid, st.name as name, st.description as description, st.type as type
            """
            with db.session() as session:
                result = session.run(query, company_uid=self.uid)
                stack_list = [{'uid':record['uid'], 'name':record['name'], 'description':record['description'], 'type':record['type']} for record in result]
            db.close()
        
            return stack_list
        except Exception as e:
            logger.error(f"Error getting company stacks: {e}")
            return False