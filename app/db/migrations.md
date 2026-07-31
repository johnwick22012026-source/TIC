# Database Initialization & Migration Guidance

1. **Initialization**
   - Call `app.db.init_db()` during one-time setup (for example, in a startup script) to create the schema defined by the SQLAlchemy models.
   - The SQLite database file lives under `app/data/game_results.db` by default but can be overridden via the `GAME_RESULTS_DATABASE_URL` environment variable.

2. **Migration Strategy**
   - For early development, `Base.metadata.create_all()` gives a quick way to ensure tables exist.
   - When schema changes are required, add Alembic to the project and generate revision files.
   - `app/db/init.py` should continue to be the lightweight bootstrap, but migrations should become the source of truth for breaking changes.

3. **Local Development Workflow**
   - Keep the database file under version control only if the project explicitly needs example data; otherwise, include `app/data/` in `.gitignore` and recreate the file fresh.
   - Consider wrapping `init_db()` inside a CLI script or FastAPI startup event once the backend needs to serve stored results.
