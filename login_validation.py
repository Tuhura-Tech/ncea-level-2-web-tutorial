from fastapi import Request
from typing import List
from typing import Optional

class NewSignup:
    def __init__(self, request: Request):
      self.request: Request = request
      self.errors: List = []
      self.email: Optional[str] = None
      self.password: Optional[str] = None


    def valid_input(self):
        if not self.email or not len(self.email) >=5:
            self.errors.append("Invalid email address")
        if not self.password or not len(self.password) >= 6:
            self.errors.append("Your password must be at least 5 characters long")
        
        if not self.errors:
            return True
        else: 
            return False

    async def load_data(self):
        form = await self.request.form()
        self.email = form.get("email")
        self.password = form.get("password")