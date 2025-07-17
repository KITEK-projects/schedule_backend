from ninja import Field, Schema


class CertCreate(Schema):
    first_name: str = Field(..., max_length=150)
    last_name: str = Field(..., max_length=150)
    group: str = Field(..., max_length=16)
    requested_by: str = Field(..., max_length=150)
    quantity: int = Field(..., gt=1, le=5)


class CertRetrieve(Schema):
    first_name: str = Field(..., max_length=150)
    last_name: str = Field(..., max_length=150)
    group: str = Field(..., max_length=16)
    requested_by: str = Field(..., max_length=150)
    quantity: int
    status: str
