from core.models.assignments import GradeEnum, AssignmentStateEnum
import pytest

@pytest.fixture
def h_teacher_3():
    # Return headers for a teacher who has no assignments
    return {'X-Principal': '{"teacher_id": 3, "user_id": 5}'}


def test_get_assignments_teacher_1(client, h_teacher_1):
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_1
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 1


def test_get_assignments_teacher_2(client, h_teacher_2):
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_2
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 2
        assert assignment['state'] in ['SUBMITTED', 'GRADED']


def test_grade_assignment_cross(client, h_teacher_2):
    """
    failure case: assignment 1 was submitted to teacher 1 and not teacher 2
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,
        json={
            "id": 1,
            "grade": GradeEnum.A.value
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_bad_grade(client, h_teacher_1):
    """
    failure case: API should allow only grades available in enum
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 1,
            "grade": "AB"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'ValidationError'


def test_grade_assignment_bad_assignment(client, h_teacher_1):
    """
    failure case: If an assignment does not exists check and throw 404
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 100000,
            "grade": GradeEnum.A.value
        }
    )

    assert response.status_code == 404
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_draft_assignment(client, h_teacher_1):
    """
    failure case: only a submitted assignment can be graded
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1
        , json={
            "id": 2,
            "grade": GradeEnum.A.value
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'
def test_grade_assignment_by_teacher_my(client, h_teacher_1):
    """
    failure case: an assignment can't be graded more than once by a teacher
    """
    # First, ensure the assignment is in the submitted state
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 7,
            "grade": GradeEnum.A.value
        }
    )

    if response.status_code != 200:
        assert response.status_code == 400
        data = response.json
        assert data['error'] == 'FyleError'
        assert data['message'] == 'Only a submitted assignment can be graded'
        return

    # Now try to grade it again
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 7,
            "grade": GradeEnum.A.value
        }
    )

    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'FyleError'
    assert data['message'] == 'Assignment is already graded'

def test_grade_assignment_success(client, h_student_1, h_teacher_1):
    """
    Success case: Create an assignment as a student, submit it, and then grade it as a teacher when all conditions are met
    """
    # Step 1: Create an assignment as a student
    create_response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            "title": "Test Assignment",
            "description": "Test Description",
            "content": "Some content"  # Ensure this is not null
        }
    )
    
    assert create_response.status_code == 200  # Assuming 200 is the success status code for upsert
    created_data = create_response.json['data']
    assignment_id = created_data['id']
    
    # Step 2: Submit the assignment as a student
    submit_response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            "id": assignment_id,
            "teacher_id": 1  # Ensure this ID is valid for the test
        }
    )
    
    assert submit_response.status_code == 200
    submitted_data = submit_response.json['data']
    assert submitted_data['id'] == assignment_id
    assert submitted_data['state'] == AssignmentStateEnum.SUBMITTED.value
    
    # Step 3: Grade the assignment as a teacher
    grade_response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": assignment_id,
            "grade": GradeEnum.B.value
        }
    )
    
    print("Grade Response Status Code:", grade_response.status_code)
    print("Grade Response Body:", grade_response.json)
    
    assert grade_response.status_code == 200
    graded_data = grade_response.json['data']
    assert graded_data['id'] == assignment_id
    assert graded_data['grade'] == GradeEnum.B.value



def test_get_assignments_empty(client, h_teacher_3):
    """
    Case where the teacher has no assignments
    """
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_3  # Assume this teacher has no assignments
    )

    assert response.status_code == 200
    assert response.json['data'] == []

def test_get_assignments_no_auth(client):
    """
    Failure case: No authentication provided
    """
    response = client.get('/teacher/assignments')

    assert response.status_code == 401
    data = response.json
    assert data['error'] == 'FyleError'

def test_grade_assignment_no_auth(client):
    """
    Failure case: No authentication provided
    """
    response = client.post(
        '/teacher/assignments/grade',
        json={
            "id": 1,
            "grade": GradeEnum.A.value
        }
    )

    assert response.status_code == 401
    data = response.json
    assert data['error'] == 'FyleError'

def test_grade_assignment_missing_field(client, h_teacher_1):
    """
    Failure case: Missing grade field in payload
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 1
        }
    )

    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'ValidationError'

def test_grade_assignment_invalid_payload(client, h_teacher_1):
    """
    Failure case: Invalid payload structure
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json="invalid_payload"
    )

    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'ValidationError'

def test_grade_assignment_invalid_method(client, h_teacher_1):
    """
    Failure case: Invalid HTTP method used
    """
    response = client.put(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 1,
            "grade": GradeEnum.A.value
        }
    )

    assert response.status_code == 405
    data = response.json
    assert data['error'] == 'MethodNotAllowed'

def test_get_assignments_invalid_endpoint(client, h_teacher_1):
    """
    Failure case: Invalid endpoint
    """
    response = client.get('/teacher/assignments/invalid', headers=h_teacher_1)

    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'NotFound'
