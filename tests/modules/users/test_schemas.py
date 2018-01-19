# encoding: utf-8
from catalog.modules.users import schemas


def test_BaseUserSchema_dump_empty_input():
    dumped_result = schemas.UserSchema().dump({})
    assert dumped_result.errors == {}
    assert dumped_result.data == {}


def test_UserSchema_dump_user_instance(user_instance):
    user_instance.password = "password"
    dumped_result = schemas.UserSchema().dump(user_instance)
    assert dumped_result.errors == {}
    assert 'password' not in dumped_result.data
    print(dumped_result.data.keys())
    assert set(dumped_result.data.keys()) == {
        'id',
        'username',
        'first_name',
        'middle_name',
        'last_name',
        'followers',
        'following',
        'bio',
        'email',
        'country',
        'organization',
        'github',
        'created',
        'updated',
        'is_active',
        'is_admin',
        'is_regular_user'
    }


def test_UserSignupFormSchema_dump():
    form_data = {'recaptcha_server_key': 'key'}
    dumped_result = schemas.UserSignupFormSchema().dump(form_data)
    assert dumped_result.errors == {}
    assert dumped_result.data == form_data
