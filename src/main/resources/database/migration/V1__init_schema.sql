-- ========================
-- ROLE
-- ========================
CREATE TABLE IF NOT EXISTS role (
                                    code        VARCHAR(50) PRIMARY KEY,
    description VARCHAR(255)
    );

-- ========================
-- USERS
-- ========================
CREATE TABLE IF NOT EXISTS users (
                                     id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_email  VARCHAR(255),
    contact_phone  VARCHAR(255),
    full_name      VARCHAR(255),
    avatar_url     VARCHAR(255),
    last_time_change timestamptz DEFAULT NULL,
    verified       BOOLEAN NOT NULL DEFAULT FALSE,
    account_status VARCHAR(50) DEFAULT 'ACTIVE',
    user_type      VARCHAR(50),
    created_at     timestamptz,
    updated_at     timestamptz,
    roles_code     VARCHAR(50),
    location       VARCHAR(255),

    CONSTRAINT fk_users_role FOREIGN KEY (roles_code) REFERENCES role(code)
    );

CREATE INDEX IF NOT EXISTS idx_users_email ON users(contact_email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(contact_phone);

-- ========================
-- USER_IDENTITY
-- ========================
CREATE TABLE IF NOT EXISTS user_identity (
                                             id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id            UUID NOT NULL UNIQUE,
    provider           VARCHAR(50) NOT NULL,
    provider_user_id   VARCHAR(255) NOT NULL,
    email              VARCHAR(255),
    password           VARCHAR(255),
    verified           BOOLEAN DEFAULT FALSE,
    last_password_change timestamptz,
    created_at         timestamptz,

    CONSTRAINT fk_user_identity_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT uq_provider_user UNIQUE (provider, provider_user_id)
    );

CREATE INDEX IF NOT EXISTS idx_user_identities_user_id ON user_identity(user_id);

-- ========================
-- INVALIDATED_TOKEN
-- ========================
CREATE TABLE IF NOT EXISTS invalidated_token (
                                                 id          UUID PRIMARY KEY,
                                                 expiry_time TIMESTAMP
);

-- ========================
-- OAUTH_CODE
-- ========================
CREATE TABLE IF NOT EXISTS oauth_code (
                                          code          VARCHAR(255) PRIMARY KEY,
    access_token  TEXT NOT NULL,
    refresh_token TEXT,
    expiry_time   timestamptz NOT NULL,
    used          BOOLEAN NOT NULL DEFAULT FALSE
    );

-- ========================
-- CREDIBILITY_SCORE
-- ========================
CREATE TABLE IF NOT EXISTS credibility_score (
                                                 id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type               VARCHAR(255) NOT NULL,
    average_score             DOUBLE PRECISION,
    total_ratings             INTEGER,
    total_completed_sessions  INTEGER,
    update_at                 timestamptz
    );

-- ========================
-- STARTUP
-- ========================
CREATE TABLE IF NOT EXISTS startup (
                                       id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id              UUID NOT NULL,
    credibility_score_id UUID,
    industry             VARCHAR(255),
    description          TEXT,
    team_size            INTEGER,

    CONSTRAINT fk_startup_user             FOREIGN KEY (user_id)              REFERENCES users(id),
    CONSTRAINT fk_startup_credibility      FOREIGN KEY (credibility_score_id) REFERENCES credibility_score(id)
    );

-- ========================
-- INVESTOR
-- ========================
CREATE TABLE IF NOT EXISTS investor (
                                        id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id              UUID NOT NULL,
    credibility_score_id UUID,
    investment_criteria  VARCHAR(255),
    preferred_stages     VARCHAR(255),
    organization_name    VARCHAR(255),
    bio                  TEXT,
    investment_min       DOUBLE PRECISION,
    investment_max       DOUBLE PRECISION,
    linkedin_url         VARCHAR(255),
    website_url          VARCHAR(255),
    twitter_url          VARCHAR(255),

    CONSTRAINT fk_investor_user        FOREIGN KEY (user_id)              REFERENCES users(id),
    CONSTRAINT fk_investor_credibility FOREIGN KEY (credibility_score_id) REFERENCES credibility_score(id)
    );

-- ========================
-- MENTOR
-- ========================
CREATE TABLE IF NOT EXISTS mentor (
                                      id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id              UUID NOT NULL,
    credibility_score_id UUID,
    expertise            VARCHAR(255) NOT NULL,
    bio                  TEXT,
    hourly_rate          DOUBLE PRECISION,
    rating               DOUBLE PRECISION,
    review               TEXT,

    CONSTRAINT fk_mentor_user        FOREIGN KEY (user_id)              REFERENCES users(id),
    CONSTRAINT fk_mentor_credibility FOREIGN KEY (credibility_score_id) REFERENCES credibility_score(id)
    );

-- ========================
-- PROJECT
-- ========================
CREATE TABLE IF NOT EXISTS project (
                                       id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    startup_id          UUID,
    project_name        VARCHAR(255) NOT NULL,
    project_description TEXT
    );

-- ========================
-- DEAL
-- ========================
CREATE TABLE IF NOT EXISTS deal (
                                    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    startup_id     UUID NOT NULL,
    investor_id    UUID NOT NULL,
    project_id     UUID NOT NULL,
    contract_value DOUBLE PRECISION NOT NULL,
    success_fee    DOUBLE PRECISION NOT NULL,
    status         VARCHAR(50) NOT NULL,
    signed_at      timestamptz NOT NULL,
    updated_at     timestamptz,

    CONSTRAINT fk_deal_startup  FOREIGN KEY (startup_id)  REFERENCES startup(id),
    CONSTRAINT fk_deal_investor FOREIGN KEY (investor_id) REFERENCES investor(id),
    CONSTRAINT fk_deal_project  FOREIGN KEY (project_id)  REFERENCES project(id)
    );

-- ========================
-- ADVISORY_SESSION
-- ========================
CREATE TABLE IF NOT EXISTS advisory_session (
                                                id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mentor_id  UUID NOT NULL,
    startup_id UUID NOT NULL,
    topic      VARCHAR(255),
    start_time timestamptz NOT NULL,
    end_time   timestamptz NOT NULL,
    format     VARCHAR(50),
    rating     DOUBLE PRECISION,
    review     TEXT,
    status     VARCHAR(50),

    CONSTRAINT fk_session_mentor  FOREIGN KEY (mentor_id)  REFERENCES mentor(id),
    CONSTRAINT fk_session_startup FOREIGN KEY (startup_id) REFERENCES startup(id)
    );

-- ========================
-- OTP
-- ========================
CREATE TABLE IF NOT EXISTS otp (
                                   id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code        VARCHAR(6) NOT NULL,
    user_id     UUID NOT NULL,
    target      VARCHAR(255),
    type        VARCHAR(32) NOT NULL,
    expiry_time timestamptz NOT NULL,
    is_used     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT fk_otp_user FOREIGN KEY (user_id) REFERENCES users(id)
    );

-- ========================
-- PASSWORD_RESET_TOKEN
-- ========================
CREATE TABLE IF NOT EXISTS password_reset_token (
                                                    id               UUID PRIMARY KEY,
                                                    token            VARCHAR(255),
    user_identity_id UUID NOT NULL,
    expiry_time      timestamptz,
    used             BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_prt_user_identity FOREIGN KEY (user_identity_id) REFERENCES user_identity(id)
    );