from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from fastapi import FastAPI

app = FastAPI()


class Book(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: str = Field(title="Description of the Book", min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=101)

    class Config:
        schema_extra = {
            "example": {
                "id": "e5486170-3023-4273-acc7-02212987c97a",
                "title": "Title2",
                "author": "Author2",
                "description": "description2",
                "rating": 60
            }

        }


Books: [Book] = []


@app.get("/")
async def read_all_books() -> [Book]:
    if len(Books) == 0:
        Books.append(create_book_no_api())
    return Books


@app.post("/")
async def create_book(book: Book) -> [Book]:
    Books.append(book)
    return Books


def create_book_no_api() -> [Book]:
    book_1 = Book(id=uuid4(),
                  title="Title1",
                  author="Author1",
                  description="description1",
                  rating=60)
    book_2 = Book(id=uuid4(),
                  title="Title2",
                  author="Author2",
                  description="description2",
                  rating=60)
    return [book_1, book_2]
