import uuid

from sqlalchemy import func

from catalog.exception import ObjectDoesNotExist
from catalog.extensions import db


class Publisher(db.Model):
    """
    Publisher database, One-to-Many
    """
    __tablename__ = 'publisher'

    id = db.Column(db.String(128), primary_key=True, default=lambda: uuid.uuid4().hex)
    name = db.Column(db.String(128), nullable=False, unique=True)
    department = db.Column(db.String(128))
    web = db.Column(db.String(1024))
    email = db.Column(db.String(128))
    role = db.Column(db.String(64))
    created = db.Column(db.DateTime(), default=func.now())
    updated = db.Column(db.DateTime(), onupdate=func.now())
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    organization = db.relationship('Organization', backref='publishers')

    @classmethod
    def get(cls, publisher_id=None, publisher_name=None, **kwargs):
        if publisher_id is not None:
            publisher = cls.query.filter_by(id=publisher_id).first()
            if publisher is None:
                raise ObjectDoesNotExist('Publisher "%s" does not exists' % publisher_id)
            return publisher

        if publisher_name is not None:
            publisher = cls.query.filter_by(name=publisher_name).first()
            if publisher is None:
                raise ObjectDoesNotExist('Publisher "%s" does not exists' % publisher_name)
            return publisher

        if len(kwargs) > 0:
            return cls.query.filter_by(**kwargs).all()

        return None

    @classmethod
    def create(cls, **params):
        """Add a new publisher
        """
        new_publisher = Publisher(**params)
        db.session.add(new_publisher)
        return new_publisher
