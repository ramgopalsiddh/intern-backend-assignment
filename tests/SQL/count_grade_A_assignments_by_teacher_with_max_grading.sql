-- Write query to find the number of grade A's given by the teacher who has graded the most assignments
WITH teacher AS (
    SELECT teacher_id, COUNT(*) AS grading_count
    FROM assignments
    WHERE state = 'GRADED'
    GROUP BY teacher_id
    ORDER BY grading_count DESC
    LIMIT 1
)
SELECT COUNT(*) AS a_grade_count
FROM assignments
JOIN teacher ON assignments.teacher_id = teacher.teacher_id
WHERE grade = 'A';
