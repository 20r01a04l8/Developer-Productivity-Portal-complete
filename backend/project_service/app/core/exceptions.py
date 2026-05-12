"""
Domain exceptions for Project Service.

Architecture rule:
    Services raise these exceptions — they never raise HTTPException.
    The exception handler in middleware maps these to HTTP status codes.
    This keeps HTTP concerns completely out of the business logic layer.
"""


class ProjectServiceError(Exception):
    """Base class — catch this to handle any project domain error."""
    pass


class ProjectNotFoundError(ProjectServiceError):
    def __init__(self, project_id: str):
        self.project_id = project_id
        super().__init__(f"Project '{project_id}' not found.")


class ProjectAlreadyExistsError(ProjectServiceError):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"A project named '{name}' already exists.")


class InvalidProjectOperationError(ProjectServiceError):
    """Raised when a business rule is violated."""
    pass
