import json
from pathlib import Path
from typing import Iterable, List, Set

try:
    from loguru import logger
except ImportError:  # pragma: no cover
    import logging
    logger = logging.getLogger(__name__)


class AccessControlService:
    """Manage a whitelist of users with unlimited access."""

    def __init__(
        self,
        whitelist_file: str = "data/unlimited_users.json",
        initial_users: Iterable[str] | None = None,
    ) -> None:
        self.whitelist_file = Path(whitelist_file)
        self.whitelist_file.parent.mkdir(parents=True, exist_ok=True)
        self._users: Set[str] = set()

        stored_users = self._load_users()
        if stored_users:
            self._users = stored_users

        if initial_users:
            normalized = {str(user).strip() for user in initial_users if str(user).strip()}
            if normalized - self._users:
                self._users.update(normalized)
                self._save_users(self._users)
        elif not stored_users:
            # Ensure file exists even if there are no users yet
            self._save_users(self._users)

    def _load_users(self) -> Set[str]:
        if not self.whitelist_file.exists():
            return set()

        try:
            with open(self.whitelist_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {str(user).strip() for user in data if str(user).strip()}
        except Exception as exc:
            logger.error(f"Error loading unlimited users: {exc}")
            return set()

    def _save_users(self, users: Set[str]) -> None:
        try:
            with open(self.whitelist_file, "w", encoding="utf-8") as f:
                json.dump(sorted(users), f, ensure_ascii=False, indent=2)
        except Exception as exc:
            logger.error(f"Error saving unlimited users: {exc}")

    def is_unlimited(self, user_id: str | int) -> bool:
        return str(user_id) in self._users

    def add_user(self, user_id: str | int) -> bool:
        normalized = str(user_id).strip()
        if not normalized:
            return False

        if normalized in self._users:
            return False

        self._users.add(normalized)
        self._save_users(self._users)
        logger.info(f"Added unlimited user {normalized}")
        return True

    def remove_user(self, user_id: str | int) -> bool:
        normalized = str(user_id).strip()
        if normalized not in self._users:
            return False

        self._users.remove(normalized)
        self._save_users(self._users)
        logger.info(f"Removed unlimited user {normalized}")
        return True

    def list_users(self) -> List[str]:
        return sorted(self._users)
