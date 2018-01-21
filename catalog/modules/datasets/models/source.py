import uuid

from sqlalchemy import func

from catalog.exception import ObjectDoesNotExist
from catalog.extensions import db


class Source(db.Model):
    """
    Data sources (distributions) database, Many-to-One
    """
    __tablename__ = 'source'

    id = db.Column(db.String(128), primary_key=True, default=lambda: uuid.uuid4().hex)
    dataset_id = db.Column(db.String(128), db.ForeignKey('dataset.id'), nullable=True)
    title = db.Column(db.String(256), nullable=False, unique=True)
    url = db.Column(db.String(1024), nullable=False)
    snapshot = db.Column(db.String(512))
    email = db.Column(db.String(128))
    description = db.Column(db.Text)
    format = db.Column(db.String(64), nullable=False, default='')
    media_type = db.Column(db.String(64), nullable=False, default='')
    schema = db.Column(db.Text)
    created = db.Column(db.DateTime(), default=func.now())
    updated = db.Column(db.DateTime(), onupdate=func.now())

    @classmethod
    def get(cls, source_id=None, source_title=None, **kwargs):
        if source_id is not None:
            source = cls.query.filter_by(id=source_id).first()
            if source is None:
                raise ObjectDoesNotExist('Source "%s" does not exists' % source_id)
            return source

        if source_title is not None:
            source = cls.query.filter_by(name=source_title).first()
            if source is None:
                raise ObjectDoesNotExist('Source "%s" does not exists' % source_title)
            return source

        if len(kwargs) > 0:
            return cls.query.filter_by(**kwargs).all()

        return None

    @classmethod
    def create(cls, **params):
        """Add a new data source
        """
        new_source = Source(**params)
        db.session.add(new_source)
        return new_source
