"""
SQL DDL constants for all database tables.
Execute in the order listed to satisfy foreign key dependencies.
"""

CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT    UNIQUE NOT NULL,
    password        TEXT    NOT NULL,
    firstname       TEXT,
    lastname        TEXT,
    linkedin_url    TEXT,
    profile_url     TEXT,
    github_url      TEXT,
    email           TEXT,
    phone           TEXT,
    objective       TEXT,
    created_dt      TEXT    DEFAULT (datetime('now')),
    last_update_dt  TEXT    DEFAULT (datetime('now'))
);
"""

CREATE_SKILLS = """
CREATE TABLE IF NOT EXISTS skills (
    id          TEXT    PRIMARY KEY,
    username    TEXT    NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    name        TEXT    NOT NULL,
    proficiency TEXT,
    summary     TEXT,
    embedding   TEXT
);
"""

CREATE_EXPERIENCE = """
CREATE TABLE IF NOT EXISTS experience (
    id          TEXT    PRIMARY KEY,
    username    TEXT    NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    type        TEXT    NOT NULL CHECK(type IN ('general', 'job', 'project', 'volunteer')),
    title       TEXT    NOT NULL,
    start_date  TEXT,
    end_date    TEXT,
    summary     TEXT,
    embedding   TEXT
);
"""

CREATE_JOBS = """
CREATE TABLE IF NOT EXISTS jobs (
    id          TEXT    PRIMARY KEY,
    username    TEXT    NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    title       TEXT    NOT NULL,
    company     TEXT    NOT NULL,
    start_date  TEXT,
    end_date    TEXT,
    summary     TEXT,
    embedding   TEXT
);
"""

CREATE_APPLICATIONS = """
CREATE TABLE IF NOT EXISTS applications (
    id           TEXT    PRIMARY KEY,
    username     TEXT    NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    title        TEXT    NOT NULL,
    company      TEXT    NOT NULL,
    website_url  TEXT,
    outcome      TEXT,
    started_dt   TEXT    DEFAULT (datetime('now')),
    submitted_dt TEXT,
    outcome_dt   TEXT
);
"""

CREATE_CHAT_MESSAGES = """
CREATE TABLE IF NOT EXISTS chat_messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id  TEXT    NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    role            TEXT    NOT NULL CHECK(role IN ('user', 'assistant', 'tool')),
    content         TEXT    NOT NULL,
    created_dt      TEXT    DEFAULT (datetime('now'))
);
"""

CREATE_JOB_EXPERIENCE = """
CREATE TABLE IF NOT EXISTS job_experience (
    job_id          TEXT    NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    experience_id   TEXT    NOT NULL REFERENCES experience(id) ON DELETE CASCADE,
    PRIMARY KEY (job_id, experience_id)
);
"""

CREATE_EXPERIENCE_SKILLS = """
CREATE TABLE IF NOT EXISTS experience_skills (
    experience_id   TEXT    NOT NULL REFERENCES experience(id) ON DELETE CASCADE,
    skill_id        TEXT    NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    PRIMARY KEY (experience_id, skill_id)
);
"""

CREATE_JOB_SKILLS = """
CREATE TABLE IF NOT EXISTS job_skills (
    job_id      TEXT    NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    skill_id    TEXT    NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    PRIMARY KEY (job_id, skill_id)
);
"""

CREATE_EXAMPLE_DOCUMENTS = """
CREATE TABLE IF NOT EXISTS example_documents (
    id                TEXT    PRIMARY KEY,
    username          TEXT    NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    original_filename TEXT    NOT NULL,
    content_type      TEXT,
    document_type     TEXT    CHECK(document_type IN ('resume', 'cover_letter', 'other')),
    created_dt        TEXT    DEFAULT (datetime('now'))
);
"""

# Ordered for FK dependency resolution
ALL_TABLES = [
    CREATE_USERS,
    CREATE_SKILLS,
    CREATE_EXPERIENCE,
    CREATE_JOBS,
    CREATE_APPLICATIONS,
    CREATE_CHAT_MESSAGES,
    CREATE_JOB_EXPERIENCE,
    CREATE_EXPERIENCE_SKILLS,
    CREATE_JOB_SKILLS,
    CREATE_EXAMPLE_DOCUMENTS,
]
