from pydantic import BaseModel, ConfigDict

class AddressBase(BaseModel):
    address: str

class AddressCreate(AddressBase):
    pass                         # user_uid comes from the token, not the payload

class AddressUpdate(AddressBase):
    pass

class Address(AddressBase):
    id: int
    user_uid: str

    model_config = ConfigDict(from_attributes=True)
'''    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        orm_mode = True
        # This allows the model to work with ORM objects directly
        # and use field names as aliases.
        # It also allows population by field name, which is useful
        # when using the model with data that may not match the field names exactly.'''