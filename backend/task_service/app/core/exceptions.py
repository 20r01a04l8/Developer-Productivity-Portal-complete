"""
Domain exceptions for Task Service.
"""


class TaskServiceError(Exception):
    """Base class — catch this to handle any task domain error."""
    pass


class TaskNotFoundError(TaskServiceError):
    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task '{task_id}' not found.")


class InvalidTaskOperationError(TaskServiceError):
    """Raised when a business rule is violated."""
    pass


class ProjectNotAccessibleError(TaskServiceError):
    """Raised when the referenced project_id cannot be verified."""
    def __init__(self, project_id: str):
        super().__init__(f"Project '{project_id}' is not accessible.")
