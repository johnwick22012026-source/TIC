# Database Initialization & Migration Guidance

1. **Initialization**
   - Call `app.db.init_db()` during one-time setup (for example, in a startup script) to create the schema defined by the SQLAlchemy models.
   - The SQLite database file lives under `app/data/game_results.db` by default but can be overridden via the `GAME_RESULTS_DATABASE_URL` environment variable.

2. **Migration Strategy**
   - For early development, `Base.metadata.create_all()` gives a quick way to ensure tables exist.
   - When schema changes are required, add Alembic to the project and generate revision files. The models back the schema for finished games, so ensure each migration makes the same schema changes defined in `app/models/`.
   - `app/db/init.py` should continue to be the lightweight bootstrap, but migrations should become the source of truth for breaking changes.

3. **Persisting Game Results**
   - Game results now store a UUID primary key `id`, a `status` (one of `in_progress`, `x_won`, `o_won`, `draw`), and a `recorded_at` timestamp alongside the existing `completed_at` field. The `winner` column records the winner identifier (`X`, `O`, or `draw`).
   - Queries for completed games should filter on `status` values other than `in_progress`, and can use `completed_at` vs `recorded_at` depending on whether you care about the end of play or when the backend persisted the result.

4. **Local Development Workflow**
   - Keep the database file under version control only if the project explicitly needs example data; otherwise, include `app/data/` in `.gitignore` and recreate the file fresh.
   - Consider wrapping `init_db()` inside a CLI script or FastAPI startup event once the backend needs to serve stored results.