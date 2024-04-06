# from fastapi.testclient import TestClient
# from models.handlers.software import SoftwareHandler
# from models.request.schemas import CompanyReq, SoftwareReq, StackReq
# from main import app  
# import pytest
# from config.models import User, Company, Software, Stack
# from models.request.detailed_schemas import UserDetailed
# from security.secure import get_current_user, get_password_hash, is_superuser
# from services import generate_password
# from models.handlers.user import get_details
# import neomodel
# from fastapi import status, HTTPException

# client = TestClient(app)

# @pytest.fixture
# def app():
#     from main import app as _app
#     return _app

# @pytest.fixture(scope="class")
# def database_objects():
#     password = generate_password()
#     hashed_password = get_password_hash(password)
#     # Creating objects in the database

#     test_stack1 = Stack(name='stack1', description= 'stack1 stack_description1').save()
#     test_stack1_1 = Stack(name='stack1_1', description= 'stack1_1 stack_description1_1').save()
#     test_stack1_2 = Stack(name='stack1_2', description= 'stack1_2 stack_description1_2').save()
#     test_stack1_3 = Stack(name='stack1_3', description= 'stack1_3 stack_description1_3').save()
#     test_stack2 = Stack(name='stack2', description= 'stack2 stack_description2').save()
#     test_stack2_1 = Stack(name='stack2_1', description= 'stack2_1 stack_description2_1').save()
#     test_stack2_2 = Stack(name='stack2_2', description= 'stack2_2 stack_description2_2').save()
#     test_stack2_3 = Stack(name='stack2_3', description= 'stack2_3 stack_description2_3').save()
#     test_stack3 = Stack(name='stack3', description= 'stack3 stack_description3').save()
#     test_software1 =Software(name='software1', description= 'software1 software_description1').save()
#     test_software2 = Software(name='software2', description= 'software2 software_description2').save()
#     test_software3= Software(name='software3', description= 'software3 software_description3').save()
#     test_user1 =User(email='user1@test.com', password=get_password_hash('1234'), is_superuser=True).save()
#     test_user2=User(email='user2@test.com', password=hashed_password).save()
#     test_user3=User(email='user3@test.com', password=hashed_password).save()
#     test_user4=User(email='user4@test.com', password=hashed_password).save()
#     test_company1= Company(name='company1', description='company1 company_description1').save()
#     test_company2= Company(name='company2', description='company2 company_description2').save()
    
#     # objects to test delete functionalities
#     test_company3= Company(name='company3', description='company3 company_description2').save()
#     test_stack4 = Stack(name='stack4', description= 'stack4 stack_description3').save()

#     # Creating relationships for users
#     test_user1.works_for.connect(test_company1)
#     test_user1.worked_on.connect(test_software1)
#     test_user1.knows.connect(test_stack1)
#     test_user1.knows.connect(test_stack1_1)
#     test_user1.knows.connect(test_stack1_2)
#     test_user1.knows.connect(test_stack1_3)
#     test_user2.works_for.connect(test_company1)
#     test_user2.worked_on.connect(test_software2)
#     test_user2.knows.connect(test_stack2)
#     test_user2.knows.connect(test_stack2_1)
#     test_user2.knows.connect(test_stack2_2)
#     test_user2.knows.connect(test_stack2_3)
#     test_user3.works_for.connect(test_company2)
#     test_user3.worked_on.connect(test_software3)
#     test_user3.knows.connect(test_stack3)
#     test_user3.knows.connect(test_stack1)
#     test_user3.knows.connect(test_stack2)

#     # Creating relationships for stacks
#     test_stack1_1.part_of.connect(test_stack1)
#     test_stack1_2.part_of.connect(test_stack1)
#     test_stack1_3.part_of.connect(test_stack1)
#     test_stack2_1.part_of.connect(test_stack2)
#     test_stack2_2.part_of.connect(test_stack2)
#     test_stack2_3.part_of.connect(test_stack2)

#     # Creating relationships for softwares
#     test_software1.builded_with.connect(test_stack1)
#     test_software1.builded_with.connect(test_stack1_1)
#     test_software1.builded_with.connect(test_stack1_2)
#     test_software1.builded_with.connect(test_stack1_3)
#     test_software1.created_by.connect(test_company1)
#     test_software2.builded_with.connect(test_stack2)
#     test_software2.builded_with.connect(test_stack2_1)
#     test_software2.builded_with.connect(test_stack2_2)
#     test_software2.builded_with.connect(test_stack2_3)
#     test_software2.created_by.connect(test_company1)
#     test_software3.builded_with.connect(test_stack3)
#     test_software3.builded_with.connect(test_stack1)
#     test_software3.builded_with.connect(test_stack2)
#     test_software3.created_by.connect(test_company2)
    


