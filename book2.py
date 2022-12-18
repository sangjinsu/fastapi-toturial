from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

from fastapi import FastAPI, HTTPException, Request, status, Form, Header
from secrets import compare_digest

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


class NegativeNumberException(Exception):
    def __init__(self, books_to_return):
        self.books_to_return = books_to_return


class BookNoRating(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: str = Field(title="Description of the Book", min_length=1, max_length=100)


@app.exception_handler(NegativeNumberException)
async def negative_number_exception_handler(request: Request, exception: NegativeNumberException):
    return JSONResponse(
        status_code=418,
        content={"message": exception.books_to_return}
    )


@app.post("/books/login")
async def book_login(book_id: int, username: str = Header(None), password: str = Header(None)):
    if compare_digest(username, "FastAPIUser") and compare_digest(password, "test1234!"):
        return Books[book_id]
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')


@app.get("/header")
async def read_header(random_header: Optional[str] = Header(None)):
    return {"Random-Header": random_header}


@app.get("/")
async def read_all_books(books_to_return: Optional[int] = None) -> [Book]:
    if books_to_return and books_to_return < 0:
        raise NegativeNumberException(books_to_return=books_to_return)

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


@app.get("/book/rating/{book_id}", response_model=BookNoRating)
async def read_book_no_rating(book_id: UUID):
    for book in Books:
        if book.id == book_id:
            return book
    raise_item_not_found_exception()


@app.post("/", status_code=status.HTTP_201_CREATED)
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
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="book_id is not existed")
