import pytest
from src.app import create_app
from src.models import User, db, ProjectType, Project


@pytest.fixture(scope='module')
def new_user():
    user = User('evan@aol.com')
    return user


@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app(config_name='dev')

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


@pytest.fixture(scope='module')
def init_database():
    # Create the database and the database table
    db.create_all()

    # Insert user data
    app = create_app('dev')
    with app.app_context():
        # project types
        building = ProjectType(type_name='Building')
        vehicle_transportation = ProjectType(type_name='Vehicle Transportation')
        infastructure_transportation = ProjectType(type_name='Infastructure Transportation')
        for pt in building, vehicle_transportation, infastructure_transportation:
            db.session.add(pt)

        # projects
        p1 = Project(name='Black Hills Energy- KS', year=2013,
                     gge_reduced=1995, ghg_reduced=2.5845225, type=building)

    yield db  # this is where the testing happens!

    db.drop_all()
