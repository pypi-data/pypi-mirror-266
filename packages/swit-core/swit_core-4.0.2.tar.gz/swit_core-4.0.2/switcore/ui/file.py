from enum import Enum
from typing import Literal

from switcore.pydantic_base_model import SwitBaseModel
from switcore.ui.element_components import StaticAction


class FileTypes(str, Enum):
    image = "image"
    video = "video"
    document = "document"
    pdf = "pdf"
    presentation = "presentation"
    spreadsheet = "spreadsheet"
    archive = "archive"
    psd = "psd"
    ai = "ai"
    other = "other"


def get_file_type(file_extension: str) -> FileTypes:
    if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
        file_type = FileTypes.image
    elif file_extension in ['mp4', 'avi', 'mov']:
        file_type = FileTypes.video
    elif file_extension in ['doc', 'docx', 'txt']:
        file_type = FileTypes.document
    elif file_extension == 'pdf':
        file_type = FileTypes.pdf
    elif file_extension in ['ppt', 'pptx']:
        file_type = FileTypes.presentation
    elif file_extension == 'xls':
        file_type = FileTypes.spreadsheet
    elif file_extension in ['zip', 'rar']:
        file_type = FileTypes.archive
    elif file_extension == 'psd':
        file_type = FileTypes.psd
    elif file_extension == 'ai':
        file_type = FileTypes.ai
    else:
        file_type = FileTypes.other

    return file_type


class File(SwitBaseModel):
    type: Literal['file'] = 'file'
    file_type: FileTypes
    file_size: int
    file_name: str
    action_id: str | None = None
    static_action: StaticAction | None = None
