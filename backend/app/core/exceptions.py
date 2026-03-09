from fastapi import HTTPException, status


class DocumentNotFound(HTTPException):
    def __init__(self, document_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found",
        )


class DocumentNotReady(HTTPException):
    def __init__(self, document_id: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Document '{document_id}' is still processing",
        )


class StorageError(HTTPException):
    def __init__(self, detail: str = "Storage operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class UnauthorizedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
