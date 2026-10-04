import os
from dataclasses import dataclass
from pathlib import Path
from typing import FrozenSet, Optional

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Prefix is intentionally fixed. It is part of the bot's public command syntax.
COMMAND_PREFIX = "<"


class ConfigurationError(RuntimeError):
    pass


def _optional_id(name: str, fallback: Optional[str] = None) -> Optional[int]:
    raw_value = os.getenv(name, fallback)
    if raw_value is None or not raw_value.strip():
        return None
    try:
        return int(raw_value)
    except ValueError as exc:
        raise ConfigurationError(f"{name} musi być numerycznym identyfikatorem Discorda.") from exc


def _id_set(name: str) -> FrozenSet[int]:
    raw_value = os.getenv(name, "")
    if not raw_value.strip():
        return frozenset()

    values = set()
    for item in raw_value.replace(";", ",").split(","):
        item = item.strip()
        if not item:
            continue
        try:
            values.add(int(item))
        except ValueError as exc:
            raise ConfigurationError(
                f"{name} musi zawierać identyfikatory Discorda oddzielone przecinkami."
            ) from exc
    return frozenset(values)


def _bool_value(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    normalized = raw_value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ConfigurationError(f"{name} musi mieć wartość true albo false.")


def _directory(name: str, default: Path) -> Path:
    configured = os.getenv(name)
    if not configured:
        return default

    path = Path(configured)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


@dataclass(frozen=True)
class Settings:
    discord_bot_token: Optional[str]
    openai_api_key: Optional[str]
    owner_id: Optional[int]
    gm_role_id: Optional[int]
    allowed_guild_ids: FrozenSet[int]
    content_data_dir: Path
    storage_dir: Path
    ai_enabled: bool
    ai_auto_start: bool
    ai_start_personality: str
    ai_model: str
    ai_summary_model: str
    command_prefix: str = COMMAND_PREFIX

    def require_discord_token(self) -> str:
        if not self.discord_bot_token:
            raise ConfigurationError(
                "Brakuje DISCORD_BOT_TOKEN. Ustaw go w .env albo w zmiennych Railway."
            )
        return self.discord_bot_token


settings = Settings(
    discord_bot_token=os.getenv("DISCORD_BOT_TOKEN"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    owner_id=_optional_id("BOT_OWNER_ID", os.getenv("ADMIN_ID")),
    gm_role_id=_optional_id("GM_ROLE_ID"),
    allowed_guild_ids=_id_set("ALLOWED_GUILD_IDS"),
    content_data_dir=_directory("CONTENT_DATA_DIR", PROJECT_ROOT / "data"),
    storage_dir=_directory("STORAGE_DIR", PROJECT_ROOT / "data"),
    ai_enabled=_bool_value("AI_ENABLED", bool(os.getenv("OPENAI_API_KEY"))),
    ai_auto_start=_bool_value("AI_AUTO_START", True),
    ai_start_personality=os.getenv("AI_START_PERSONALITY", "pijak").strip() or "pijak",
    ai_model=os.getenv("AI_MODEL", "gpt-4o").strip() or "gpt-4o",
    ai_summary_model=os.getenv("AI_SUMMARY_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini",
)
