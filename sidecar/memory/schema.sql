-- sidecar/memory/schema.sql
-- SQLite with sqlite-vec. PRAGMA journal_mode=WAL; foreign_keys=ON;
-- Applied by memory/db.py as migration 1. Transcribed from BUILD_SPEC §7.3.

-- ── Tier 1/2: raw conversation and episodes ──────────────────────

CREATE TABLE sessions (
  id          TEXT PRIMARY KEY,
  started_at  TEXT NOT NULL,
  ended_at    TEXT,
  title       TEXT
);

CREATE TABLE messages (
  id          INTEGER PRIMARY KEY,
  session_id  TEXT NOT NULL REFERENCES sessions(id),
  role        TEXT NOT NULL CHECK (role IN ('user','assistant','tool','system')),
  content     TEXT NOT NULL,
  tool_calls  TEXT,                    -- JSON array
  route       TEXT,                    -- 'local' | 'cloud' | null
  latency_ms  INTEGER,
  created_at  TEXT NOT NULL
);
CREATE INDEX idx_messages_session ON messages(session_id, created_at);

CREATE TABLE episodes (
  id            INTEGER PRIMARY KEY,
  session_id    TEXT REFERENCES sessions(id),
  summary       TEXT NOT NULL,         -- 1-3 sentences, model-generated
  started_at    TEXT NOT NULL,
  ended_at      TEXT NOT NULL,
  salience      REAL DEFAULT 0.5,      -- 0-1, drives retention
  access_count  INTEGER DEFAULT 0,
  last_accessed TEXT
);
CREATE VIRTUAL TABLE episode_vec USING vec0(
  episode_id INTEGER PRIMARY KEY,
  embedding  float[768]
);

-- ── Tier 3: semantic profile — what she has LEARNED about you ─────

CREATE TABLE facts (
  id             INTEGER PRIMARY KEY,
  subject        TEXT NOT NULL,        -- 'user' | 'aria' | named entity
  predicate      TEXT NOT NULL,        -- 'prefers' | 'works_on' | 'dislikes' | ...
  object         TEXT NOT NULL,
  confidence     REAL NOT NULL DEFAULT 0.6,
  source_episode INTEGER REFERENCES episodes(id),
  evidence_count INTEGER DEFAULT 1,    -- reinforced on repeat observation
  created_at     TEXT NOT NULL,
  updated_at     TEXT NOT NULL,
  superseded_by  INTEGER REFERENCES facts(id),
  user_locked    INTEGER DEFAULT 0     -- user asserted it; reflection can't overwrite
);
CREATE UNIQUE INDEX idx_facts_triple
  ON facts(subject, predicate, object) WHERE superseded_by IS NULL;
CREATE VIRTUAL TABLE fact_vec USING vec0(
  fact_id   INTEGER PRIMARY KEY,
  embedding float[768]
);

-- ── Tier 4: procedural — workflows learned by observation ─────────

CREATE TABLE procedures (
  id             INTEGER PRIMARY KEY,
  name           TEXT UNIQUE NOT NULL,
  trigger_phrase TEXT,
  steps          TEXT NOT NULL,        -- JSON: [{tool, args_template}]
  times_observed INTEGER DEFAULT 1,
  times_used     INTEGER DEFAULT 0,
  confirmed      INTEGER DEFAULT 0,    -- user approved promotion to a macro
  created_at     TEXT NOT NULL
);

-- ── Affect ────────────────────────────────────────────────────────

CREATE TABLE affect_state (
  id          INTEGER PRIMARY KEY CHECK (id = 1),
  warmth      REAL NOT NULL DEFAULT 0.6,
  energy      REAL NOT NULL DEFAULT 0.6,
  playfulness REAL NOT NULL DEFAULT 0.5,
  concern     REAL NOT NULL DEFAULT 0.2,
  updated_at  TEXT NOT NULL
);

-- Singleton seed. The CHECK(id=1) above implies exactly one row, but the spec
-- never inserts it; Phase 8's affect model would otherwise have to special-case
-- an empty table on every read.
INSERT INTO affect_state (id, warmth, energy, playfulness, concern, updated_at)
VALUES (1, 0.6, 0.6, 0.5, 0.2, strftime('%Y-%m-%dT%H:%M:%SZ','now'));

-- ── File index (the finder) ───────────────────────────────────────

CREATE TABLE file_index (
  path         TEXT PRIMARY KEY,
  name         TEXT NOT NULL,
  ext          TEXT,
  size         INTEGER,
  mtime        REAL,
  content_hash TEXT,
  indexed_at   TEXT,
  status       TEXT DEFAULT 'pending'  -- pending|indexed|skipped|error
);
CREATE INDEX idx_file_status ON file_index(status);

CREATE TABLE file_chunks (
  id        INTEGER PRIMARY KEY,
  path      TEXT NOT NULL REFERENCES file_index(path) ON DELETE CASCADE,
  chunk_idx INTEGER NOT NULL,
  text      TEXT NOT NULL
);
CREATE VIRTUAL TABLE file_vec USING vec0(
  chunk_id  INTEGER PRIMARY KEY,
  embedding float[768]
);

-- ── Audit ─────────────────────────────────────────────────────────

CREATE TABLE tool_log (
  id          INTEGER PRIMARY KEY,
  call_id     TEXT NOT NULL,
  session_id  TEXT,
  tool        TEXT NOT NULL,
  args        TEXT NOT NULL,
  tier        INTEGER NOT NULL,
  approved    INTEGER,                 -- null if no confirmation needed
  ok          INTEGER,
  error       TEXT,
  duration_ms INTEGER,
  created_at  TEXT NOT NULL
);
