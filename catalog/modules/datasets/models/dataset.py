import logging
import uuid

from sqlalchemy import func

from catalog.exception import ObjectDoesNotExist
from catalog.extensions import db
from .reference import Reference
from .source import Source

logger = logging.getLogger(__name__)


class Dataset(db.Model):
    """
    Database of datasets
    """
    __tablename__ = 'dataset'
    type = 'table'

    id = db.Column(db.String(128), primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=False)
    homepage = db.Column(db.String(1024), nullable=False)
    version = db.Column(db.String(24))
    keywords = db.Column(db.String(128), nullable=False)
    image = db.Column(db.String(1024))
    temporal = db.Column(db.String(64))
    spatial = db.Column(db.String(64))
    access_level = db.Column(db.String(32), nullable=False)
    copyrights = db.Column(db.String(256))
    accrual_periodicity = db.Column(db.String(32))
    specification = db.Column(db.Text)
    data_quality = db.Column(db.Boolean, nullable=False)
    data_dictionary = db.Column(db.String(1024))
    category = db.Column(db.String(128), nullable=False)
    issued_time = db.Column(db.String(64))
    language = db.Column(db.String(64))
    stars = db.Column(db.Integer, default=0)

    license_id = db.Column(db.Integer, db.ForeignKey('license.id'))
    license = db.relationship('License', backref='datasets')

    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    organization = db.relationship('Organization', backref='datasets')

    # Original publisher of dataset
    publisher_id = db.Column(db.String(128), db.ForeignKey('publisher.id'))
    publisher = db.relationship('Publisher', backref='datasets')

    # Owner
    contributor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    contributor = db.relationship('User', backref='datasets')

    created = db.Column(db.DateTime(), default=func.now())
    updated = db.Column(db.DateTime(), onupdate=func.now())
    deleted = db.Column(db.Boolean, default=False)

    # relationships
    sources = db.relationship('Source', backref='dataset', lazy='dynamic')
    references = db.relationship('Reference', backref='dataset', lazy='dynamic')

    @classmethod
    def dataset_id(cls):
        return uuid.uuid4().hex

    @classmethod
    def get(cls, id=None, deleted=False, **kwargs):
        """
        DAO: query dataset by ID or arguments.
        :return: Dataset object or None
        """
        if id is not None:
            dataset = cls.query.filter_by(id=id, deleted=deleted, **kwargs).first()
            if dataset is None:
                raise ObjectDoesNotExist('Dataset "%s" does not exists' % id)
            return dataset

        if len(kwargs) > 0:
            return Dataset.query.filter_by(**kwargs).all()
        return None

    @classmethod
    def create(cls, **params):
        new_dataset = Dataset(
            id=cls.dataset_id(),
            name=params.get('name'),
            title=params.get('title'),
            license_id=params.get('license_id'),
            organization_id=params.get('organization_id'),
            publisher_id=params.get('publisher_id'),
            contributor_id=params.get('contributor_id'),
            description=params.get('description'),
            homepage=params.get('homepage'),
            version=params.get('version'),
            keywords=params.get('keywords'),
            image=params.get('image'),
            temporal=params.get('temporal'),
            spatial=params.get('spatial'),
            access_level=params.get('access_level'),
            copyrights=params.get('copyrights'),
            accrual_periodicity=params.get('accrual_periodicity'),
            specification=params.get('specification'),
            data_quality=params.get('data_quality'),
            data_dictionary=params.get('data_dictionary'),
            category=params.get('category'),
            issued_time=params.get('issued_time'),
            language=params.get('language'),
            stars=params.get('stars', 0)
        )
        db.session.add(new_dataset)
        return new_dataset

    @classmethod
    def update(cls, id, **kwargs):
        cls.query.filter_by(id=id, deleted=False).update(dict(kwargs))
        return cls.get(id=id)

    @classmethod
    def delete(cls, id=None, dataset=None, hard=True):
        if id is not None:
            dataset = cls.get(id=id)

        if hard:
            db.session.delete(dataset)
        else:
            dataset.deleted = True

    @classmethod
    def delete_all(cls, hard=True):
        try:
            if not hard:
                db.session.get(Dataset).update(deleted=True)
            else:
                db.session.get(Dataset).delete()
        except Exception as e:
            logger.error('Problems occur for deleting datastes, rollback: {}'.format(e))
            db.session.rollback()

    @classmethod
    def update_contributor(cls, dataset_id, contributor):
        dataset = cls.get(id=dataset_id)
        dataset.contributor = contributor

    @classmethod
    def update_license(cls, dataset_id, license):
        dataset = cls.get(id=dataset_id)
        dataset.license = license

    @classmethod
    def update_organization(cls, dataset_id, organization):
        dataset = cls.get(id=dataset_id)
        dataset.organization = organization

    @classmethod
    def update_publisher(cls, dataset_id, publisher):
        dataset = cls.get(id=dataset_id)
        dataset.publisher = publisher

    @classmethod
    def add_reference(cls, dataset_id, **params):
        """Add a new Reference
        """
        name = params.get('name')
        reference = params.get('reference')
        new_ref = Reference(
            dataset_id=dataset_id,
            name=name,
            reference=reference
        )
        db.session.add(new_ref)
        return new_ref

    @classmethod
    def add_source(cls, dataset_id, **params):
        """Add a new Source
        """
        title = params.get('title')
        format = params.get('format')
        access_url = params.get('access_url')
        download_url = params.get('download_url')
        if download_url is None:
            download_url = access_url
        email = params.get('email')
        description = params.get('description')
        media_type = params.get('media_type')
        schema = params.get('schema')

        new_source = Source(
            dataset_id=dataset_id,
            title=title,
            format=format,
            access_url=access_url,
            download_url=download_url,
            email=email,
            description=description,
            media_type=media_type,
            schema=schema
        )
        db.session.add(new_source)
        return new_source

    def associated_stories_num(self):
        """
        Get the number of associated stories with the dataset
        :return: integer
        """
        return len(list(self.stories_association))
