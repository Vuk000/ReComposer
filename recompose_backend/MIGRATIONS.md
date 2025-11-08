# Database Migration Guide

## Initial Setup

The initial migration (`001_initial_migration.py`) is already included in the repository. After setting up your database and configuring your `.env` file, simply apply the migration:

```bash
# Apply migrations
alembic upgrade head
```

This will create the `users` and `rewrite_logs` tables.

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

## Revision Workflow

### Creating a New Migration

1. **Make model changes**: Update your SQLAlchemy models in `app/models/`
2. **Generate migration**: Run `alembic revision --autogenerate -m "Description of changes"`
3. **Review the migration**: Check the generated file in `alembic/versions/` to ensure it matches your intended changes
4. **Test locally**: Apply the migration to a development database and verify it works
5. **Commit**: Commit both the model changes and the migration file together

### Applying Migrations

- **Development**: Run `alembic upgrade head` to apply all pending migrations
- **Production**: Always backup your database before applying migrations
- **Rollback**: Use `alembic downgrade -1` to rollback the last migration if needed

### Best Practices

- Never edit a migration that has already been applied to production
- Create a new migration to fix issues instead of modifying existing ones
- Keep migrations small and focused on a single change when possible
- Test migrations in a staging environment that mirrors production