#     yield

#     objects_to_delete = [
#     test_stack1, test_stack1_1, test_stack1_2, test_stack1_3,
#     test_stack2, test_stack2_1, test_stack2_2, test_stack2_3,
#     test_stack3, test_software1, test_software2, test_software3,
#     test_user1, test_user2, test_user3, test_user4,
#     test_company1, test_company2, test_company3, test_stack4
#     ]
#     for obj in objects_to_delete:
#         for rel_name, rel in obj.defined_properties(rels=True).items():
#             # If it's a relationship property, disconnect all nodes connected by this relationship
#             if isinstance(rel, neomodel.RelationshipManager):
#                 connected_nodes = getattr(obj, rel_name).all()
#                 for connected_node in connected_nodes:
#                     getattr(obj, rel_name).disconnect(connected_node)


#     # Deleting objects from the database
#     for obj in objects_to_delete:
#         obj.delete()

# def get_mock_current_user():
#     return get_details(email="user1@test.com")

# @pytest.mark.usefixtures("database_objects")
# class TestBaseEndpoints(object):
#     @pytest.fixture(autouse=True)
#     def setup(self, app):
#         # Override the actual dependency with the mock function
#         app.dependency_overrides[get_current_user] = get_mock_current_user


# class TestSoftwareEndpoints(TestBaseEndpoints):
#     def test_add_software(self):
#         # Prepare the request payload
#         software_req = {
#             "name": "newsoftware",
#             "description": "new software description",
#         }

#         # Perform the request
#         response = client.post("api/software/add", data=software_req)

#         # Check for successful response
#         assert response.status_code == 200
#         assert response.json()["name"] == software_req["name"].lower()
#         assert response.json()["description"] == software_req["description"]

#         # Test for duplicate software addition
#         response_duplicate = client.post("api/software/add", data=software_req)
#         assert response_duplicate.status_code == 400
#         assert response_duplicate.json() == {"detail": "Software already exists"}
#         Software.nodes.get_or_none(name="newsoftware").delete()

#     def test_delete_obj(self, app):        
#         # Create a new software
#         new_software_name = "software_to_be_deleted"
#         new_software = Software(name=new_software_name, description="test_description")
#         new_software.save()
#         # Delete the newly created software
#         response = client.delete(f"/api/software/delete/{new_software_name}")
#         assert response.status_code == 200
#         assert response.json() == {"detail": "Software has been deleted"}
        
#         # Try to delete the software again, expecting a 404 since it was already deleted
#         response = client.delete(f"/api/software/delete/{new_software_name}")
#         assert response.status_code == 404


#     def test_update_obj(self):
#         # Define data to update existing software
#         existing_software = {
#             "name": "software1",
#             "description": "updated software1 description"
#         }

#         # Testing successful update
#         response = client.patch("/api/software/update", data=existing_software)
#         assert response.status_code == 200
#         assert response.json()["name"] == existing_software["name"].lower()

#         # Trying to update a non-existent software
#         non_existent_software = {
#             "name": "software_non_existent",
#             "description": "description for non-existent software"
#         }

#         response = client.patch("/api/software/update", data=non_existent_software)
#         assert response.status_code == 404
#         assert response.json()== {"detail": "Software hasn't been found"}
        
    
#     def test_list_all_software(self, app):
#         # Testing with a valid user (should return the list of softwares)
#         response = client.get("/api/software/list")
#         assert response.status_code == 200
#         assert isinstance(response.json(), list)

            
#         # Simulating unauthorized access by replacing the get_current_user dependency
#         def unauthorized_user():
#             raise HTTPException(status_code=403, detail="Not authorized user.")
#         app.dependency_overrides[get_current_user] = unauthorized_user
#         response = client.get("/api/software/list")
#         assert response.status_code == 403
#         assert response.json() == {"detail": "Not authorized user."}



#         # Reset the dependencies
#         app.dependency_overrides = {}

#     def test_get_software(self):
#         # Testing for a software that exists
#         software_name = "software1"
#         response = client.get(f"/api/software/{software_name}")
#         assert response.status_code == 200
#         assert response.json()["name"] == software_name.lower()

