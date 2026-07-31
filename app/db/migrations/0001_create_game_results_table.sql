-- Migration: create the canonical game_results table with tracking metadata
PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS game_results (
    id TEXT PRIMARY KEY NOT NULL,
    winner TEXT NOT NULL CHECK(winner IN ('X', 'O', 'draw')),
    status TEXT NOT NULL DEFAULT 'in_progress'
        CHECK(status IN ('in_progress', 'x_won', 'o_won', 'draw')),
    board_snapshot TEXT NOT NULL,
    summary TEXT,
    completed_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    recorded_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

CREATE INDEX IF NOT EXISTS idx_game_results_status ON game_results (status);
CREATE INDEX IF NOT EXISTS idx_game_results_winner ON game_results (winner);
CREATE INDEX IF NOT EXISTS idx_game_results_completed_at ON game_results (completed_at);
CREATE INDEX IF NOT EXISTS idx_game_results_recorded_at ON game_results (recorded_at);

COMMIT;
