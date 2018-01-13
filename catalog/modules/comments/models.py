# encoding: utf-8

import uuid
from enum import IntEnum

from sqlalchemy.sql import func

from catalog.exception import ObjectDoesNotExist
from catalog.extensions import db


class CommentType(IntEnum):
    DATASET_COMMENT = 0
    STORY_COMMENT = 1


class Comment(db.Model):
    """
    Database of user comments on datasets and stories
    """
    __tablename__ = 'comment'

    id = db.Column(db.String(128), primary_key=True, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    target_id = db.Column(db.String(128), nullable=False)
    target_type = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='comments')
    stars = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime(), default=func.now())
    updated = db.Column(db.DateTime(), onupdate=func.now())

    @classmethod
    def comment_id(cls):
        return uuid.uuid4().hex

    @classmethod
    def create(cls, user_id, target_id, target_type, comment):
        """
        Create a new comment
        :param user_id: the user id
        :param target_id: the target id
        :param target_type: the target type, as an instance of `CommentType`
        :param comment: comment content
        :return: created comment
        """
        cid = cls.comment_id()
        comment = Comment(id=cid, comment=comment, target_id=target_id,
                          target_type=int(target_type), user_id=user_id)
        db.session.add(comment)
        return comment

    @classmethod
    def get(cls, comment_id=None, **kwargs):
        """Get specific comment or a general query"""
        if comment_id is not None:
            comment = cls.query.filter_by(id=comment_id).first()
            if comment is None:
                raise ObjectDoesNotExist('Comment "%s" does not exists' % comment_id)
            return comment

        return cls.query.filter_by(**kwargs).all()

    @classmethod
    def delete(cls, comment_id=None, comment=None):
        if comment_id is not None:
            comment = cls.get(comment_id=comment_id)
        db.session.delete(comment)

    @classmethod
    def get_target_comments(cls, target_id, target_type=None):
        """ Get all comments of a target"""
        params = {'target_id': target_id}
        if target_type is not None:
            params.update(target_type=int(target_type))
        return cls.get(**params)

    @classmethod
    def delete_target_all_comments(cls, target_id, target_type=None):
        comments = cls.get_target_comments(target_id, target_type)
        for comment in comments:
            db.session.delete(comment)
