-- Migration 4 -> 5: record what the router decided, and what the user thought.
--
-- §9.7 asks for this outright: "Log every routing decision with the provider,
-- the resulting turn's latency and a user thumbs-up/down. After a few weeks
-- you'll have a labelled dataset to tune the rules against — that's the upgrade
-- path, not a bigger model."
--
-- None of it existed. `messages.route` stores the string 'local' or 'cloud' and
-- nothing else: not which model, not which stage decided, not the bias in force,
-- not whether the turn was spoken. So "smart mode picked the wrong model" was
-- unanswerable after the fact — the log file had a `turn.routed` line, but log
-- files rotate and cannot be queried alongside the turn they describe.
--
-- The immediate reason it is needed: a spoken "increase the volume" was answered
-- by the weakest model in the catalog, for a whole week, and the only way that
-- was found was reading a structlog line by hand.
--
-- One row per assistant turn. Nothing here is on the critical path — the write
-- happens after the reply has been streamed.

CREATE TABLE routing_log (
  id            INTEGER PRIMARY KEY,
  message_id    INTEGER REFERENCES messages(id) ON DELETE CASCADE,
  session_id    TEXT,

  -- What was decided, and why. `stage` and `detail` are the router's own
  -- RouteReason, so a row explains itself without needing the code that wrote it.
  model         TEXT NOT NULL,
  provider      TEXT NOT NULL,
  local         INTEGER NOT NULL,
  stage         TEXT NOT NULL,
  detail        TEXT,

  -- The inputs the decision was made from. Without these a row says what
  -- happened but not what it was responding to, and the dataset cannot be used
  -- to tune the rules — which is the entire point of keeping it.
  bias          TEXT NOT NULL,
  spoken        INTEGER NOT NULL DEFAULT 0,
  tool_shaped   INTEGER NOT NULL DEFAULT 0,
  chars         INTEGER NOT NULL DEFAULT 0,

  -- What it cost and whether it worked.
  latency_ms    INTEGER,
  tool_called   TEXT,
  tool_ok       INTEGER,

  -- The label. Null until the user says something, which is most rows — a
  -- thumbs-down is the signal, and silence is not agreement.
  rating        INTEGER,          -- 1 | -1 | null
  rated_at      TEXT,

  created_at    TEXT NOT NULL
);

CREATE INDEX idx_routing_log_model ON routing_log(model);
CREATE INDEX idx_routing_log_message ON routing_log(message_id);
-- Partial: rated rows are the rare ones and the only ones worth scanning for.
CREATE INDEX idx_routing_log_rated ON routing_log(rating) WHERE rating IS NOT NULL;
