# encoding: utf-8
import json


def test_modifying_dataset_info_by_owner(flask_app_client, regular_user, example_dataset, db):
    pass


def test_modifying_dataset_info_by_admin(flask_app_client, example_dataset, admin_user, regular_user, db):

    with flask_app_client.login(admin_user, auth_scopes=('datasets:write',)):
        response = flask_app_client.patch(
            '/api/v1/datasets/%s' % example_dataset.id,
            content_type='application/json',
            data=json.dumps([
                {
                    'op': 'replace',
                    'path': '/title',
                    'value': "Modified Dataset Title",
                },
                {
                    'op': 'replace',
                    'path': '/license_id',
                    'value': 1
                }
            ])
        )

        assert response.status_code == 200
        assert response.content_type == 'application/json'
        assert isinstance(response.json, dict)
        assert set(response.json.keys()) >= {'id', 'name'}
        assert response.json['id'] == example_dataset.id

        # Restore original state
        from catalog.modules.datasets.models import Dataset

        dataset_instance = Dataset.get(id=response.json['id'])
        assert dataset_instance.license_id == 1
        assert dataset_instance.license is None


def test_modifying_dataset_info_admin_fields_by_not_admin(flask_app_client, regular_user, db):
    pass
