from pydantic import BaseModel,ConfigDict

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    slug:str

    model_config = ConfigDict(from_attributes =True)
