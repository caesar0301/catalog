from sqlalchemy import func

from catalog.exception import ObjectDoesNotExist
from catalog.extensions import db


class License(db.Model):
    """
    License database, One-to-Many
    """
    __tablename__ = 'license'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False, unique=True)
    web = db.Column(db.String(1024))
    type = db.Column(db.String(64))
    created = db.Column(db.DateTime(), default=func.now())
    updated = db.Column(db.DateTime(), onupdate=func.now())

    @classmethod
    def get(cls, license_id=None, license_name=None, **kwargs):
        if license_id is not None:
            license = cls.query.filter_by(id=license_id).first()
            if license is None:
                raise ObjectDoesNotExist('License "%s" does not exists' % license_id)
            return license

        if license_name is not None:
            license = cls.query.filter_by(title=license_name).first()
            if license is None:
                raise ObjectDoesNotExist('License "%s" does not exists' % license_name)
            return license

        if len(kwargs) > 0:
            return cls.query.filter_by(**kwargs).all()

        return None

    @classmethod
    def create(cls, **params):
        """Add a new License
        """
        new_license = License(**params)
        db.session.add(new_license)
        return new_license