#         # Testing for a software that doesn't exist
#         software_name = "non_existent_software"
#         response = client.get(f"/api/software/{software_name}")
#         assert response.status_code == 404
#         assert response.json() == {"detail": "Software has not been found"}
        
#     def test_search(self):
#         # Testing only for softwares
#         response = client.get("/api/software/search", params={"softwares": "software1"})
#         assert response.status_code == 200
#         assert response.json()[0]["name"] == 'software1'

#         # Testing only for companies
#         response = client.get("/api/software/search", params={"companies": "company1"})
#         assert response.status_code == 200
#         assert response.json()[0]["name"] == 'software2'
        
#         # Testing only for stacks
#         response = client.get("/api/software/search", params={"stacks": "stack1"})
#         assert response.status_code == 200
#         assert response.json()[0]["name"] == 'software3'

#         # Testing only for users
#         response = client.get("/api/software/search", params={"users": "user1@test.com"})
#         assert response.status_code == 200
#         assert response.json()[0]["name"] == 'software1'

#         # Testing for softwares and companies
#         response = client.get("/api/software/search", params={"softwares": "software1", "companies": "company1"})
#         assert response.status_code == 200
#         assert response.json()[0]["name"] == 'software1'

#         # Testing for all parameters
#         response = client.get("/api/software/search", params={"softwares": "software1", "companies": "company1", "stacks": "stack1", "users": "user1@test.com"})
#         assert response.status_code == 200
#         assert response.json()[0]["name"] == 'software1'

#         # Testing for no parameters (should return all softwares)
#         response = client.get("/api/software/search")
#         assert response.status_code == 200
#         assert len(response.json()) > 0



# class TestLoginEndpoints(TestBaseEndpoints):
#     def test_login(self):
#         # Testing successful login
#         response = client.post("/api/auth/login", data={"username": "user@test.com", "password": "1234"})
#         assert response.status_code == 200
#         assert response.json() == {'detail': 'Login successful.'}

#         # Testing unsuccessful login with incorrect email
#         response = client.post("/api/auth/login", data={"username": "nonexistent_user@test.com", "password": "actual_password"})
#         assert response.status_code == 401
#         assert response.json() == {"detail": "Incorrect email or password."}

#         # Testing unsuccessful login with incorrect password
#         response = client.post("/api/auth/login", data={"username": "user1@test.com", "password": "wrong_password"})
#         assert response.status_code == 401
#         assert response.json() == {"detail": "Incorrect email or password."}

#     def test_create_new_user(self):
#         # Test data
#         valid_email = "new_user@company01.com"
#         invalid_domain_email = "new_user@invalid.com"
#         already_registered_email = "user1@test.com"


#         # Test for successful user creation
#         response = client.post("/api/auth/create_new_user", json={"email": valid_email})
#         a = response.json()
#         assert response.status_code == status.HTTP_201_CREATED
#         assert response.json() == {'detail': 'User successfully created.'}

#         # Test for email already registered
#         response = client.post("/api/auth/create_new_user", json={"email": already_registered_email})
#         assert response.status_code == 400
#         assert response.json() == {'detail': 'Email already registered or not allowed.'}
#         User.nodes.get(email='new_user@company01.com').delete()

#     def test_logout(self):
#         response = client.post("/api/auth/login", data={"username": "user1@test.com", "password": "1234"})
#         assert response.status_code == 200
#         # Testing successful logout
#         response = client.post("/api/auth/logout")
#         assert response.status_code == 302
#         assert response.json() == {'detail': 'Logout successful.'}


# class TestUserEndpoints(TestBaseEndpoints):    
#     def test_get_my_details(self):
#         email = "user1@test.com"
#         response = client.get("/api/user/me")
#         assert response.status_code == 200
#         assert response.json()["email"] == email

#     def test_list_all_users(self):
#         response = client.get("/api/user/list")
#         assert response.status_code == 200
#         users = response.json()
#         assert len(users) > 1

#     def test_update_obj(self):
#         # New relationships
#         updated_company = 'company2'
#         updated_softwares = 'software2'
#         updated_stacks = 'stack2'
#         response_company = CompanyReq(name='company2', description='company2 company_description2')
#         response_softwares = [SoftwareReq(name='software2', description='software2 software_description2')]
#         response_stacks = [StackReq(name='stack2', description='stack2 stack_description2', type=None)]


