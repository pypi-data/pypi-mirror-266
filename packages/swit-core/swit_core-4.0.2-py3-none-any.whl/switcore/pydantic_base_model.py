from pydantic import BaseModel


class SwitBaseModel(BaseModel):
    class Config:
        use_enum_values = True
