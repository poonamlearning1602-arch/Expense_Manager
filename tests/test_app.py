import pytest
from app import app, db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200


def test_health_route(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'ok'


def test_404_error(client):
    response = client.get('/nonexistent')
    assert response.status_code == 404
