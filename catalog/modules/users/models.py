# encoding: utf-8
"""
User database models
--------------------
"""
import enum

from sqlalchemy.sql import func
from sqlalchemy_utils import types as column_types

from catalog.exception import ObjectDoesNotExist
from catalog.extensions import db


def _get_is_static_role_property(role_name, static_role):
    """
    A helper function that aims to provide a property getter and setter
    for static roles.

    Args:
        role_name (str)
        static_role (int) - a bit mask for a specific role

    Returns:
        property_method (property) - preconfigured getter and setter property
        for accessing role.
    """

    @property
    def _is_static_role_property(self):
        return self.has_static_role(static_role)

    @_is_static_role_property.setter
    def _is_static_role_property(self, value):
        if value:
            self.set_static_role(static_role)
        else:
            self.unset_static_role(static_role)

    _is_static_role_property.fget.__name__ = role_name
    return _is_static_role_property


class User(db.Model):
    """
    User database model.
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=80), unique=True, nullable=False)
    password = db.Column(
        column_types.PasswordType(
            max_length=128,
            schemes=('bcrypt',)
        ),
        nullable=False
    )
    email = db.Column(column_types.EmailType(length=120), unique=True, nullable=False)
    first_name = db.Column(db.String(length=30), default='', nullable=False)
    middle_name = db.Column(db.String(length=30), default='', nullable=False)
    last_name = db.Column(db.String(length=30), default='', nullable=False)

    organization = db.Column(db.String(128))
    github = db.Column(db.String(128))
    country = db.Column(db.String(64))
    bio = db.Column(db.Text)

    followers = db.Column(db.Integer, default=0, nullable=False)
    following = db.Column(db.Integer, default=0, nullable=False)

    created = db.Column(db.DateTime(), default=func.now(), nullable=False)
    updated = db.Column(db.DateTime(), onupdate=func.now(), default=func.now(), nullable=False)

    class StaticRoles(enum.Enum):
        INTERNAL = (0x8000, "Internal")
        ADMIN = (0x4000, "Admin")
        REGULAR_USER = (0x2000, "Regular User")
        ACTIVE = (0x1000, "Active Account")

        @property
        def mask(self):
            return self.value[0]

        @property
        def title(self):
            return self.value[1]

    static_roles = db.Column(db.Integer, default=0, nullable=False)
    is_internal = _get_is_static_role_property('is_internal', StaticRoles.INTERNAL)
    is_admin = _get_is_static_role_property('is_admin', StaticRoles.ADMIN)
    is_regular_user = _get_is_static_role_property('is_regular_user', StaticRoles.REGULAR_USER)
    is_active = _get_is_static_role_property('is_active', StaticRoles.ACTIVE)

    def __repr__(self):
        return (
            "<{class_name}("
            "id={self.id}, "
            "username=\"{self.username}\", "
            "email=\"{self.email}\", "
            "is_internal={self.is_internal}, "
            "is_admin={self.is_admin}, "
            "is_regular_user={self.is_regular_user}, "
            "is_active={self.is_active}, "
            ")>".format(
                class_name=self.__class__.__name__,
                self=self
            )
        )

    def has_static_role(self, role):
        return (self.static_roles & role.mask) != 0

    def set_static_role(self, role):
        if self.has_static_role(role):
            return
        self.static_roles |= role.mask

    def unset_static_role(self, role):
        if not self.has_static_role(role):
            return
        self.static_roles ^= role.mask

    def check_owner(self, user):
        return self == user

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @classmethod
    def find_with_password(cls, username, password):
        """
        Args:
            username (str)
            password (str) - plain-text password

        Returns:
            user (User) - if there is a user with a specified username and
            password, None otherwise.
        """
        user = cls.query.filter_by(username=username).first()
        if not user:
            return None
        if user.password == password:
            return user
        return None

    @classmethod
    def get(cls, user_id=None, username=None, **kwargs):
        """
        DAO: query dataset by ID or arguments.
        :return: Dataset object or None
        """
        if user_id is not None:
            user = cls.query.filter_by(id=user_id).first()
            if user is None:
                raise ObjectDoesNotExist('User "%s" does not exists' % user_id)
            return user

        if username is not None:
            user = cls.query.filter_by(username=username).first()
            if user is None:
                raise ObjectDoesNotExist('User "%s" does not exists' % username)
            return user

        if len(kwargs) > 0:
            return cls.query.filter_by(**kwargs).all()

        return None

    def follows(self, another_id):
        """Follow another user
        """
        follower = UserFollowers(user_id=another_id, follower_id=self.id)
        db.session.add(follower)

        # Update stat.
        another = self.query.get_or_404(another_id)
        another.followers += 1
        self.following += 1

    def unfollows(self, another_id):
        """Unfollow another user
        """
        follower = UserFollowers.query \
            .filter_by(user_id=another_id, follower_id=self.id) \
            .first_or_404()

        # Update stat.
        another = self.query.get_or_404(another_id)
        if another.followers > 0:
            another.followers -= 1
        if self.following > 0:
            self.following -= 1

        db.session.delete(follower)

    @classmethod
    def query_all_followers(cls, uid):
        """Return query of all followers of current user
        """
        followers_query = cls.query \
            .join(UserFollowers, User.id == UserFollowers.follower_id) \
            .filter(UserFollowers.user_id == uid)
        return followers_query

    @classmethod
    def query_all_following(cls, uid):
        """Return query of all following of current user
        """
        following_query = cls.query \
            .join(UserFollowers, User.id == UserFollowers.user_id) \
            .filter(UserFollowers.follower_id == uid)
        return following_query


class UserFollowers(db.Model):
    """
    User bidirectional following relationships
    """
    __tablename__ = 'user_followers'
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'follower_id'),
    )

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    issued_time = db.Column(db.DateTime(), default=func.now())


class UserStarDataset(db.Model):
    """
    User staring on datasets
    """
    __tablename__ = 'user_star_dataset'
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'dataset_id'),
    )

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    dataset_id = db.Column(db.String(128), db.ForeignKey('dataset.id'), nullable=True)
    stared_time = db.Column(db.DateTime(), default=func.now())


class UserStarStory(db.Model):
    """
    User staring on stories
    """
    __tablename__ = 'user_star_story'
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'story_id'),
    )

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    story_id = db.Column(db.String(128), db.ForeignKey('story.id'), nullable=True)
    stared_time = db.Column(db.DateTime(), default=func.now())
