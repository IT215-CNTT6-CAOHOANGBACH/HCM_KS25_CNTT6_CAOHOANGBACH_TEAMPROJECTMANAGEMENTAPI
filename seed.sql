USE project_management;

START TRANSACTION;

-- Demo passwords: all users = 123

-- Xoa du lieu cu theo thu tu khoa ngoai de co the chay lai file seed.
DELETE FROM activity_logs;
DELETE FROM tasks;
DELETE FROM project_members;
DELETE FROM projects;
DELETE FROM users;

INSERT INTO users (id, email, password_hash, full_name, role, is_active)
VALUES
    (1, 'admin@example.com', '$2b$12$PNYuWPg0R1sRthS35v7jW.VqmE75zQjqrQju84cQfreGettjAIBHO', 'System Admin', 'ADMIN', 1),
    (2, 'user1@example.com', '$2b$12$PNYuWPg0R1sRthS35v7jW.VqmE75zQjqrQju84cQfreGettjAIBHO', 'Nguyen Van A', 'USER', 1),
    (3, 'user2@example.com', '$2b$12$PNYuWPg0R1sRthS35v7jW.VqmE75zQjqrQju84cQfreGettjAIBHO', 'Tran Thi B', 'USER', 1),
    (4, 'user3@example.com', '$2b$12$PNYuWPg0R1sRthS35v7jW.VqmE75zQjqrQju84cQfreGettjAIBHO', 'Le Van C', 'USER', 1);

INSERT INTO projects (id, name, description, owner_id, is_deleted)
VALUES
    (1, 'Project Management API', 'Backend API for team project management', 1, 0),
    (2, 'Mobile App', 'Mobile application development project', 2, 0),
    (3, 'Website Redesign', 'Redesign the company website', 3, 0),
    (4, 'QA Automation', 'Automated testing for the product', 4, 0);

INSERT INTO project_members (project_id, user_id, role)
VALUES
    (1, 1, 'OWNER'),
    (1, 2, 'MEMBER'),
    (1, 3, 'MEMBER'),
    (2, 2, 'OWNER'),
    (2, 3, 'MEMBER'),
    (2, 4, 'MEMBER'),
    (3, 3, 'OWNER'),
    (3, 4, 'MEMBER'),
    (4, 4, 'OWNER'),
    (4, 2, 'MEMBER');

INSERT INTO tasks
    (id, project_id, title, description, assignee_id, status, priority, due_date)
VALUES
    (1, 1, 'Design database', 'Design tables and relationships', 2, 'DONE', 'HIGH', '2026-09-01 17:00:00'),
    (2, 1, 'Implement authentication', 'Implement register, login and JWT', 2, 'IN_PROGRESS', 'HIGH', '2026-09-05 17:00:00'),
    (3, 2, 'Create mobile wireframes', 'Prepare initial screens for the app', 3, 'TODO', 'MEDIUM', '2026-09-10 17:00:00'),
    (4, 3, 'Prepare homepage design', 'Create the first homepage prototype', 4, 'TODO', 'LOW', '2026-09-15 17:00:00'),
    (5, 4, 'Write API tests', 'Add automated tests for core endpoints', 2, 'IN_PROGRESS', 'HIGH', '2026-09-20 17:00:00');

INSERT INTO activity_logs (project_id, user_id, action)
VALUES
    (1, 1, 'Tao du an moi'),
    (2, 2, 'Tao du an moi'),
    (3, 3, 'Tao du an moi'),
    (4, 4, 'Tao du an moi');

COMMIT;