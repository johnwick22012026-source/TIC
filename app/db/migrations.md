# Database Initialization & Migration Guidance

1. **Initialization**
   - Call `app.db.init_db()` during one-time setup (for example, in a startup script) to create the schema defined by the SQLAlchemy models.
   - The SQLite database file lives under `app/data/game_results.db` by default but can be overridden via the `GAME_RESULTS_DATABASE_URL` environment variable.

2. **Migration Strategy**
   - For early development, `Base.metadata.create_all()` gives a quick way to ensure tables exist.
   - When schema changes are required, add Alembic to the project and generate revision files. The models back the schema for finished games, so ensure each migration makes the same schema changes defined in `app/models/`.
   - `app/db/init.py` should continue to be the lightweight bootstrap, but migrations should become the source of truth for breaking changes.

3. **Persisting Game Results**
   - Game results store a UUID `id`, a constrained `winner` column (`'X'`, `'O'`, or `'draw'`), and a `status` enum that mirrors the `GameOutcome` enum from the SQLAlchemy models. `board_snapshot`, `summary`, `completed_at`, and `recorded_at` keep the provenance needed to rebuild scoreboard totals and audit when a game finished versus when it was recorded.
   - Indexes on `status`, `winner`, `mode`, `completed_at`, and `recorded_at` keep aggregate queries affordable while the table grows.
   - Queries for completed games should filter on `status` values other than `in_progress`, and can use `completed_at` vs `recorded_at` depending on whether you care about the end of play or when the backend persisted the result.
   - Since scoreboard totals are derived strictly from these persisted rows, resetting the active board or starting a new match never removes the historical rows that feed the scoreboard, ensuring continuity for players.

4. **Local Development Workflow**
   - Keep the database file under version control only if the project explicitly needs example data; otherwise, include `app/data/` in `.gitignore` and recreate the file fresh.
   - Consider wrapping `init_db()` inside a CLI script or FastAPI startup event once the backend needs to serve stored results.

5. **Migration History**
   - `0001_create_game_results_table.sql`: creates the `game_results` table with `id`, `winner`, `status`, `board_snapshot`, `summary`, `completed_at`, and `recorded_at`, plus supporting indexes and constraints.
   - `0002_add_mode_to_game_results_table.sql`: augments `game_results` with the `mode` column (restricted to `'single'` or `'versus'`), populates existing rows with the default `'single'`, and adds the associated index and constraint that lets the backend persist the selected match mode with each recorded outcome.