#         # Create a UserDetailed object with updated data
#         updated_user = {
#             'name': 'Updated Name',
#             'bio': 'Updated Bio',
#             'company':updated_company,
#             'softwares':updated_softwares,
#             'stacks':updated_stacks,
#             'active': False,
#         }

#         # Make a PATCH request to the /update endpoint
#         response = client.patch("/api/user/update", data=updated_user)

#         # Assert that the response status code is 200
#         assert response.status_code == 200

#         # Convert response JSON to UserDetailed object
#         updated_user_response = UserDetailed(**response.json())

#         # Assert that the response data matches the updated data
#         assert updated_user_response.name == updated_user['name'].lower()
#         assert updated_user_response.bio == updated_user['bio']
#         assert updated_user_response.company == response_company
#         assert updated_user_response.softwares == response_softwares
#         assert updated_user_response.stacks == response_stacks
#         assert not updated_user_response.active
        
#     def test_get_by_uid(self):
#         # Testing with a valid email
#         uid = "62876c814bd8428a8e8577004e18aa23"
#         response = client.get(f"/api/user/{uid}")
#         assert response.status_code == 200
#         assert response.json()["uid"] == uid

#         # Testing with an email not present in the database
#         uid = "non_existent_uid"
#         response = client.get(f"/api/user/{uid}")
#         assert response.status_code == 404
#         assert response.json() == {"detail": "User not found."}

#     def test_search(self):
#         # Testing only for users
#         response = client.get("/api/user/search", params={"users": "test"})
#         assert response.status_code == 200


#         # Testing only for companies
#         response = client.get("/api/user/search", params={"companies": "company1"})
#         assert response.status_code == 200
#         assert response.json()[0]["email"] == "user2@test.com"

#         # Testing only for softwares
#         response = client.get("/api/user/search", params={"softwares": "software2"})
#         assert response.status_code == 200
#         a = response.json()
#         assert response.json()[0]["email"] == "user1@test.com"

#         # Testing only for stacks
#         response = client.get("/api/user/search", params={"stacks": "stack1"})
#         assert response.status_code == 200
#         assert response.json()[0]["email"] == 'user3@test.com'

#         # Testing for users and companies
#         response = client.get("/api/user/search", params={"users": "user1@test.com", "companies": "company1"})
#         assert response.status_code == 200
#         assert response.json()[0]["email"] == "user2@test.com"


#         # Testing for all parameters
#         response = client.get("/api/user/search", params={"users": "user1@test.com", "companies": "company1", "softwares": "software1", "stacks": "stack1"})
#         assert response.status_code == 200
#         assert response.json()[0]["email"] == "user2@test.com"
 

#         # Testing for no parameters (should return all users)
#         response = client.get("/api/user/search")
#         assert response.status_code == 200
#         assert len(response.json()) > 0


# class TestCompanyEndpoints(TestBaseEndpoints): 
#     def test_add_company(self):
#         # Test data
#         data = {"name": 'New Company', "description": "New company description"}

#         # Test successful creation of company
#         response = client.post(f"/api/company/add", data=data)
#         assert response.status_code == 200
#         assert response.json()["name"] == 'new company'
#         assert response.json()["description"] == "New company description"

#         # Test for attempting to add an already existing company
#         response = client.post(f"/api/company/add", data=data)
#         assert response.status_code == 400
#         assert response.json() == {"detail": "Company already exists"}
#         Company.nodes.get_or_none(name='new company').delete()

    

#     def test_delete_obj(self):
#         # Attempt to delete a non-existing company§
#         non_existing_company_name = "nonexistent_company"
#         response = client.delete(f"/api/company/delete/{non_existing_company_name}")
#         assert response.status_code == 404
#         assert response.json() == {'detail':"Company doesn't exist"}

#         # Create a company to test successful deletion
#         existing_company_name = "company3"
#         response = client.delete(f"/api/company/delete/{existing_company_name}")
#         assert response.status_code == 200
#         assert response.json() == {'detail':'company has been deleted'}

#         # Try to delete the same company again to ensure it was successfully deleted
#         response = client.delete(f"/api/company/delete/{existing_company_name}")
#         assert response.status_code == 404
#         assert response.json() == {'detail':"Company doesn't exist"}
    
#     def test_update_obj(self):
#         # Define a company to update
#         company_data = {
#             "name": "company1",
#             "description": "Updated Company Description",
#             "softwares": "software1, software2"
#         }

#         # Make the patch request to update the company
#         response = client.patch("/api/company/update", data=company_data)

