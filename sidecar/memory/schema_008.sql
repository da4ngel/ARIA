-- Migration 7 -> 8: a study chat is a kind of conversation, not a mode on one.
--
-- Eyaas: "study mode is another type of chat, where everything i mention above
-- happens, dedicated fully for studies purpose." Study shipped as one of six
-- modes you toggle on an ordinary conversation; this is what makes it the
-- thing you open instead.
--
-- `kind` is durable where `ConversationMode` is not, and the difference is
-- visibility rather than a change of heart. Modes reset on New Chat because a
-- mode set last week must not silently shape today's answers — the danger was
-- always that it is *invisible*. A study chat is the opposite of invisible: you
-- created it deliberately, it is badged in Chats and listed in the Study tab.

ALTER TABLE sessions ADD COLUMN kind TEXT NOT NULL DEFAULT 'chat';

-- **A record of where this chat got to, not a binding.** A study chat may roam
-- between subjects ("now let's do networking") and which one is live is still
-- inferred per turn from whichever was most recently touched. This is stamped
-- as that happens, so the Study tab can group chats under the subject they last
-- worked on without constraining them to it.
--
-- ON DELETE SET NULL is the load-bearing half. Deleting a subject from the
-- panel already destroys its map and every answer given against it; it must not
-- also delete the conversations you had while learning it. SQLite requires an
-- added REFERENCES column to default to NULL, which is what this wants anyway.
ALTER TABLE sessions ADD COLUMN study_subject_id INTEGER
    REFERENCES study_subjects(id) ON DELETE SET NULL;

-- Study chats are read by kind in two places (the Study tab's list, and the
-- badge in Chats), and 'chat' will always be the overwhelming majority — so the
-- index is partial, the same shape `idx_messages_proactive` already uses.
CREATE INDEX idx_sessions_study ON sessions(study_subject_id) WHERE kind = 'study';
