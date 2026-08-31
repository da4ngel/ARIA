-- Migration 8 -> 9: what a turn cost, what he copied, and what he asked to be
-- reminded of.
--
-- Three tables' worth of change in one migration because they ship together and
-- splitting them would mean three schema versions for one session's work.
--
-- The through-line: every one of these records something the sidecar already
-- produces and currently throws away. No new measurement is taken anywhere.

-- **Token counts have been arriving since Phase 1 and going straight in the
-- bin.** `StreamDelta.prompt_tokens`/`completion_tokens` are populated by every
-- provider that reports usage — Ollama (`prompt_eval_count`), OpenAI
-- (`usage.prompt_tokens`), Gemini (`usageMetadata.promptTokenCount`), Bedrock
-- (`usage.inputTokens`) — and until now the only thing in this repo that read
-- either field was a single assertion in test_bedrock.py.
--
-- **Nullable on purpose, and it is the same rule as `ModelInfo.tool_score`.**
-- OpenRouter reports no usage at all, and a row claiming 0 tokens for a turn
-- that really happened is worse than one that admits it does not know: the
-- first quietly drags every average down, the second can be counted and shown
-- as unpriced. Never default these to 0.
ALTER TABLE routing_log ADD COLUMN prompt_tokens     INTEGER;
ALTER TABLE routing_log ADD COLUMN completion_tokens INTEGER;

-- **A reminder is solicited, which is why it does not live in `proactivity`.**
-- That scheduler drops a candidate when the user has touched the machine in the
-- last 20 minutes, when four messages have already gone out today, when the
-- last one was under 90 minutes ago, or when a local model calls it noise — and
-- nothing re-queues what it drops. Every one of those gates exists to stop
-- *unsolicited* nagging. "Remind me in 20 minutes" is precisely the case the
-- focus check would suppress, and silently dropping something the user asked
-- for out loud is the one outcome a reminder must never have.
--
-- So reminders are rows with a due time, and `ReminderScheduler` reads them on
-- its own loop.
CREATE TABLE reminders (
  id           INTEGER PRIMARY KEY,
  text         TEXT NOT NULL,
  -- ISO-8601 UTC. Compared as a string, which sorts correctly because the
  -- format is fixed-width and zero-padded — the same assumption
  -- `episodes.created_at` has relied on since migration 1.
  due_at       TEXT NOT NULL,
  created_at   TEXT NOT NULL,
  -- Which conversation asked for it. Not a foreign key: deleting the chat you
  -- set a reminder in must not cancel the reminder.
  session_id   TEXT,
  -- **Both the record and the guard.** Stamped in the same step that delivers,
  -- so a tick that overlaps the previous one cannot send twice — exactly what
  -- `sessions.ended_at` does for `close_session`.
  delivered_at TEXT,
  cancelled_at TEXT
);

-- Partial, because the scheduler only ever asks for the handful that are still
-- pending and those are the rare rows once a few weeks have passed. Same idiom
-- as `idx_routing_log_rated` and `idx_messages_proactive`.
CREATE INDEX idx_reminders_due ON reminders(due_at)
  WHERE delivered_at IS NULL AND cancelled_at IS NULL;

-- **Everything copied on this machine lands here, and that is worth stating
-- plainly rather than burying.** `clipboard_watcher.py` filters out what looks
-- like a credential before writing, and that filter is a reduction in exposure,
-- not a guarantee — it will miss things, and `data/aria.db` is not a file to
-- hand to anyone afterwards. The panel says so on screen too.
CREATE TABLE clipboard_history (
  id        INTEGER PRIMARY KEY,
  content   TEXT NOT NULL,
  chars     INTEGER NOT NULL,
  -- sha256 of the content. Re-copying the same text moves the existing row's
  -- `copied_at` instead of adding a duplicate, so a history of fifty entries is
  -- fifty *different* things rather than one thing copied fifty times.
  digest    TEXT NOT NULL UNIQUE,
  -- Displayed, and **deliberately not what the ring is ordered by.** Windows'
  -- system clock ticks roughly every 15.6ms, so two copies in quick succession
  -- carry a byte-identical stamp even at microsecond precision — measured here,
  -- not assumed. `id` is monotonic and cannot tie, so it does the ordering and
  -- a re-copied entry is deleted and re-inserted to move to the front.
  copied_at TEXT NOT NULL,
  -- Foreground window title when the copy happened, best effort. Nullable
  -- because the Win32 call can fail and a missing label is not worth losing the
  -- entry over.
  source    TEXT
);

-- No index on `copied_at`: the ring is read newest-first by `id`, which is the
-- primary key and already indexed. An index nothing queries is a write cost on
-- every copy for nothing.
