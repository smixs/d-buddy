from config.config import config

from .access_control import AccessControlService

access_control_service = AccessControlService(
    whitelist_file=config.UNLIMITED_USERS_FILE,
    initial_users=config.UNLIMITED_USERS,
)

__all__ = ["AccessControlService", "access_control_service"]