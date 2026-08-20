-- Migration 6 -> 7: Study Mode's state (BUILD_SPEC §9 Phase 5's memory tiers,
-- applied to teaching).
--
-- Study Mode has existed as a `ModePolicy` and a prompt since modes shipped,
-- and its prompt body already promises two things nothing could deliver:
-- "find out what he already knows before explaining", and "bring back an
-- earlier mistake when it becomes relevant". Both need somewhere to remember
-- what happened, and there was none — every session started from nothing.
--
-- These three tables are that somewhere. They are deliberately not part of
-- `facts`/`episodes`: a fact is a belief about the user that reflection may
-- supersede overnight, and mastery is a measurement of answers actually
-- given. Filing one as the other would let a model call overwrite evidence.

-- The unit that outlives a conversation. `source_path` is the lecture the
-- map was built from, kept so a resumed subject can re-read it without the
-- user having to attach the file again.
CREATE TABLE study_subjects (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    source_path     TEXT,
    created_at      TEXT NOT NULL,
    last_studied_at TEXT
);

-- The knowledge map, as a tree. `position` is what makes "what comes next"
-- answerable at all — a set has no next.
--
-- UNIQUE(subject_id, name) is the whole de-duplication mechanism, the same
-- job `procedures.name UNIQUE` already does: re-running the extraction over
-- the same lecture must not double every concept.
CREATE TABLE concepts (
    id         INTEGER PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES study_subjects(id) ON DELETE CASCADE,
    parent_id  INTEGER REFERENCES concepts(id) ON DELETE CASCADE,
    name       TEXT NOT NULL,
    summary    TEXT NOT NULL DEFAULT '',
    position   INTEGER NOT NULL DEFAULT 0,
    UNIQUE(subject_id, name)
);

CREATE INDEX idx_concepts_subject ON concepts(subject_id, position);

-- What he has actually demonstrated, per concept.
--
-- `asked`/`correct` are kept alongside `level` rather than being derivable
-- from it, because they are the evidence and `level` is the judgement. A
-- level with no count behind it cannot be argued with, and the rule that
-- 5 requires three correct answers needs the count to enforce it.
--
-- `last_wrong_at` is separate from a simple counter for the same reason:
-- "got this wrong recently" and "got this wrong once, months ago" are
-- different states and only the timestamp can tell them apart.
CREATE TABLE concept_mastery (
    concept_id    INTEGER PRIMARY KEY REFERENCES concepts(id) ON DELETE CASCADE,
    level         INTEGER NOT NULL DEFAULT 0,
    asked         INTEGER NOT NULL DEFAULT 0,
    correct       INTEGER NOT NULL DEFAULT 0,
    last_seen_at  TEXT,
    last_wrong_at TEXT
);
