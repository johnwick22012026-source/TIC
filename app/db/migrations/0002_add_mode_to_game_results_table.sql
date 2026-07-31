-- Migration: persist selected match mode with recorded game outcomes
PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

ALTER TABLE game_results ADD COLUMN mode TEXT NOT NULL DEFAULT 'single'
    CHECK(mode IN ('single','versus'));

COMMIT;
