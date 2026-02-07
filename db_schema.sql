-- ==========================================================
-- IT Assets Management System (MySQL 8.4.x) - Schema
-- phpMyAdmin: copy/paste into SQL tab and run
-- DB name: it_assets_db
-- ==========================================================

CREATE DATABASE IF NOT EXISTS it_assets_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE it_assets_db;

-- Reset tables (optional - remove if you don't want to drop)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS ticket_logs;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS checkouts;
DROP TABLE IF EXISTS assets;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

-- ======================
-- users
-- ======================
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(120) NOT NULL,
  email VARCHAR(120) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'staff',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT uq_users_email UNIQUE (email),
  CONSTRAINT ck_users_role CHECK (role IN ('admin','staff'))
) ENGINE=InnoDB;

CREATE INDEX idx_users_email ON users(email);

-- ======================
-- categories
-- ======================
CREATE TABLE categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  CONSTRAINT uq_categories_name UNIQUE (name)
) ENGINE=InnoDB;

-- ======================
-- locations
-- ======================
CREATE TABLE locations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  building VARCHAR(120) NOT NULL,
  room VARCHAR(120) NOT NULL
) ENGINE=InnoDB;

CREATE INDEX idx_locations_building_room ON locations(building, room);

-- ======================
-- assets
-- ======================
CREATE TABLE assets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  asset_tag VARCHAR(50) NOT NULL,
  name VARCHAR(200) NOT NULL,
  category_id INT NOT NULL,
  location_id INT NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'new',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by INT NULL,

  CONSTRAINT uq_assets_asset_tag UNIQUE (asset_tag),

  CONSTRAINT fk_assets_category
    FOREIGN KEY (category_id) REFERENCES categories(id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  CONSTRAINT fk_assets_location
    FOREIGN KEY (location_id) REFERENCES locations(id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  CONSTRAINT fk_assets_created_by
    FOREIGN KEY (created_by) REFERENCES users(id)
    ON UPDATE CASCADE
    ON DELETE SET NULL,

  CONSTRAINT ck_assets_status CHECK (status IN ('new','in_use','repair','retired'))
) ENGINE=InnoDB;

CREATE INDEX idx_assets_status ON assets(status);
CREATE INDEX idx_assets_category_id ON assets(category_id);
CREATE INDEX idx_assets_location_id ON assets(location_id);

-- ======================
-- checkouts
-- ======================
CREATE TABLE checkouts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  asset_id INT NOT NULL,
  borrower_id INT NOT NULL,
  checkout_date DATE NOT NULL,
  due_date DATE NULL,
  return_date DATE NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'requested',
  approved_by INT NULL,
  approved_at DATETIME NULL,

  CONSTRAINT fk_checkouts_asset
    FOREIGN KEY (asset_id) REFERENCES assets(id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  CONSTRAINT fk_checkouts_borrower
    FOREIGN KEY (borrower_id) REFERENCES users(id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  CONSTRAINT fk_checkouts_approved_by
    FOREIGN KEY (approved_by) REFERENCES users(id)
    ON UPDATE CASCADE
    ON DELETE SET NULL,

  CONSTRAINT ck_checkouts_status CHECK (status IN ('requested','approved','returned','rejected')),
  CONSTRAINT ck_checkouts_due CHECK (due_date IS NULL OR due_date >= checkout_date),
  CONSTRAINT ck_checkouts_return CHECK (return_date IS NULL OR return_date >= checkout_date)
) ENGINE=InnoDB;

CREATE INDEX idx_checkouts_asset ON checkouts(asset_id);
CREATE INDEX idx_checkouts_borrower ON checkouts(borrower_id);
CREATE INDEX idx_checkouts_status ON checkouts(status);
CREATE INDEX idx_checkouts_dates ON checkouts(checkout_date, due_date, return_date);

-- ======================
-- tickets
-- ======================
CREATE TABLE tickets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  asset_id INT NOT NULL,
  requester_id INT NOT NULL,
  issue TEXT NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'open',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_tickets_asset
    FOREIGN KEY (asset_id) REFERENCES assets(id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  CONSTRAINT fk_tickets_requester
    FOREIGN KEY (requester_id) REFERENCES users(id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  CONSTRAINT ck_tickets_status CHECK (status IN ('open','in_progress','resolved','closed'))
) ENGINE=InnoDB;

CREATE INDEX idx_tickets_asset ON tickets(asset_id);
CREATE INDEX idx_tickets_requester ON tickets(requester_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);

-- ======================
-- ticket_logs
-- ======================
CREATE TABLE ticket_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  ticket_id INT NOT NULL,
  changed_by INT NULL,
  old_status VARCHAR(20) NOT NULL,
  new_status VARCHAR(20) NOT NULL,
  note VARCHAR(255) NULL,
  changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_ticket_logs_ticket
    FOREIGN KEY (ticket_id) REFERENCES tickets(id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,

  CONSTRAINT fk_ticket_logs_changed_by
    FOREIGN KEY (changed_by) REFERENCES users(id)
    ON UPDATE CASCADE
    ON DELETE SET NULL,

  CONSTRAINT ck_ticket_logs_old CHECK (old_status IN ('open','in_progress','resolved','closed')),
  CONSTRAINT ck_ticket_logs_new CHECK (new_status IN ('open','in_progress','resolved','closed'))
) ENGINE=InnoDB;

CREATE INDEX idx_ticket_logs_ticket ON ticket_logs(ticket_id);
CREATE INDEX idx_ticket_logs_changed_at ON ticket_logs(changed_at);

-- ==========================================================
-- Optional seed (safe to rerun)
-- ==========================================================
INSERT INTO categories (name) VALUES
('Laptop'), ('Monitor'), ('Network')
ON DUPLICATE KEY UPDATE name = VALUES(name);

INSERT INTO locations (building, room) VALUES
('A', '101'),
('A', 'IT-Store');

-- NOTE:
-- Admin user will be auto-created by app.py (seed_admin)
-- email: admin@example.com  password: Admin1234!
