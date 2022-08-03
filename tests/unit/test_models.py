from src.database import User, Bookmark, Restaurant


def test_new_user():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the fields are defined correctly
    """
    user = User(firstName="Test", lastName="User",
                countryCode="+977", phone="9860463471", password="123456")
    assert user.firstName == 'Test'
    assert user.lastName == 'User'
    assert user.phone == '9860463471'
    assert user.password != '123456'
