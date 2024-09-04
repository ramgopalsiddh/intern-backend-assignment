import pytest
import json
from tests import app
from unittest.mock import patch
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
def h_teacher_1():
    headers = {
        'X-Principal': json.dumps({
            'teacher_id': 1,
            'user_id': 3
        })
    }
    return headers

@pytest.fixture
def mock_assignments():
    # Mock or prepare assignments data for the tests
    return [
        {'id': 1, 'student_id': 1, 'content': 'Assignment 1', 'state': 'SUBMITTED', 'grade': 'A'},
        {'id': 2, 'student_id': 2, 'content': 'Assignment 2', 'state': 'SUBMITTED', 'grade': 'B'}
    ]

@pytest.mark.parametrize("mock_assignments,expected_count", [
    ([
        {'id': 1, 'student_id': 1, 'content': 'Assignment 1', 'state': 'SUBMITTED', 'grade': 'A'},
        {'id': 2, 'student_id': 2, 'content': 'Assignment 2', 'state': 'SUBMITTED', 'grade': 'B'}
    ], 2),
    ([], 0)
])
def test_get_assignments(client, h_principal, mock_assignments, expected_count):
    with patch('core.models.assignments.Assignment.get_all_submitted_and_graded_assignments', return_value=mock_assignments):
        response = client.get('/principal/assignments', headers=h_principal)
        
        assert response.status_code == 200
        data = response.json['data']
        assert len(data) == expected_count
        if expected_count > 0:
            assert all('id' in assignment for assignment in data)
            assert all('grade' in assignment for assignment in data)



# def test_grade_or_regrade_success(client, h_principal):
#     payload = {
#         'id': 1,
#         'grade': 'A+'
#     }

#     with patch('core.models.assignments.Assignment.mark_grade') as mock_mark_grade:
#         mock_mark_grade.return_value = {
#             'id': 1,
#             'student_id': 1,
#             'content': 'Assignment 1',
#             'state': 'SUBMITTED',
#             'grade': 'A+'
#         }
#         response = client.post('/principal/assignments/grade', headers=h_principal, json=payload)

#         assert response.status_code == 200
#         data = response.json['data']
#         assert data['id'] == 1
#         assert data['grade'] == 'A+'


def test_grade_or_regrade_invalid_data(client, h_principal):
    payload = {
        'id': 1,
        'grade': None  # Invalid grade
    }
    
    response = client.post('/principal/assignments/grade', headers=h_principal, json=payload)
    
    assert response.status_code == 400
    assert response.json['error'] == 'ValidationError'  # Adjusted based on actual error handling

def test_grade_or_regrade_unauthorized(client, h_teacher_1):
    payload = {
        'id': 1,
        'grade': 'B'
    }
    
    response = client.post('/principal/assignments/grade', headers=h_teacher_1, json=payload)
    
    assert response.status_code == 403
    assert response.json['error'] == 'FyleError'  # Adjusted based on actual error handling
    assert response.json['message'] == 'requester should be a principal'  # Correct error message