#         # Check the response status code
#         assert response.status_code == 200, response.json()

#         updated_company = Company.nodes.get(name=company_data["name"])
#         assert updated_company.description == company_data["description"]
#         assert "software1" in [s.name for s in updated_company.created_software.all()]
#         assert "software2" in [s.name for s in updated_company.created_software.all()]

#     def test_list_all_companies(self):
#         response = client.get("/api/company/list")
#         assert response.status_code == 200
#         companies = response.json()
#         assert len(companies) > 1



#     def test_get_company_by_name(self):
#         # Test for an existing company
#         existing_company_name = "company1"
#         response = client.get(f"/api/company/{existing_company_name}")
#         assert response.status_code == 200
#         assert response.json()['name'] == existing_company_name.lower()

#         # Test for a company that doesn't exist
#         non_existing_company_name = "non_existent_company"
#         response = client.get(f"/api/company/{non_existing_company_name}")
#         assert response.status_code == 500

    
#     def test_search(self):
#         # Testing only for companies
#         response = client.post("/api/company/search", params={"companies": "company2"})
#         assert response.status_code == 200
#         a = response.json()
#         assert response.json()[0]["name"] == "company2"

#         # Testing only for softwares
#         response = client.post("/api/company/search", params={"softwares": "software2"})
#         assert response.status_code == 200
#         assert response.json()[0]["name"] == "company1"

#         # Testing only for stacks
#         response = client.post("/api/company/search", params={"stacks": "stack2"})
#         c = response.json()
#         assert response.status_code == 200
#         assert response.json()[0]["name"] == "company2"

#         # Testing only for employees
#         response = client.post("/api/company/search", params={"employees": "user2@test.com"})
#         assert response.status_code == 200
#         assert response.json()[0]["name"] == "company1"

#         # Testing for companies and softwares
#         response = client.post("/api/company/search", params={"companies": "company1", "softwares": "software1"})
#         assert response.status_code == 200
#         assert response.json()[0]["name"] == "company1"

#         # Testing for all parameters
#         response = client.post("/api/company/search", params={"companies": "company1", "softwares": "software1", "stacks": "stack1", "employees": "user1@test.com"})
#         assert response.status_code == 200
#         assert response.json()[0]["name"] == "company1"

#         # Testing for no parameters (should return all companies)
#         response = client.post("/api/company/search")
#         assert response.status_code == 200
#         assert len(response.json()) > 0


# class TestStackEndpoints(TestBaseEndpoints): 
#     def test_add_stack(self):
#         new_stack_detailed = {
#             "name": "new_stack",
#             "description": "new_stack_description",
#             "stack_type": "language"
#         }
#         response = client.post("/api/stack/add", data=new_stack_detailed)
#         assert response.status_code == 200
#         assert response.json()["name"] == new_stack_detailed["name"]
#         assert response.json()["description"] == new_stack_detailed["description"]
#         assert response.json()["type"] == new_stack_detailed["stack_type"]

#         # Test by attempting to insert an existing stack
#         response = client.post("/api/stack/add", data=new_stack_detailed)
#         assert response.status_code == 400
#         a = response.json()
#         assert response.json() == {'detail': 'Stack already exists'}

#         # Test by inserting a stack with a parent stack
#         new_stack_with_parent = {
#             "name": "new_stack_with_parent",
#             "description": "new_stack_with parent_description",
#             "stack_type": "devops",
#             "part_of": "new_stack"
#         }
#         response = client.post("/api/stack/add", data=new_stack_with_parent)
#         assert response.status_code == 200
#         assert response.json()["name"] == new_stack_with_parent["name"]
#         assert response.json()["description"] == new_stack_with_parent["description"]
#         assert response.json()["type"] == new_stack_with_parent["stack_type"]
#         assert response.json()["part_of"]['name'] == new_stack_with_parent["part_of"]

#         # Test by attempting to insert a stack with a non-existent parent
#         new_stack_with_unsaved_parent = {
#             "name": "new_stack_with_unsaved_parent",
#             "description": "new_stack_with_unsaved_parent_description",
#             "stack_type": "devops",
#             "part_of": "non_existent_stack"
#         }
#         response = client.post("/api/stack/add", data=new_stack_with_unsaved_parent)
#         assert response.status_code == 404
#         assert response.json() == {'detail': "Parent stack hasn't been found"}


