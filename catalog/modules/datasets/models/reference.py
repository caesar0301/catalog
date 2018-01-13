import uuid

from sqlalchemy import func

from catalog.exception import ObjectDoesNotExist
from catalog.extensions import db


class Reference(db.Model):
    """
    Reference database, Many-to-One
    """
    __tablename__ = 'reference'

    id = db.Column(db.String(128), primary_key=True, default=lambda: uuid.uuid4().hex)
    dataset_id = db.Column(db.String(128), db.ForeignKey('dataset.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False, unique=True)
    reference = db.Column(db.String(1024), nullable=False)
    snapshot = db.Column(db.String(512))
    created = db.Column(db.DateTime(), default=func.now())
    updated = db.Column(db.DateTime(), onupdate=func.now())

    @classmethod
    def get(cls, ref_id=None, ref_title=None, **kwargs):
        if ref_id is not None:
            reference = cls.query.filter_by(id=ref_id).first()
            if reference is None:
                raise ObjectDoesNotExist('Reference "%s" does not exists' % ref_id)
            return reference

        if ref_title is not None:
            reference = cls.query.filter_by(name=ref_title).first()
            if reference is None:
                raise ObjectDoesNotExist('Reference "%s" does not exists' % ref_title)
            return reference

        if len(kwargs) > 0:
            return cls.query.filter_by(**kwargs).all()

        return None

    @classmethod
    def create(cls, **params):
        """Add a new reference
        """
        new_ref = Reference(**params)
        db.session.add(new_ref)
        return new_ref
