-- Migration 5 -> 6: Phase 8's proactivity engine (BUILD_SPEC §9).
--
-- A proactive message is persisted through the same `messages` table every
-- other reply already uses — it reuses `ConversationStore`, the transcript,
-- and (via a `routing_log` row written the same way every other turn's is)
-- the existing `turn.rate` thumbs mechanism for free. "Rate each proactive
-- message useful/noise" is a query away, not a new UI.
--
-- What it does not get for free is telling itself apart from an ordinary
-- reply. `route` says which model answered, not whether anything asked it
-- to. Inferring "no preceding user turn" structurally was considered and
-- rejected — the same reasoning already on record for `tool_log.approved_by`:
-- an audit trail that cannot tell two things apart is worth much less than
-- one that can, and the rate limiter (max 4/day, min 90min apart) needs to
-- count these rows specifically, not guess at them.

ALTER TABLE messages ADD COLUMN proactive INTEGER NOT NULL DEFAULT 0;

-- Partial, and global rather than per-session: the rate limit (max 4/day,
-- min 90min apart) is about not overwhelming the person, not about one
-- conversation thread, so the query it serves scans every session's
-- proactive rows together.
CREATE INDEX idx_messages_proactive ON messages(created_at) WHERE proactive = 1;
