-- 创建数据库
CREATE DATABASE IF NOT EXISTS DataSystem CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE DataSystem;

-- 设置默认时区
SET time_zone = '+08:00';

-- 创建用户并授权（如果需要）
-- CREATE USER IF NOT EXISTS 'student_user'@'%' IDENTIFIED BY 'student_password';
-- GRANT ALL PRIVILEGES ON DataSystem.* TO 'student_user'@'%';
-- FLUSH PRIVILEGES; 