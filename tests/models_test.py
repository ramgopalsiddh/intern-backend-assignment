import pytest
from unittest.mock import patch, MagicMock
from core.models.assignments import Assignment, GradeEnum, AssignmentStateEnum
from core.libs import assertions
from core.apis.decorators import AuthPrincipal
from core.models.teachers import Teacher
from core.models.students import Student

@pytest.fixture
def assignment():
    return Assignment(
        id=1,
        student_id=1,
        teacher_id=1,
        content="Test content",
        grade=None,
        state=AssignmentStateEnum.DRAFT  
    )


@pytest.fixture
def auth_principal():
    return AuthPrincipal(principal_id=1, student_id=1, teacher_id=None, user_id=5)

@pytest.fixture
def auth_principal_teacher():
    return AuthPrincipal(principal_id=None, student_id=None, teacher_id=1, user_id=5)


@patch('core.models.assignments.db.session')
def test_filter(mock_db_session, assignment):
    mock_db_session.query().filter.return_value = [assignment]
    result = Assignment.filter(Assignment.id == 1)
    assert result == [assignment]

@patch('core.models.assignments.db.session')
def test_get_by_id(mock_db_session, assignment):
    mock_db_session.query().filter().first.return_value = assignment
    result = Assignment.get_by_id(1)
    assert result == assignment

@patch('core.models.assignments.db.session')
def test_upsert_create(mock_db_session, assignment):
    mock_db_session.add = MagicMock()
    mock_db_session.flush = MagicMock()

    # Test creating a new assignment
    assignment.id = None  # Simulate a new assignment (no existing ID)
    result = Assignment.upsert(assignment)
    assert result == assignment
    mock_db_session.add.assert_called_once_with(assignment)
    mock_db_session.flush.assert_called_once()


@patch('core.models.assignments.db.session')
def test_submit(mock_db_session, assignment, auth_principal):
    mock_db_session.query().filter().first.return_value = assignment
    result = Assignment.submit(1, teacher_id=2, auth_principal=auth_principal)
    assert result.state == AssignmentStateEnum.SUBMITTED
    assert result.teacher_id == 2

@patch('core.models.assignments.db.session')
def test_mark_grade_teacher(mock_db_session, assignment, auth_principal_teacher):
    assignment.state = AssignmentStateEnum.SUBMITTED
    assignment.teacher_id = auth_principal_teacher.teacher_id  # Ensure teacher_id matches
    mock_db_session.query().filter().first.return_value = assignment

    result = Assignment.mark_grade(1, GradeEnum.A, auth_principal_teacher)
    assert result.grade == GradeEnum.A
    assert result.state == AssignmentStateEnum.GRADED

@patch('core.models.assignments.db.session')
def test_get_assignments_by_student(mock_db_session, assignment):
    mock_db_session.query().filter().all.return_value = [assignment]
    result = Assignment.get_assignments_by_student(1)
    assert result == [assignment]

@patch('core.models.assignments.db.session')
def test_get_assignments_by_teacher(mock_db_session, assignment):
    mock_db_session.query().filter().all.return_value = [assignment]
    result = Assignment.get_assignments_by_teacher(1)
    assert result == [assignment]

@patch('core.models.assignments.db.session')
def test_get_all_submitted_and_graded_assignments(mock_db_session, assignment):
    assignment.state = AssignmentStateEnum.SUBMITTED
    mock_db_session.query().filter().all.return_value = [assignment]
    result = Assignment.get_all_submitted_and_graded_assignments()
    assert result == [assignment]
