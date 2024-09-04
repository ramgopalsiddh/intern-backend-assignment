import pytest
from flask import Flask
from core import app
from core.libs.exceptions import FyleError
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import NotFound

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_ready(client):
    """Test the '/' route (Line 39)"""
    response = client.get('/')
    assert response.status_code == 200
    assert response.json['status'] == 'ready'
    assert 'time' in response.json

def test_handle_fyle_error(client):
    """Test FyleError handling (Line 20)"""
    @app.route('/fyle-error')
    def fyle_error_route():
        raise FyleError(status_code=400, message='Test FyleError')

    response = client.get('/fyle-error')
    assert response.status_code == 400
    assert response.json['error'] == 'FyleError'
    assert response.json['message'] == 'Test FyleError'

def test_handle_validation_error(client):
    """Test ValidationError handling (Line 22)"""
    @app.route('/validation-error')
    def validation_error_route():
        raise ValidationError('Test ValidationError')

    response = client.get('/validation-error')
    assert response.status_code == 400
    assert response.json['error'] == 'ValidationError'
    assert response.json['message'] == ['Test ValidationError'] 


def test_handle_integrity_error(client):
    """Test IntegrityError handling (Line 24)"""
    @app.route('/integrity-error')
    def integrity_error_route():
        raise IntegrityError('Test IntegrityError', orig='Test Origin', params=None)

    response = client.get('/integrity-error')
    assert response.status_code == 400
    assert response.json['error'] == 'IntegrityError'
    assert response.json['message'] == 'Test Origin'

def test_handle_http_exception(client):
    """Test HTTPException handling (Line 26)"""
    @app.route('/http-exception')
    def http_exception_route():
        raise NotFound('Test NotFound')

    response = client.get('/http-exception')
    assert response.status_code == 404
    assert response.json['error'] == 'NotFound'
    assert response.json['message'] == '404 Not Found: Test NotFound'

def test_handle_general_exception(client):
    """Test general exception handling (Line 47)"""
    @app.route('/general-exception')
    def general_exception_route():
        raise Exception('Test Exception')

    with pytest.raises(Exception) as excinfo:
        client.get('/general-exception')

    assert 'Test Exception' in str(excinfo.value)
