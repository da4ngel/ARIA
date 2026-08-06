-- Migration 2 -> 3: clear conversations that never held a message.
--
-- Until now `chat.new` inserted a session row the moment the button was
-- pressed, so opening a new chat and closing the window left an empty
-- conversation behind. `data/aria.db` had one. `chat.new` now reserves an id
-- without writing, and the row is created by the first message instead — but
-- the rows already written still need clearing, or the history panel would open
-- on a list of blanks.
--
-- Safe at startup: migrations run before the conversation service is wired, so
-- no reserved id can be in flight. A session created and used later gets a new
-- row under the same id via `ensure_session`.

DELETE FROM sessions
WHERE id NOT IN (SELECT DISTINCT session_id FROM messages);

-- The history list orders by last activity and searches message content.
-- `idx_messages_session` already covers the per-session lookup; this one serves
-- the "first user message" subquery that renders each row's preview.
CREATE INDEX IF NOT EXISTS idx_messages_role
  ON messages(session_id, role, id);
