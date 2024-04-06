import unittest
from config.models import * 
from unittest.mock import patch
from models.request.schemas import *

class TestModels(unittest.TestCase):
    def setUp(self):
        self.userreq = UserReq(
            email='testSuperUser@example.com',
            name='Test Superuser',
            preferred_name='Test',
            role='Test Role SuperUser',
            joined_at='01/01/2023',
            twitter='test_twitter SuperUser',
            linkedin='test_linkedin SuperUser',
            github='test_github SuperUser',
            picture='/assets/img/users/SuperUser.jpg',
            bio='Test Bio SuperUser',
            password='test_password_SuperUser',
            active=True,
            is_superuser=False
        )

        self.locationReq = LocationReq(
            country='Test country',
            city='Test city',
            address='Test address'
        )
        self.companyReq = CompanyReq(
            name='Test company name',
            description='test description',
            logo='https://teamnet-company01.s3.eu-west-2.amazonaws.com/assets/img/companies/company01_logo.png'
        )

        self.softwareReq = SoftwareReq(
            name='Test software',
            client='Test client',
            project_type='Test project',
            problem='Test problem.',
            solution='Test solution.',
            comments='Test comments.',
            link='https://nitrogen.un.company01dev.com/',
            image='/assets/img/softwares/screenshot_2024-01-14_at_18.jpg'
            )

        self.stackReq = StackReq(
            name='Test stack',
            description='Test stack description',
            type='DevOps',
            image='https://code.benco.io/icon-collection/azure-docs/logo_terraform.svg'
        )

        self.postReq = PostReq(
            text='Test text tagging test user, test software, test stack',
            image=None,
            link=None,
            link_title=None,
            link_description=None,
            link_image=None,
            tagged_users=None
        )

        self.commentReq = CommentReq(
            comment='Test comment on test post'
        )

    @patch.object(Location, 'save', return_value=None)
    def test_location_creation(self, save_method):
        self.location = Location(**self.locationReq.dict())
        self.location.save()
        save_method.assert_called_once()
        self.assertEqual(self.location.country, 'test country')
        self.assertEqual(self.location.city, 'test city')
        self.assertEqual(self.location.address, 'test address')

    @patch.object(User, 'save', return_value=None)
    def test_user_creation(self, save_method):
        self.superuser = User(**self.userreq.dict())
        self.superuser.save()
        save_method.assert_called_once()

        self.assertEqual(self.superuser.email, 'testsuperuser@example.com')
        self.assertEqual(self.superuser.name, 'test superuser')
        self.assertEqual(self.superuser.preferred_name, 'test')
        self.assertEqual(self.superuser.role, 'test role superuser')
        self.assertEqual(self.superuser.joined_at, '01/01/2023')
        self.assertEqual(self.superuser.twitter, 'test_twitter SuperUser')
        self.assertEqual(self.superuser.linkedin, 'test_linkedin SuperUser')
        self.assertEqual(self.superuser.github, 'test_github SuperUser')
        self.assertEqual(self.superuser.picture, '/assets/img/users/SuperUser.jpg')
        self.assertEqual(self.superuser.bio, 'Test Bio SuperUser')
        self.assertEqual(self.superuser.password, 'test_password_SuperUser')
        self.assertEqual(self.superuser.active, True)
        self.assertEqual(self.superuser.is_superuser, False)


    @patch.object(Company, 'save', return_value=None)
    def test_company_creation(self, save_method):
        self.company = Company(**self.companyReq.dict())
        self.company.save()
        save_method.assert_called_once()
        self.assertEqual(self.company.name, 'test company name')
        self.assertEqual(self.company.description, 'test description')
        self.assertEqual(self.company.logo, 'https://teamnet-company01.s3.eu-west-2.amazonaws.com/assets/img/companies/company01_logo.png')


    @patch.object(Software, 'save', return_value=None)
    def test_software_creation(self, save_method):
        self.software = Software(**self.softwareReq.dict())
        self.software.save()
        save_method.assert_called_once()
        self.assertEqual(self.software.name, 'test software')
        self.assertEqual(self.software.client, 'test client')
        self.assertEqual(self.software.project_type, 'test project')
        self.assertEqual(self.software.problem, 'Test problem.')
        self.assertEqual(self.software.solution, 'Test solution.')
        self.assertEqual(self.software.comments, 'Test comments.')
        self.assertEqual(self.software.link, 'https://nitrogen.un.company01dev.com/')
        self.assertEqual(self.software.image, '/assets/img/softwares/screenshot_2024-01-14_at_18.jpg')


    @patch.object(Stack, 'save', return_value=None)
    def test_stack_creation(self, save_method):
        self.stack = Stack(**self.stackReq.dict())
        self.stack.save()
        save_method.assert_called_once()
        self.assertEqual(self.stack.name, 'test stack')
        self.assertEqual(self.stack.description, 'Test stack description')
        self.assertEqual(self.stack.type, 'devops')
        self.assertEqual(self.stack.image, 'https://code.benco.io/icon-collection/azure-docs/logo_terraform.svg')


    @patch.object(Post, 'save', return_value=None)
    def test_post_creation(self, save_method):
        self.post = Post(**self.postReq.dict())
        self.post.save()
        save_method.assert_called_once()
        self.assertEqual(self.post.text, 'Test text tagging test user, test software, test stack')
        self.assertEqual(self.post.image, None)
        self.assertEqual(self.post.link, None)
        self.assertEqual(self.post.link_title, None)
        self.assertEqual(self.post.link_description, None)
        self.assertEqual(self.post.link_image, None)


    @patch.object(Comment, 'save', return_value=None)
    def test_comment_creation(self, save_method):
        self.comment = Comment(**self.commentReq.dict())
        self.comment.save()
        save_method.assert_called_once()
        self.assertEqual(self.comment.comment, 'Test comment on test post') 

      
if __name__ == '__main__':
    unittest.main()