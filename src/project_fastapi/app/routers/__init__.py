from .auth import router as AuRouter
from .project import router as ProRouter
from .project_member import router as ProMeRouter
from .task import router as TasRouter
from .user import router as UsRouter

__all__ = ["AuRouter", "ProMeRouter", "ProRouter", "TasRouter", "UsRouter"]
