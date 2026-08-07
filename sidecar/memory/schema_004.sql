-- Migration 3 -> 4: record *who* approved a tool call, not just whether.
--
-- Trusted folders let a call run without asking. That is a convenience, and an
-- audit trail that cannot tell "you approved this" from "it ran because the
-- folder was trusted" is worth much less than one that can — the second is
-- precisely the case you would want to review after something went wrong.
--
-- Null for calls that needed no approval at all (AUTO and SAFE), which is the
-- same meaning `approved` already has.

ALTER TABLE tool_log ADD COLUMN approved_by TEXT;  -- user | trust | null
