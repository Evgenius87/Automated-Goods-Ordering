from pprint import pprint
from pydantic import BaseModel
from typing import Optional



class GoogleAuthResp(BaseModel):
    at_hash: Optional[str]
    aud: Optional[str]
    azp: Optional[str]
    email: Optional[str]
    email_verified: Optional[bool]
    exp: Optional[int]
    family_name: Optional[str]
    given_name: Optional[str]
    iat: Optional[int]
    iss: Optional[str]
    name: Optional[str]
    nonce: Optional[str]
    picture: Optional[str]
    sub: Optional[str]

    class Config:
        orm_mode = True
        from_attributes = True

a = {'iss': 'https://accounts.google.com', 'azp': '281094189618-bhuu95f4r37sp7crc1tr5lt6ae4g9ksh.apps.googleusercontent.com', 'aud': '281094189618-bhuu95f4r37sp7crc1tr5lt6ae4g9ksh.apps.googleusercontent.com', 'sub': '116316719663018783929', 'email': 'jegermejster@gmail.com', 'email_verified': True, 'at_hash': 'N2ehSg5B2B8PKAlFUR7OLw', 'nonce': 'qisQe09s3TH18gU2KzHn', 'name': 'Євген Плотніков', 'picture': 'https://lh3.googleusercontent.com/a/ACg8ocJ79DozOJPGLPZrpAhWzNdqINxed_E-PRXhTvk5opT9_0VPDw=s96-c', 'given_name': 'Євген', 'family_name': 'Плотніков', 'iat': 1723296481, 'exp': 1723300081}

data = GoogleAuthResp(**a)

pprint(data)
