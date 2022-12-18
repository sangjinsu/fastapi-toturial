from typing import Optional

from fastapi import FastAPI, HTTPException
from enum import Enum

app = FastAPI()


class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author


books: dict[str, Book] = dict(
    book_1=Book('Title1', 'Author1'),
    book_2=Book('Title2', 'Author2'),
    book_3=Book('Title3', 'Author3'),
)


class DirectionName(str, Enum):
    north = 'North'
    south = 'South'
    east = 'East'
    west = 'West'


async def is_exist_book_name(book_name):
    if books.get(book_name) is None:
        raise HTTPException(status_code=404, detail="book_name is not existed")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/books")
async def read_all_books(skip_book: Optional[str] = None):
    if skip_book:
        books_copy = books.copy()
        del books_copy[skip_book]
        return books_copy
    return books


@app.get("/books/{book_name}")
async def get_book(book_name: str) -> Book:
    return books.get(book_name)


@app.get("/directions/{direction}")
async def get_directions(direction: DirectionName):
    sub = {
        DirectionName.north: 'Up',
        DirectionName.south: 'Down',
        DirectionName.east: 'Left',
        DirectionName.west: 'Right'
    }
    return {"Direction": direction, "sub": sub[direction]}


@app.post("/")
async def create_book(book_title: str, book_author: str) -> Book:
    current_book_id = 0
    if len(books) > 0:
        for book in books:
            idx = int(book.split('_')[-1])
            if idx > current_book_id:
                current_book_id = idx

    books[f'book_{current_book_id + 1}'] = Book(book_title, book_author)
    return books[f'book_{current_book_id + 1}']


@app.put("/{book_name}")
async def update_book(book_name: str, book_title: str, book_author: str) -> Book:
    await is_exist_book_name(book_name)
    books[book_name] = Book(book_title, book_author)
    return books.get(book_name)


@app.delete("/{book_name}")
async def delete_book(book_name: str) -> Book:
    await is_exist_book_name(book_name)
    deleted_book = books[book_name]
    del books[book_name]
    return deleted_book


@app.get("/assignment")
async def read_book_assignment(book_name: str) -> Book:
    return books.get(book_name)


@app.delete("/assignment")
async def delete_book_assignment(book_name: str) -> Book:
    await is_exist_book_name(book_name)
    deleted_book = books[book_name]
    del books[book_name]
    return deleted_book
