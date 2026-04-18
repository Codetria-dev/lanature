"""
Data migration for routine_logs integrity.

Run:
  python migrate_routine_logs_constraints.py

This script:
1. Normalizes invalid status values to "pending"
2. Removes duplicate (task_id, date) rows, keeping the highest id
3. Adds a unique index on (task_id, date)
"""

from sqlalchemy import text

from app.database import engine


def run_sqlite() -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE routine_logs
                SET status = 'pending'
                WHERE status IS NULL
                   OR status NOT IN ('done', 'skipped', 'pending')
                """
            )
        )

        conn.execute(
            text(
                """
                DELETE FROM routine_logs
                WHERE id NOT IN (
                    SELECT MAX(id)
                    FROM routine_logs
                    GROUP BY task_id, date
                )
                """
            )
        )

        conn.execute(
            text(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS uq_routine_log_task_date
                ON routine_logs (task_id, date)
                """
            )
        )


def run_postgres() -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE routine_logs
                SET status = 'pending'
                WHERE status IS NULL
                   OR status NOT IN ('done', 'skipped', 'pending')
                """
            )
        )

        conn.execute(
            text(
                """
                DELETE FROM routine_logs r
                USING (
                    SELECT id
                    FROM (
                        SELECT id,
                               ROW_NUMBER() OVER (PARTITION BY task_id, date ORDER BY id DESC) AS rn
                        FROM routine_logs
                    ) ranked
                    WHERE rn > 1
                ) duplicates
                WHERE r.id = duplicates.id
                """
            )
        )

        conn.execute(
            text(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS uq_routine_log_task_date
                ON routine_logs (task_id, date)
                """
            )
        )


def main() -> None:
    dialect = engine.dialect.name
    if dialect == "sqlite":
        run_sqlite()
    else:
        run_postgres()
    print("routine_logs migration completed successfully.")


if __name__ == "__main__":
    main()
