import pytest
import json
from unittest.mock import patch
from core.server import app
from core.models.assignments import Assignment

@pytest.fixture
def client():
    return app.test_client()

@pytest.fixture
def h_principal():
    headers = {
        'X-Principal': json.dumps({
            'principal_id': 1,
            'user_id': 5
        })
    }
    return headers

@pytest.fixture
def mock_teachers():
    return [
        {'id': 1, 'name': 'Teacher 1'},
        {'id': 2, 'name': 'Teacher 2'}
    ]

@pytest.fixture
def mock_assignments():
    return [
        {'id': 1, 'grade': 'A'},
        {'id': 2, 'grade': 'B'}
    ]

@pytest.fixture
def mock_assignment():
    return {'id': 1, 'grade': 'A'}

@patch('core.models.teachers.Teacher.get_all_teachers')
@patch('core.apis.responses.APIResponse.respond')
def test_list_teachers(mock_api_response, mock_get_all_teachers, client, h_principal):
    mock_get_all_teachers.return_value = [{'id': 1, 'name': 'Teacher 1'}, {'id': 2, 'name': 'Teacher 2'}]
    mock_api_response.return_value = {'data': [{'id': 1, 'name': 'Teacher 1'}, {'id': 2, 'name': 'Teacher 2'}]}
    
    response = client.get('/principal/teachers', headers=h_principal)
    assert response.status_code == 200
    assert response.json == {'data': [{'id': 1, 'name': 'Teacher 1'}, {'id': 2, 'name': 'Teacher 2'}]}
    mock_get_all_teachers.assert_called_once()
    mock_api_response.assert_called_once()

@patch('core.models.teachers.Teacher.get_all_teachers')
@patch('core.apis.responses.APIResponse.respond')
def test_list_teachers_no_teachers(mock_api_response, mock_get_all_teachers, client, h_principal):
    mock_get_all_teachers.return_value = []
    mock_api_response.return_value = {'data': []}
    
    response = client.get('/principal/teachers', headers=h_principal)
    assert response.status_code == 200
    assert response.json == {'data': []}
    mock_get_all_teachers.assert_called_once()
    mock_api_response.assert_called_once()

@patch('core.models.assignments.Assignment.get_all_submitted_and_graded_assignments')
@patch('core.apis.responses.APIResponse.respond')
def test_get_assignments(mock_api_response, mock_get_all_assignments, client, h_principal, mock_assignments):
    mock_get_all_assignments.return_value = mock_assignments
    mock_api_response.return_value = {'data': mock_assignments}
    
    response = client.get('/principal/assignments', headers=h_principal)
    assert response.status_code == 200
    assert response.json == {'data': mock_assignments}
    mock_get_all_assignments.assert_called_once()
    mock_api_response.assert_called_once()

@patch('core.models.assignments.Assignment.mark_grade')
@patch('core.apis.responses.APIResponse.respond')
def test_grade_or_regrade_assignments_invalid_payload(mock_api_response, mock_mark_grade, client, h_principal):
    incoming_payload = {'invalid_field': 'value'}
    
    response = client.post('/principal/assignments/grade', 
                           headers=h_principal,
                           data=json.dumps(incoming_payload),
                           content_type='application/json')
    
    assert response.status_code == 400
    mock_mark_grade.assert_not_called()
    mock_api_response.assert_not_called()
