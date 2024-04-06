import unittest
from config.models import * 
from unittest.mock import patch
from models.request.schemas import *
from models.handlers.comment import CommentHandler
from models.handlers.post import PostHandler
import tracemalloc
import asyncio
import pytest
tracemalloc.start()

class TestComments(unittest.TestCase):
    def setUp(self):
        self.luke = User.nodes.get_or_none(email="daniel.koublachvili@company01.com")
        self.danny = User.nodes.get_or_none(email="luke.stevenson@company01.com")
        self.victor = User.nodes.get_or_none(email="victor.almeida@company01.com")
        self.python = Stack.nodes.get_or_none(name="python")
        self.django = Stack.nodes.get_or_none(name="django")
        self.voicebox = Software.nodes.get_or_none(name="voicebox")
        self._company01 = Company.nodes.get_or_none(name="company01")
        self.company02 = Company.nodes.get_or_none(name="company02")
        self.london = Location.nodes.get_or_none(country="london")
    
    @pytest.mark.asyncio
    def test_comments_relations(self):
        asyncio.run(self.asyn_comments_relations())

    async def asyn_comments_relations(self):

        postReq = PostReq(
            text='Test text tagging test user, test software voicebox, test stack django, test company company02',
            image=None,
            link=None,
            link_title=None,
            link_description=None,
            link_image=None,
            tagged_users= [self.victor.uid]
        )
        postDict = postReq.dict()
        postDict['userUid'] = self.victor.uid
        posthandler = PostHandler(**postDict)
        post = await posthandler.insert_post()
        commentHandler = CommentHandler(
            comment='Test comment on test post',
            obj='post',
            user_uid=self.luke.uid,
            object_uid=post['uid']
        )
        comment = await commentHandler.insert_obj()

        post = Post.nodes.get_or_none(uid=post['uid'])
        comment = Comment.nodes.get_or_none(uid=comment['uid'])

        assert comment.comment == 'Test comment on test post'

        created_by = comment.created_by.single()
        assert created_by.uid == self.luke.uid
        assert comment.uid in [c.uid for c in self.luke.comments.all()]
        post.delete()
        comment.delete()


    # @pytest.mark.asyncio
    # def test_post_update(self):
    #     asyncio.run(self.async_post_update())

    # async def async_post_update(self):
    #     post = Post.nodes.get_or_none(uid=self.postUid)

    #     postReq = PostReq(
    #         uid=self.postUid,
    #         text='Test text tagging test user, test software voicebox, test stack django, test company company02',
    #         image=None,
    #         link=None,
    #         link_title=None,
    #         link_description=None,
    #         link_image=None,
    #         tagged_users= [self.luke.uid]
    #     )
    #     postDict = postReq.dict()
    #     postDict['userUid'] = self.victor.uid
    #     posthandler = PostHandler(**postDict)
    #     updatedPost = await posthandler.update_obj()
    #     luke = await self.luke.simple_dict()
    #     company02 = await self.company02.simple_dict()
    #     voicebox = await self.voicebox.simple_dict()
    #     django = await self.django.simple_dict()

    #     self.assertIn(luke, updatedPost['tagged_users'])
    #     self.assertNotIn(self.victor, updatedPost['tagged_users'])
    #     self.assertIn(company02, updatedPost['tagged_companies'])
    #     self.assertNotIn(self._company01, updatedPost['tagged_companies'])
    #     self.assertIn(voicebox, updatedPost['tagged_softwares'])
    #     self.assertIn(django, updatedPost['tagged_stacks'])
    #     self.assertNotIn(self.python, updatedPost['tagged_stacks'])
    #     self.assertEqual(updatedPost['text'], 'Test text tagging test user, test software voicebox, test stack django, test company company02')
         
    #     print(f'\n \n post.tagged_users 2 \n: {post.tagged_users}')


    # @pytest.mark.asyncio
    # def test_like_post(self):
    #     asyncio.run(self.async_like_post())

    # async def async_like_post(self):
    #     post = Post.nodes.get_or_none(uid=self.postUid)
    #     postLikeReq = PostLikeReq(
    #         post_uid=self.postUid,
    #         user_uid=self.luke.uid,
    #         like='true'
    #     )
    #     post.liked_by.disconnect_all()
    #     strenght = post.strenght
    #     n_like = post.likes_count
    #     postDict = postLikeReq.dict()
    #     like = postDict.pop('like')

    #     post_handler = PostHandler(userUid=postDict['user_uid'], uid=postDict['post_uid'])
    #     post_handler.like_post(like)
    #     post = Post.nodes.get_or_none(uid=self.postUid)
    #     self.assertEqual(post.likes_count, n_like + 1)
    #     self.assertEqual(post.strenght, strenght + 1)

    #     post = Post.nodes.get_or_none(uid=self.postUid)
    #     post_handler.like_post(False)
    #     self.assertEqual(post.likes_count, n_like)
    #     self.assertEqual(post.strenght, strenght)

    

    # @pytest.mark.asyncio
    # def test_get_post(self):
    #     asyncio.run(self.async_get_post())
    
    # async def async_get_post(self):
    #     post = Post.nodes.get_or_none(uid=self.postUid)
    #     post_handler = PostHandler(uid=self.postUid, userUid=self.luke.uid)
    #     post = await post_handler.get_by_uid()
    #     self.assertEqual(post['uid'], self.postUid)


    # @pytest.mark.asyncio
    # def test_delete_post(self):
    #     asyncio.run(self.async_delete_post())
    
    # async def async_delete_post(self):
    #     postReq = PostReq(
    #         text='Test text',
    #     )
    #     postDict = postReq.dict()
    #     posthandler = PostHandler(**postDict)
    #     post = await posthandler.insert_post()
    #     post = Post.nodes.get_or_none(uid=post['uid'])
    #     post_handler = PostHandler(uid=post.uid)
    #     result = post_handler.delete_obj()
    #     self.assertTrue(result)

    # @pytest.mark.asyncio
    # def test_get_posts(self):
    #     asyncio.run(self.async_get_all_posts())
    
    # async def async_get_all_posts(self):
    #     post_handler = PostHandler(skip=0, limit=10)
    #     posts = await post_handler.get_posts()
    #     self.assertTrue(len(posts) == 10)


    # @pytest.mark.asyncio
    # def test_get_user_posts(self):
    #     asyncio.run(self.async_get_user_posts())
    
    # async def async_get_user_posts(self):
    #     post_handler = PostHandler(userUid=self.luke.uid, skip=0, limit=10)
    #     posts = await post_handler.get_user_posts()
    #     self.assertTrue(len(posts) == 10)

if __name__ == '__main__':
    unittest.main()