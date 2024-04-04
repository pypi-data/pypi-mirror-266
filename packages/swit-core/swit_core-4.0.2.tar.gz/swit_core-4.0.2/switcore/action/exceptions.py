from typing import Any, Optional, Dict

from fastapi import HTTPException
from starlette import status


class UndefinedSubmitAction(HTTPException):

    def __init__(self, detail: Any = None, headers: Optional[Dict[str, str]] = None) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, headers=headers)
