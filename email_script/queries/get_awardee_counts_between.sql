SELECT
    EMP.ID_Employee,
    KP_A.points awards_received,
    KP_AB.points awards_given

FROM `Employee` EMP
LEFT JOIN (SELECT awarded_to_id, COUNT(*) points FROM KudosApp_kudospoint GROUP BY awarded_to_id) KP_A
ON KP_A.awarded_to_id = EMP.ID_Employee
LEFT JOIN (SELECT awarded_by_id, COUNT(*) points FROM KudosApp_kudospoint GROUP BY awarded_by_id) KP_AB
ON KP_AB.awarded_by_id = EMP.ID_Employee
JOIN (
    SELECT 
        employee_email,
        id_employee
        SUBSTRING(employee_email, POSITION('@' IN employee_email) - 1, 1) REGEXP '^[0-9]+$' main_addr
        FROM employees_email
        WHERE employee_email 
        LIKE '%keyintelligence.uk'
) emp_addresses 
ON emp_addresses.id_employee = EMP.ID_Employee 
AND main_addr = 1
WHERE COALESCE(KP_A.points, KP_AB.points) IS NOT NULL

GROUP BY EMP.ID_Employee

