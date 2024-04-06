import asyncio
from fastapi import HTTPException
from models.request.detailed_schemas import CommentDetailed
from config.models import Post, User, Comment
from config.logger import logger 
from config.cache import CACHE



class CommentHandler:
    def __init__(self, 
                 uid: str = None,
                 comment: str = None,
                 obj: str = 'post',
                 user_uid: str = None,
                 object_uid: str = None,
                 liked: bool = True
    ):
        self.uid = uid
        self.comment = comment
        self.obj = obj
        self.user_uid = user_uid
        self.object_uid = object_uid
        self.liked = liked


    async def get_details(self, uid) -> dict: 
        try:    
            # Find the comment by uid   
            comment_node = Comment.nodes.get_or_none(uid=uid)
            if comment_node is not None:
                result = await comment_node.full_dict()
                return result
            
        except Exception as e:
            logger.error(f"Error getting comment details: {e}")
            return None

    async def insert_obj(self) -> dict: 
        try:
            comment_node = Comment(comment=self.comment)
            comment_node.save()       

            await self.patchCommentConnections(comment_node=comment_node)

            response = await self.get_details(comment_node.uid)
            if response is None:
                raise HTTPException(status_code=500, detail="Insert stack problem encountered")
            return response
        except HTTPException as e:
            logger.error(f"Error inserting comment: {e}")
            raise e
        except Exception as e: 
            return False
        

    async def update_notification(self, post_node: Post):
        try:
            post_user_node = post_node.created_by.single()
            post_node.tagged_users.connect(post_user_node)
            for user in post_node.tagged_users:
                if user.uid != self.user_uid:
                    rels = post_node.tagged_users.all_relationships(user)
                    for rel in rels:
                        if rel.has_opened == True:
                            rel.has_opened = False
                            rel.save()
        except Exception as e:
            logger.error(f"Error updating notification: {e}")
            pass

    async def add_user_to_post(self, comment_node: Comment):
        try:
            user_node = comment_node.created_by.single()
            if user_node.uid != self.user_uid:
                if comment_node.c_on_post is not None:
                    post = comment_node.c_on_post.single()
                    post.tagged_users.connect(user_node)
                
                elif comment_node.c_on_comment is not None:
                    post = comment_node.c_on_comment.single().c_on_post.single()
                    post.tagged_users.connect(user_node)
        except Exception as e:
            logger.error(f"Error adding user to post: {e}")
            pass
        

    async def patchCommentConnections(self, comment_node: Comment):
        try:
            user = User.nodes.get_or_none(uid=self.user_uid)
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            
            comment_node.created_by.connect(user)
            
            if self.obj == 'post':
                post_node = Post.nodes.get_or_none(uid=self.object_uid)
                if post_node:
                    post_node.commented_by.connect(user)
                    comment_node.c_on_post.connect(post_node)
            elif self.obj == 'comment':
                commented_node = Comment.nodes.get_or_none(uid=self.object_uid)
                if comment_node:
                    comment_node.c_commented_by.connect(user)
                    comment_node.c_on_comment.connect(commented_node)

            await self.update_notification(post_node=comment_node.c_on_post.single())
            await self.add_user_to_post(post_node=comment_node.c_on_post.single())

            return True
        except Exception as e:
            logger.error(f"Error patching comment connections: {e}")
            pass


    async def get_by_uid(self, uid) -> CommentDetailed:
        try:   
            return await self.get_details(uid)
        except Exception as e:
            logger.error(f"Error getting comment by uid: {e}")
            return False
        


    def comment_like(self) -> bool:
        try:
            comment = Comment.nodes.get_or_none(uid=self.comment_uid)
            if comment is None:
                raise HTTPException(status_code=404, detail="comment not found")
            user = User.nodes.get_or_none(uid=self.user_uid)
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            if self.like:
                comment.c_liked_by.connect(user)
            else:
                comment.c_liked_by.disconnect(user)
            return True
        except HTTPException as e:
            logger.error(f"Error liking comment: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error liking comment: {e}")
            return False
    

    async def update_obj(self) -> bool: 
        try:
            comment_node = Comment.nodes.get_or_none(uid=self.uid)
            if comment_node is None:
                raise HTTPException(status_code=404, detail="Comment not found")
            if self.comment:
                comment_node.comment = self.comment
                comment_node.save()

            response = await self.get_details(comment_node.uid)
            if response is None:
                raise HTTPException(status_code=500, detail="Insert stack problem encountered")
    
            return response
        except HTTPException as e:
            logger.error(f"Error updating comment: {e}")
            raise e
        except Exception as e: 
            logger.error(f"Error updating comment: {e}")
            return False
        
    async def delete_obj(self) -> bool: 
        try:
            comment = Comment.nodes.get_or_none(uid=self.uid)
            if comment is None:
                raise HTTPException(status_code=404, detail="Comment not found")

            comment.c_liked_by.disconnect_all()
            comment.c_commented_by.disconnect_all()
            comment.c_on_post.disconnect_all()
            comment.c_on_comment.disconnect_all()
            comment.c_comments.disconnect_all()
            comment.delete()


            cache_key = f"comment_{self.uid}_simple_dict"
            await CACHE.delete(cache_key)

            return True
        except HTTPException as e:
            logger.error(f"Error deleting comment: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error deleting comment: {e}")
            return False