#         new_stack = Stack.nodes.get_or_none(name="new_stack")
#         new_stack.part_of.disconnect_all()
#         new_stack.delete()
#         new_stack_with_parent = Stack.nodes.get_or_none(name="new_stack_with_parent")
#         new_stack_with_unsaved_parent = Stack.nodes.get_or_none(name="new_stack_with_unsaved_parent")
#         try:
#             new_stack_with_parent.part_of.disconnect_all()
#         except:
#             pass
#         try:
#             new_stack_with_unsaved_parent.part_of.disconnect_all()
#         except:
#             pass
#         new_stack_with_parent.delete()
#         new_stack_with_unsaved_parent.delete()

#     def test_delete_obj(self):
#         # Testing deletion of a stack that exists
#         client.post("/api/stack/add", data={'name':'stack_to_be_deleted'})
#         response = client.delete(f"/api/stack/delete/stack_to_be_deleted")
#         assert response.status_code == 200
#         assert response.json() == {'message': 'stack has been deleted'}

#         # Confirm that the stack was actually deleted
#         stack = Stack.nodes.get_or_none(name='stack_to_be_deleted')
#         assert stack is None

#         # Testing deletion of a stack that does not exist
#         non_existent_stack_name = 'nonexistentstack'
#         response = client.delete(f"/api/stack/delete/{non_existent_stack_name}")
#         assert response.status_code == 404

#     def test_update_obj(self):
#         stack_name_to_update = 'stack1'
#         updated_description = 'Updated stack description'
#         updated_type = "LANGUAGE"

#         # Creating a payload for the update
#         stack_update_payload = {
#             "name": stack_name_to_update,
#             "description": updated_description,
#             "stack_type": updated_type
#         }

#         # Sending a patch request to the update endpoint
#         response = client.patch(f"/api/stack/update", data=stack_update_payload)

#         # Verifying the response status code and the updated details
#         assert response.status_code == 200
#         assert response.json()["description"] == updated_description
#         assert response.json()["type"] == updated_type.lower()


#         # If you have any logic for part_of or other relationships, you may add additional assertions here

#     def test_list_all_stack(self):
#         response = client.get("/api/stack/list")  # Adjust the URL according to your API's route
#         assert response.status_code == 200
#         assert len(response.json()) > 1
#         a = response.json()
#         stacks_list =['stack1', 'stack1_1', 'stack1_2', 'stack1_3', 'stack2', 'stack2_1', 'stack2_2', 'stack2_3', 'stack3'] 

#         assert all(stack in [stack['name'] for stack in response.json()] for stack in stacks_list)
    
#     def test_get_stack_by_name(self, database_objects):
#         # Test with existing stack name
#         stack_name = "stack1"
#         response = client.get(f"/api/stack/{stack_name}")
#         assert response.status_code == 200
#         assert response.json()["name"] == stack_name

#         # Test with non-existing stack name
#         non_existing_stack_name = "non_existing_stack"
#         response = client.get(f"/api/stack/{non_existing_stack_name}")
#         assert response.status_code == 500
#         assert response.json() == {"message": "Stack hasn't been found"}

#     def test_search(self):
#         # Testing only for stacks
#         stack_name = "stack2"
#         response = client.get("/api/stack/search", params={"stacks": stack_name})
#         assert response.status_code == 200
#         assert response.json()[0]["name"] == stack_name

#         # Testing only for softwares
#         response = client.get("/api/stack/search", params={"softwares": "software2"})        
#         assert response.status_code == 200
#         assert response.json()[0]["name"] == "stack2_3"

#         # Testing only for companies
#         response = client.get("/api/stack/search", params={"companies": "company1"})        
#         assert response.status_code == 200
#         assert response.json()[0]["name"] == "stack2_3"

#         # Testing only for users
#         response = client.get("/api/stack/search", params={"users": "user1@test.com"})
#         assert response.status_code == 200
#         assert response.json()[0]["name"] == "stack1"

#         # Testing for stacks and softwares
#         response = client.get("/api/stack/search", params={"stacks": stack_name, "softwares": "software1"})
#         assert response.status_code == 200
#         assert response.json()[0]["name"] == stack_name

#         # Testing for all parameters
#         response = client.get("/api/stack/search", params={"stacks": stack_name, "softwares": "software1", "users": "user1@test.com", "companies": "company1"})
#         assert response.status_code == 200
#         assert response.json()[0]["name"] == "stack2"

#         # Testing for no parameters (should return all stacks)
#         response = client.get("/api/stack/search")
#         assert response.status_code == 200
#         assert len(response.json()) > 0

