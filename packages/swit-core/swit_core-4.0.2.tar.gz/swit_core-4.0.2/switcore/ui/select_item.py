from switcore.pydantic_base_model import SwitBaseModel
from switcore.ui.element_components import StaticAction


class SelectItem(SwitBaseModel):
    """
        A reusable object that represents an item that can be selected.
        It is used across various components like View, AttachmentView, Tabs, and Select.
    """
    label: str
    action_id: str
    static_action: StaticAction | None = None
