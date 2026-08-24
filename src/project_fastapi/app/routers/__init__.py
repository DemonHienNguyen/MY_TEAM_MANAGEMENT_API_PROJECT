from .auth import router as AuRouter
from .user import router as UsRouter
from .project import router as ProRouter
from .project_member import router as ProMeRouter
from .task import router as TasRouter

__all__ = ["AuRouter", "UsRouter", "ProRouter", "ProMeRouter", "TasRouter"]
