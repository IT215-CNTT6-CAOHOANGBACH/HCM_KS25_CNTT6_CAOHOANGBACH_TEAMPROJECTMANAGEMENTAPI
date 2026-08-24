USE project_management;

START TRANSACTION;

-- Passwords used to generate these hashes:
-- admin@example.com: Admin@123456
-- user1@example.com: User@123456
-- user2@example.com: User@123456
INSERT INTO users (id, email, password_hash, full_name, role, is_active)
VALUES
    (1, 'admin@example.com', '$2b$12$9MOR45nyHtuzumZ/vyBsv.zvH16ZyL1OeE8kLBSTBxOF9wTiRgwLa', 'System Admin', 'ADMIN', 1),
    (2, 'user1@example.com', '$2b$12$3jhXth3COqShViB3X7uXmuo/uahIh33ts8fS03zKn5PKiydc03vOS', 'Nguyen Van A', 'USER', 1),
    (3, 'user2@example.com', '$2b$12$Ue0.rgcXAemqiER0mqCnduZXb07yT8AVWaZLVmrSx1u9MKhaj3aDy', 'Tran Thi B', 'USER', 1);

INSERT INTO projects (id, name, description, owner_id)
VALUES
    (1, 'Project Management API', 'Backend API for team project management', 1),
    (2, 'Mobile App', 'Mobile application development project', 2);

INSERT INTO project_members (project_id, user_id, role)
VALUES
    (1, 1, 'OWNER'),
    (1, 2, 'MEMBER'),
    (1, 3, 'MEMBER'),
    (2, 2, 'OWNER'),
    (2, 3, 'MEMBER');

INSERT INTO tasks
    (id, project_id, title, description, assignee_id, status, priority, due_date)
VALUES
    (1, 1, 'Design database', 'Design tables and relationships', 2, 'DONE', 'HIGH', '2026-09-01 17:00:00'),
    (2, 1, 'Implement authentication', 'Implement register, login and JWT', 2, 'IN_PROGRESS', 'HIGH', '2026-09-05 17:00:00'),
    (3, 1, 'Write API tests', 'Add tests for auth and users endpoints', 3, 'TODO', 'MEDIUM', '2026-09-10 17:00:00'),
    (4, 2, 'Create mobile wireframes', 'Prepare initial screens for the app', 3, 'TODO', 'LOW', '2026-09-15 17:00:00');

COMMIT;