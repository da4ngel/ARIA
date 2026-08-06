-- Migration 1 -> 2: a settings key-value store.
--
-- BUILD_SPEC §7.1 defines settings.get / settings.set but §7.3 has no table for
-- them. Its first user is the selected model (Phase 1.5); Phase 9's settings
-- panel builds on the same table.
--
-- Values are JSON text so a setting can be a scalar, a list, or an object
-- without another migration each time.

CREATE TABLE settings (
  key        TEXT PRIMARY KEY,
  value      TEXT NOT NULL,          -- JSON-encoded
  updated_at TEXT NOT NULL
);

-- 'smart' means "let the router choose" rather than any specific model.
INSERT INTO settings (key, value, updated_at)
VALUES ('selected_model', '"smart"', strftime('%Y-%m-%dT%H:%M:%SZ','now'));
