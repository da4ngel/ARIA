-- Migration 9 -> 10: one timeline of things that can be taken back.
--
-- `organize_folder` has had a real undo since Phase 4 — a JSON manifest in
-- data/undo/ listing every move, consumed by `undo_organize`. Nothing else did.
-- `move_file` and `rename_file` recorded their before-state only in a structlog
-- line; `write_file` overwrote outright and never read the bytes it replaced;
-- `delete_file` called `Path.unlink`, which BUILD_SPEC:1126 had already asked it
-- not to ("-> Recycle Bin, never a hard unlink").
--
-- So "undo the last thing" was answerable for exactly one tool out of six. This
-- table is the general form: one row per reversible operation, in order, with
-- enough in it to actually reverse it.
--
-- **Recording an operation and being able to reverse it are different
-- problems**, and the second one drove changes outside this file: `write_file`
-- now copies what it is about to replace into data/undo/, and the two delete
-- tools go to the Recycle Bin. A row here without those would be a timeline
-- that lists what happened and cannot undo any of it.

CREATE TABLE undo_log (
  id          INTEGER PRIMARY KEY,
  -- The tool that did it, so the timeline can say so in the user's words.
  tool        TEXT NOT NULL,
  -- 'move' | 'write' | 'delete' | 'organize'. What reversing it *means*,
  -- which is not the same as which tool ran: `move_file` and `rename_file`
  -- are one kind of undo, and `organize_folder` is a batch of them.
  kind        TEXT NOT NULL,
  -- One line, already phrased for a person: "moved budget.xlsx to Documents".
  summary     TEXT NOT NULL,
  -- What reversing it needs, as JSON. Shape depends on `kind` and is the
  -- business of `memory/undo.py` alone — nothing else reads inside it.
  payload     TEXT NOT NULL,
  session_id  TEXT,
  created_at  TEXT NOT NULL,
  -- **Both the record and the guard**, exactly as `reminders.delivered_at` is:
  -- the UPDATE that claims a row matches only while this is NULL, so an undo
  -- cannot be applied twice by two clicks in quick succession.
  undone_at   TEXT,
  -- Why it can no longer be undone, when that is knowable — the file moved
  -- again, the backup was pruned. Shown instead of a dead button.
  blocked     TEXT
);

-- The timeline reads newest-first and the panel only ever wants the recent
-- tail, so the index is on id alone; it is the primary key and monotonic,
-- which `clipboard_history` already learned is the only ordering that cannot
-- tie on a 15.6ms clock.
CREATE INDEX idx_undo_pending ON undo_log(id DESC) WHERE undone_at IS NULL;
