from typing import Literal

from switcore.pydantic_base_model import SwitBaseModel
from switcore.ui.Icon import Icon
from switcore.ui.button import Button


class IntegratedService(SwitBaseModel):
    icon: Icon


class SignInPage(SwitBaseModel):
    type: Literal['sign_in_page'] = 'sign_in_page'
    id: str | None = None
    integrated_service: IntegratedService
    title: str
    description: str
    button: Button
