# import unittest
# from main import app
# from fastapi import HTTPException
# from api.login import create_new_user, valid_email_from_db
# from models.request.schemas import UserCreate
# from unittest.mock import patch
# from fastapi.testclient import TestClient
# from services import send_email_verification
# from config.neo4j_connect import neo4j_driver as db 
# from config.models import User, Software, Stack, Post, Comment, Company, Location
# import pytest

# test_user = UserCreate(email="test@company01.com", password="testpassword")

# client = TestClient(app)


# class FastAPITest(unittest.TestCase):
#     def setUp(self):
#         self.client = TestClient(app)

# @pytest.fixture
# def software_instance():
#     payload = {'name': 'test software', 'client': 'test client', 'project_type': 'test project', 'problem': 'test problem.', 'solution': 'test solution.', 'comments': 'test comments.', 'link': 'https://nitrogen.un.company01dev.com/', 'image': '/assets/img/softwares/screenshot_2024-01-14_at_18.jpg'}
#     Software(**payload)

# @pytest.fixture
# def stack_instance():
#     payload = {'name': 'test stack', 'description': 'test stack description', 'type': 'devops', 'image': 'https://code.benco.io/icon-collection/azure-docs/logo_terraform.svg'}
#     return Stack(**payload)

# @pytest.fixture
# def post_instance():
#     payload = {'text': 'test text tagging test user, test software, test stack', 'image': None, 'link': None, 'link_title': None, 'link_description': None, 'link_image': None, 'tags': None}
#     return Post(**payload)

# @pytest.fixture()
# def comment_instance():
#     payload = { 'comment': 'test comment on test post'}
#     return Comment(**payload)

# @pytest.fixture()
# def user_instance():
#     payload = {'email': 'test.email@company01.com', 'name': 'test user', 'preferred_name': None, 'role': 'junior developer', 'joined_at': '21/02/2023', 'twitter': 'www.xman2.com', 'linkedin': 'www.linkedin2.com', 'github': 'www.github2.com', 'picture': 'https://teamnet-company01.s3.eu-west-2.amazonaws.com/assets/img/users/victor_almeida2356.jpg', 'bio': 'test bio', 'password': '$2b$12$TyL4DxJEXgSij8VzBXRHPOI6Zb864cMUOteqCR5R0IzbmQYe1k3Dq', 'active': True, 'is_superuser': True}
#     return User(**payload)

# @pytest.fixture()
# def company_instance():
#     payload = {'name': 'test company name', 'description': 'test description', 'image': 'https://teamnet-company01.s3.eu-west-2.amazonaws.com/assets/img/companies/company01_logo.png'}
#     return Company(**payload)

# @pytest.fixture()
# def location_instance():
#     payload = {'country': 'test country', 'city': 'test city', 'address': 'test address'}
#     return Location(**payload)

# # @pytest.mark.usefixtures("software_instance")
# def test_save_method_modifies_attributes(software_instance):
#     # Test the save method modifications on specific attributes
#     software_instance.save()
#     assert software_instance.name == "test software"
#     assert software_instance.client == "test client"
#     assert software_instance.project_type == "test project"
#     assert software_instance.problem == "test problem."
#     assert software_instance.solution == "test solution."
#     assert software_instance.comments == "test comments."
#     assert software_instance.link == "https://nitrogen.un.company01dev.com/"
#     assert software_instance.image == "/assets/img/softwares/screenshot_2024-01-14_at_18.jpg"
    
# def save_instances(location_instance, company_instance, software_instance, stack_instance, user_instance, post_instance, comment_instance):
#     company_instance.save()
#     software_instance.save()
#     stack_instance.save()
#     user_instance.save()
#     post_instance.save()
#     comment_instance.save()
#     location_instance.save()

# def test_create_relationships_method(location_instance, company_instance, software_instance, stack_instance, user_instance, post_instance, comment_instance):
#     # Test the create_relationships method
#     save_instances(location_instance, company_instance, software_instance, stack_instance, user_instance, post_instance, comment_instance)
#     post_instance.tagged_users.connect(user_instance)
#     post_instance.tagged_softwares.connect(software_instance)
#     post_instance.tagged_stacks.connect(stack_instance)
#     user_instance.knows.connect(stack_instance)
#     user_instance.works_for.connect(company_instance)
#     user_instance.worked_on.connect(software_instance)
#     user_instance.commented_on.connect(post_instance)
#     location_instance.company.connect(company_instance)
#     company_instance.created_software.connect(software_instance)
#     software_instance.builded_with.connect(stack_instance)
    
#     assert post_instance.tagged_users.all() == [user_instance]
#     assert post_instance.tagged_softwares.all() == [software_instance]
#     assert post_instance.tagged_stacks.all() == [stack_instance]
#     assert user_instance.knows.all() == [stack_instance]
#     assert user_instance.works_for.all() == [company_instance]
#     assert user_instance.worked_on.all() == [software_instance]
#     assert user_instance.commented_on.all() == [post_instance]
#     assert location_instance.company.all() == [company_instance]
#     assert company_instance.created_software.all() == [software_instance]
#     assert software_instance.builded_with.all() == [stack_instance]

# def test_simple_dict_software_instance(software_instance):
#     expected_result = {'name': 'test software', 
#                         'client': 'test client', 
#                         'project_type': 'test project', 
#                         'problem': 'test problem.', 
#                         'solution': 'test solution.', 
#                         'comments': 'test comments.', 
#                         'link': 'https://nitrogen.un.company01dev.com/', 
#                         'image': '/assets/img/softwares/screenshot_2024-01-14_at_18.jpg', 
#                         'strenght':3
#                     }
#     assert software_instance.simple_dict() == expected_result

# # Add more tests for other methods as needed

# # Mocking example for async methods
# # @pytest.mark.asyncio
# # async def test_full_dict_method_async(software_instance, mocker):
# #     # Mocking get_list_objects to return a list instead of coroutine
# #     mocker.patch('your_module.get_list_objects', return_value=['item1', 'item2'])

# #     # Mocking inspect.iscoroutine to return False
# #     mocker.patch('your_module.inspect.iscoroutine', return_value=False)

# #     result = await software_instance.full_dict()
# #     expected_result = {
# #         "company": {},
# #         "stacks": ['item1', 'item2'],
# #         "users": ['item1', 'item2'],
# #         "posts": ['item1', 'item2'],
# #         "uid": "",
# #         "name": "Test Software",
# #         "client": "Test Client",
# #         "project_type": "Test Project",
# #         "problem": "",
# #         "solution": "",
# #         "comments": "",
# #         "link": "",
# #         "image": "",
# #         "created_at": "",
# #         "updated_at": "",
# #         "strenght": 0,
# #     }
# #     assert result == expected_result
