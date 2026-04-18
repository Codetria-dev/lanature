"""
Backup service for database protection and recovery.

Handles automated and manual backups, restoration, and health checks.
"""

import os
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from typing import Optional, List, Dict
import uuid
import logging

logger = logging.getLogger(__name__)

class BackupInfo:
    """Represents backup metadata."""

    def __init__(self, backup_id: str, created_at: datetime, file_path: str, size_mb: float):
        self.backup_id = backup_id
        self.created_at = created_at
        self.file_path = file_path
        self.size_mb = size_mb
        self.expires_at = created_at + timedelta(days=30)

    def to_dict(self) -> Dict:
        return {
            "backup_id": self.backup_id,
            "created_at": self.created_at.isoformat(),
            "size_mb": round(self.size_mb, 2),
            "expires_at": self.expires_at.isoformat()
        }

class BackupService:
    """
    Database backup and recovery service.

    Features:
    - Create manual backups on demand
    - Automated daily backups (optional, via scheduler)
    - List all available backups
    - Restore from backup
    - Verify backup integrity
    - Clean up old backups (> 30 days)
    """

    def __init__(self, db_url: str = "sqlite:///./lanature.db", backup_dir: str = "./backups"):
        """
        Initialize backup service.

        Args:
            db_url: Database connection URL
            backup_dir: Directory to store backups
        """
        self.db_url = db_url
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

        # Extract database path from URL
        if "sqlite:///" in db_url:
            self.db_path = db_url.replace("sqlite:///", "").replace("sqlite://", "")
            # Convert to relative path if needed
            if not os.path.isabs(self.db_path):
                self.db_path = os.path.join(os.getcwd(), self.db_path)
        else:
            self.db_path = db_url

    def create_backup(self) -> BackupInfo:
        """
        Create a backup of the database.

        Returns:
            BackupInfo with backup metadata

        Raises:
            Exception if backup creation fails
        """
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found at {self.db_path}")

        backup_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        backup_filename = f"backup-{timestamp.strftime('%Y%m%d-%H%M%S')}-{backup_id[:8]}.sql.gz"
        backup_path = self.backup_dir / backup_filename

        try:
            # For SQLite, we'll use SQL dump approach
            if self.db_path.endswith('.db'):
                self._backup_sqlite(backup_path)
            else:
                raise ValueError(f"Unsupported database type: {self.db_path}")

            file_size = backup_path.stat().st_size / (1024 * 1024)  # Convert to MB
            backup_info = BackupInfo(backup_id, timestamp, str(backup_path), file_size)

            logger.info(f"Backup created: {backup_id} ({file_size:.2f}MB)")
            return backup_info

        except Exception as e:
            # Clean up partial backup if it exists
            if backup_path.exists():
                backup_path.unlink()
            logger.error(f"Backup failed: {str(e)}")
            raise

    def _backup_sqlite(self, backup_path: Path) -> None:
        """
        Create a gzipped SQL dump of SQLite database.

        Args:
            backup_path: Path to save the backup file
        """
        try:
            # Connect to database
            conn = sqlite3.connect(self.db_path)

            # Get SQL dump
            with open(backup_path.with_suffix(''), 'w') as f:
                for line in conn.iterdump():
                    f.write(f"{line}\n")

            conn.close()

            # Compress the dump
            sql_path = backup_path.with_suffix('')
            with open(sql_path, 'rb') as f_in:
                with gzip.open(backup_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Remove uncompressed dump
            os.remove(sql_path)

        except Exception as e:
            logger.error(f"SQLite backup failed: {str(e)}")
            raise

    def list_backups(self) -> List[BackupInfo]:
        """
        List all available backups, sorted by creation date (newest first).

        Returns:
            List of BackupInfo objects
        """
        backups = []

        for backup_file in sorted(self.backup_dir.glob("backup-*.sql.gz"), reverse=True):
            try:
                # Extract timestamp from filename: backup-YYYYMMDD-HHMMSS-xxxxxxxx.sql.gz
                parts = backup_file.stem.replace('.sql', '').split('-')
                if len(parts) >= 3:
                    date_str = f"{parts[1]}-{parts[2]}"
                    timestamp = datetime.strptime(date_str, "%Y%m%d-%H%M%S")
                    backup_id = parts[3] if len(parts) > 3 else "unknown"
                    file_size = backup_file.stat().st_size / (1024 * 1024)

                    backups.append(BackupInfo(backup_id, timestamp, str(backup_file), file_size))
            except (ValueError, IndexError) as e:
                logger.warning(f"Could not parse backup file {backup_file.name}: {str(e)}")

        return backups

    def restore_backup(self, backup_id: str) -> bool:
        """
        Restore database from a backup.

        Args:
            backup_id: The backup ID to restore from

        Returns:
            True if restoration successful

        Raises:
            FileNotFoundError if backup not found
            Exception if restoration fails
        """
        backup_file = self._find_backup_file(backup_id)

        if not backup_file:
            raise FileNotFoundError(f"Backup {backup_id} not found")

        if not self.verify_backup_integrity(backup_id):
            raise ValueError(f"Backup {backup_id} is corrupted or invalid")

        try:
            # Verify we can connect to current database before proceeding
            conn = sqlite3.connect(self.db_path)
            conn.close()

            # Create backup of current database before restore
            current_backup = self.create_backup()
            logger.info(f"Created safety backup before restoration: {current_backup.backup_id}")

            # Decompress backup file
            sql_path = backup_file.parent / backup_file.stem.replace('.sql', '')
            with gzip.open(backup_file, 'rb') as f_in:
                with open(sql_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Restore database
            conn = sqlite3.connect(self.db_path)
            with open(sql_path, 'r') as f:
                conn.executescript(f.read())
            conn.commit()
            conn.close()

            # Clean up temporary SQL file
            os.remove(sql_path)

            logger.info(f"Database restored from backup: {backup_id}")
            return True

        except Exception as e:
            logger.error(f"Restoration failed: {str(e)}")
            raise

    def verify_backup_integrity(self, backup_id: str) -> bool:
        """
        Verify that a backup file is valid and not corrupted.

        Args:
            backup_id: The backup ID to verify

        Returns:
            True if backup is valid, False otherwise
        """
        backup_file = self._find_backup_file(backup_id)

        if not backup_file or not backup_file.exists():
            logger.warning(f"Backup file not found: {backup_id}")
            return False

        try:
            # Try to decompress and read the file
            with gzip.open(backup_file, 'rt') as f:
                content = f.read(1000)  # Read first 1000 chars

                # Check if it looks like SQL dump
                if 'BEGIN TRANSACTION' not in content and 'CREATE TABLE' not in content:
                    logger.warning(f"Backup file doesn't look like SQL dump: {backup_id}")
                    return False

            return True

        except (gzip.BadGzipFile, EOFError) as e:
            logger.error(f"Backup integrity check failed for {backup_id}: {str(e)}")
            return False

    def cleanup_old_backups(self, days: int = 30) -> int:
        """
        Delete backups older than specified days.

        Args:
            days: Delete backups older than this many days (default 30)

        Returns:
            Number of backups deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted_count = 0

        for backup_info in self.list_backups():
            if backup_info.created_at < cutoff_date:
                try:
                    os.remove(backup_info.file_path)
                    deleted_count += 1
                    logger.info(f"Deleted old backup: {backup_info.backup_id}")
                except Exception as e:
                    logger.error(f"Failed to delete backup {backup_info.backup_id}: {str(e)}")

        return deleted_count

    def get_database_health(self) -> Dict:
        """
        Check database health and return status.

        Returns:
            Dictionary with health information:
            - status: "healthy" or "unhealthy"
            - tables_count: Number of tables
            - total_records: Total number of records across all tables
            - last_backup: Timestamp of last backup (or None)
            - backup_status: "ok" or "missing"
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get table count
            cursor.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            tables_count = cursor.fetchone()[0]

            # Get total records across all user tables
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
            tables = cursor.fetchall()
            total_records = 0

            for (table_name,) in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    total_records += count
                except:
                    pass  # Skip tables we can't query

            conn.close()

            # Get last backup time
            backups = self.list_backups()
            last_backup = backups[0].created_at if backups else None

            # Check if backups exist
            backup_status = "ok" if backups else "missing"

            return {
                "status": "healthy",
                "tables_count": tables_count,
                "total_records": total_records,
                "last_backup": last_backup.isoformat() if last_backup else None,
                "backup_status": backup_status,
                "database_file": os.path.basename(self.db_path),
                "database_size_mb": round(os.path.getsize(self.db_path) / (1024 * 1024), 2)
            }

        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    def _find_backup_file(self, backup_id: str) -> Optional[Path]:
        """Find backup file by ID in the backups directory."""
        for backup_file in self.backup_dir.glob(f"backup-*-{backup_id[:8]}.sql.gz"):
            return backup_file
        return None

    def get_backup_file_path(self, backup_id: str) -> Optional[Path]:
        """Get the file path for a backup, for serving downloads."""
        return self._find_backup_file(backup_id)


# Global backup service instance
backup_service = BackupService()
