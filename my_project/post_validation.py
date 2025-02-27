
from fastapi import Request
from typing import List
from typing import Optional

class NewPost:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.post_title: Optional[str] = None
        self.post_date: Optional[str] = None
        self.post_content: Optional[str] = None

    def valid_input(self):
        if not self.post_title or not len(self.post_title) >=3:
            self.errors.append("Please provide a title")
        if not self.post_date or not len(self.post_date) >=9:
            self.errors.append("Please provide a date in format DD/MM/YYYY")
        if not self.post_content or not len(self.post_content) >=15:
            self.errors.append("Please provide valid post content")

        if not self.errors:
            return True
        else: return False

    async def load_data(self):
            form = await self.request.form()
            self.post_title = form.get("post_title")
            self.post_date = form.get("post_date")
            self.post_content = form.get("post_content")
