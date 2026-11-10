-- ========================================================
-- Flyway Migration V4: Seed Local User Identities for Auth
-- Password for all demo accounts is '123456'
-- ========================================================

-- Update all existing users to verified
UPDATE users SET verified = true WHERE verified IS NOT TRUE;

-- Insert user identities for existing users so they can log in via /v1/auth/login
INSERT INTO user_identity (id, user_id, provider, provider_user_id, email, password, verified, created_at)
SELECT
    gen_random_uuid(),
    u.id,
    'LOCAL',
    u.contact_email,
    u.contact_email,
    '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iKTVKIUi',
    true,
    now()
FROM users u
WHERE u.contact_email IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM user_identity ui
      WHERE ui.provider = 'LOCAL' AND ui.provider_user_id = u.contact_email
  );
