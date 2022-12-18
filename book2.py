from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from fastapi import FastAPI, HTTPException

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
async def read_all_books(books_to_return: Optional[int] = None) -> [Book]:
    if len(Books) == 0:
        Books.extend(create_book_no_api())

    if books_to_return and len(Books) >= books_to_return > 0:
        new_books = Books[:books_to_return].copy()
        return new_books

    return Books


@app.get("/book/{book_id}")
async def read_book(book_id: UUID):
    for book in Books:
        if book.id == book_id:
            return book
    raise_item_not_found_exception()


@app.post("/")
async def create_book(book: Book) -> [Book]:
    Books.append(book)
    return Books


@app.put("/{book_id}")
async def update_book(book_id: UUID, book: Book) -> Book:
    for index, old_book in enumerate(Books):
        if old_book.id == book_id:
            Books[index] = book
            return Books[index]
    raise_item_not_found_exception()


@app.delete("/{book_id}")
async def delete_book(book_id: UUID) -> Book:
    for index, old_book in enumerate(Books):
        if old_book.id == book_id:
            deleted_book = Books.pop(index)
            return deleted_book
    raise_item_not_found_exception()


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


def raise_item_not_found_exception():
    raise HTTPException(status_code=404, detail="book_id is not existed")
