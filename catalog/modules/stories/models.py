# encoding: utf-8
import uuid
from enum import IntEnum

from sqlalchemy.sql import func

from catalog.exception import ObjectDoesNotExist
from catalog.extensions import db
from catalog.modules.datasets.models import Dataset


class StoryType(IntEnum):
    INVALID = -1
    GENERAL = 0
    ACADEMIC = 1
    NEWS = 2


# Helper db to link datasets and stories
class StoryDatasetAssociation(db.Model):
    __tablename__ = 'dataset_story'
    __table_args__ = (
        db.PrimaryKeyConstraint('dataset_id', 'story_id', 'linker_id'),
    )

    dataset_id = db.Column(db.String(128), db.ForeignKey('dataset.id'), nullable=False)
    story_id = db.Column(db.String(128), db.ForeignKey('story.id'), nullable=False)
    linked_time = db.Column(db.DateTime, default=func.now())
    linker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dataset = db.relationship(Dataset.__name__, backref="stories_association")


class Story(db.Model):
    """
    Story database
    """
    __tablename__ = 'story'

    id = db.Column(db.String(128), primary_key=True)
    title = db.Column(db.String(512), nullable=False, unique=True)
    web = db.Column(db.String(1024), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(64))
    type = db.Column(db.Integer, nullable=False, default=int(StoryType.GENERAL))
    stars = db.Column(db.Integer, default=0)
    keywords = db.Column(db.String(1024))
    issued_time = db.Column(db.DateTime)
    contributor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contributor = db.relationship('User', backref='stories')
    created = db.Column(db.DateTime(), default=func.now())
    updated = db.Column(db.DateTime(), onupdate=func.now())

    datasets_association = db.relationship(StoryDatasetAssociation.__name__, backref="story")

    @classmethod
    def story_id(cls):
        return uuid.uuid4().hex

    @classmethod
    def get(cls, story_id=None, story_title=None, **kwargs):
        if story_id is not None:
            story = cls.query.filter_by(id=story_id).first()
            if story is None:
                raise ObjectDoesNotExist('Story "%s" does not exists' % story_id)
            return story

        if story_title is not None:
            story = cls.query.filter_by(name=story_title).first()
            if story is None:
                raise ObjectDoesNotExist('Story "%s" does not exists' % story_title)
            return story

        if len(kwargs) > 0:
            return cls.query.filter_by(**kwargs).all()

        return None

    @classmethod
    def create(cls, details=None, **params):
        """
        Create new story entry
        :param details: the detailed story info as like `StoryAcademic`
        :param params: parameters for a story
        :return: a `Story` instance
        """
        story_id = cls.story_id()
        params['id'] = story_id
        story = Story(**params)
        db.session.add(story)
        if details:
            details.story_id = story_id
            db.session.add(details)
        return story

    def associated_datasets_num(self):
        """
        Get the number of associated datasets with the story
        :return: integer
        """
        return len(list(self.datasets_association))


class StoryAcademic(db.Model):
    """
    Academic stories
    """
    __tablename__ = 'academic_story'

    story_id = db.Column(db.String(128), db.ForeignKey('story.id'), primary_key=True, unique=True)
    story = db.relationship(Story.__name__, backref='academic_story')
    paper_name = db.Column(db.String(512), nullable=False, unique=True)
    paper_link = db.Column(db.String(1024))
    paper_authors = db.Column(db.String(256))
    code_repo = db.Column(db.String(1024))
    paper_org = db.Column(db.String(128))


class StoryNews(db.Model):
    """
    News stories
    """
    __tablename__ = 'news_story'

    story_id = db.Column(db.String(128), db.ForeignKey('story.id'), primary_key=True, unique=True)
    story = db.relationship(Story.__name__, backref='news_story')
    title = db.Column(db.String(1024), nullable=False, unique=True)
    people = db.Column(db.String(1024))
    date = db.Column(db.String(1024))
    location = db.Column(db.String(128))
    country = db.Column(db.String(64))
