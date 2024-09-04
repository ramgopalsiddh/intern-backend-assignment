import random
from sqlalchemy import text
from core import db
from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum

def create_n_graded_assignments_for_teacher(number: int = 0, teacher_id: int = 1) -> int:
    """
    Creates 'n' graded assignments for a specified teacher and returns the count of assignments with grade 'A'.

    Parameters:
    - number (int): The number of assignments to be created.
    - teacher_id (int): The ID of the teacher for whom the assignments are created.

    Returns:
    - int: Count of assignments with grade 'A'.
    """
    # Count the existing assignments with grade 'A' for the specified teacher
    grade_a_counter = Assignment.query.filter(
        Assignment.teacher_id == teacher_id,
        Assignment.grade == GradeEnum.A.value
    ).count()

    # Create 'n' graded assignments
    for _ in range(number):
        grade = random.choice([grade.value for grade in GradeEnum])
        assignment = Assignment(
            teacher_id=teacher_id,
            student_id=1,
            grade=grade,
            content='test content',
            state=AssignmentStateEnum.GRADED.value
        )
        db.session.add(assignment)
        if grade == GradeEnum.A.value:
            grade_a_counter += 1

    db.session.commit()
    return grade_a_counter

def test_get_assignments_in_graded_state_for_each_student():
    """Test to get graded assignments for each student"""

    submitted_assignments = Assignment.query.filter_by(student_id=1).all()
    for assignment in submitted_assignments:
        assignment.state = AssignmentStateEnum.GRADED.value

    db.session.flush()
    db.session.commit()

    expected_result = [(1, 3)]

    with open('tests/SQL/number_of_graded_assignments_for_each_student.sql', encoding='utf8') as fo:
        sql = fo.read()

    sql_result = db.session.execute(text(sql)).fetchall()
    for result, expected in zip(sql_result, expected_result):
        assert result[0] == expected[0]

def test_get_grade_A_assignments_for_teacher_with_max_grading():
    """Test to get count of grade A assignments for teacher which has graded maximum assignments"""

    with open('tests/SQL/count_grade_A_assignments_by_teacher_with_max_grading.sql', encoding='utf8') as fo:
        sql = fo.read()

    grade_a_count_1 = create_n_graded_assignments_for_teacher(5)
    print(f"Grade A count from function: {grade_a_count_1}")

    sql_result = db.session.execute(text(sql)).fetchall()
    print(f"Grade A count from SQL query: {sql_result[0][0]}")

    assert grade_a_count_1 == sql_result[0][0]
