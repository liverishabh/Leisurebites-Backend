import enum


class UserType(str, enum.Enum):
    customer = "customer"
    supplier = "supplier"
    admin = "admin"


class LoginType(str, enum.Enum):
    email_id = "email_id"
    phone_no = "phone_no"
