# Database Migration Guide

## Initial Setup

After setting up your database and configuring your `.env` file, create the initial migration:

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration: users and rewrite_logs tables"

# Apply migration
alembic upgrade head
```

## Migration Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Show current revision
alembic current

# Show migration history
alembic history
```

## Notes

- Migrations are stored in `alembic/versions/`
- Always review auto-generated migrations before applying
- Test migrations on a development database first

