from sqlalchemy import func

from prism.exception import ObjectDoesNotExist
from prism.extensions import db


class Organization(db.Model):
    """
    Database of dataset-publishing organizations, One-to-Many
    """
    __tablename__ = 'organization'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    email = db.Column(db.String(128))
    web = db.Column(db.String(1024))
    country = db.Column(db.String(28))
    created = db.Column(db.DateTime(), default=func.now())
    updated = db.Column(db.DateTime(), onupdate=func.now())

    @classmethod
    def get(cls, org_id=None, org_name=None, **kwargs):
        if org_id is not None:
            organization = cls.query.filter_by(id=org_id).first()
            if organization is None:
                raise ObjectDoesNotExist('Organization "%s" does not exists' % org_id)
            return organization

        if org_name is not None:
            organization = cls.query.filter_by(name=org_name).first()
            if organization is None:
                raise ObjectDoesNotExist('Organization "%s" does not exists' % org_name)
            return organization

        if len(kwargs) > 0:
            return cls.query.filter_by(**kwargs).all()

        return None

    @classmethod
    def create(cls, **params):
        """Add a new Organization
        """
        new_org = Organization(**params)
        db.session.add(new_org)
        return new_org
