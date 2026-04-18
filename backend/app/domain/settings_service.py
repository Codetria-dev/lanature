from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Settings


DEFAULT_SETTINGS: dict[str, tuple[str, str]] = {
    "registration_enabled": ("true", "Enable/disable user registration"),
    "max_pets_per_user": ("3", "Maximum pets allowed per user (free plan)"),
    "max_routines_per_pet": ("10", "Maximum routine tasks per pet"),
    "require_email_verification": ("false", "Require email verification before login"),
}


class SettingsService:
    @staticmethod
    def ensure_defaults(db: Session) -> None:
        existing = {
            setting.key
            for setting in db.query(Settings).filter(Settings.key.in_(DEFAULT_SETTINGS.keys())).all()
        }
        changed = False
        for key, (value, description) in DEFAULT_SETTINGS.items():
            if key not in existing:
                db.add(Settings(key=key, value=value, description=description))
                changed = True
        if changed:
            db.commit()

    @staticmethod
    def get_setting(db: Session, key: str, default: str | None = None) -> str | None:
        setting = db.query(Settings).filter(Settings.key == key).first()
        if setting is None:
            return default
        return setting.value

    @staticmethod
    def get_bool(db: Session, key: str, default: bool) -> bool:
        raw = SettingsService.get_setting(db, key, str(default).lower())
        if raw is None:
            return default
        return raw.strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def get_int(db: Session, key: str, default: int) -> int:
        raw = SettingsService.get_setting(db, key, str(default))
        if raw is None:
            return default
        try:
            return int(raw)
        except ValueError:
            return default


settings_service = SettingsService()
