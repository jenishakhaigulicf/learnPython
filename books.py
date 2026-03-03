from fastapi import FastAPI, Body, Path, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from starlette import status

app = FastAPI()

BOOKS = []


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

class BookRequest(BaseModel):
    id: Optional[int] = Field(description='ID is not needed on create', default=None)
    title: str = Field(min_length = 3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating:int = Field(gt=0, lt=6)
    published_date: int 

    model_config = {
        "json_schema_extra": {
            "example":{
                "title": "A new book",
                "author": "learning fast api",
                "description": "A new description of a book",
                "rating": 5,
                "published_date": 2011
            }
        }
    }


BOOKS = [
    Book(
        1,
        "Atomic Habits",
        "James Clear",
        "A book about building good habits and breaking bad ones",
        5,
        2000
    ),
    Book(
        2, "Deep Work", "Cal Newport", "Focus and productivity in a distracted world", 5, 2000
    ),
    Book(
        3,
        "Clean Code",
        "Robert C. Martin",
        "A handbook of agile software craftsmanship",
        5, 
        2000
    ),

    Book(4, "The Alchemist", "Paulo Coelho", "A story about following your dreams", 4, 200),
    Book(
        5,
        "Thinking, Fast and Slow",
        "Daniel Kahneman",
        "Insights into how humans think and make decisions",
        4, 2000
    ),
]


@app.get("/books", status_code=status.HTTP_200_OK)
async def get_books():
    return BOOKS

@app.get('/books/{book_id}', status_code=status.HTTP_200_OK)
async def get_book(book_id:int = Path(gt=0)): 
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code = 404, detail='Item not found')

@app.get('/books/', status_code=status.HTTP_200_OK)
async def get_book_by_rating(rating:int = Query(gt=0, lt=6)): 
    new_book = []
    for book in BOOKS:
        if book.rating == rating:
            new_book.append(book)
    return new_book

@app.get('/books/published_date/', status_code=status.HTTP_200_OK)
async def get_book_by_published_date(published_date: int):
    filtered_books= []
    for book in BOOKS:
        if book.published_date == published_date:
            filtered_books.append(book)
    return filtered_books


@app.post('/books/create', status_code=status.HTTP_201_CREATED)
async def create_book(book_request=Body()):
    BOOKS.append(book_request)

@app.post('/books/create_book_with_validation', status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))
    return new_book

def find_book_id(book:Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id +1 
    # if len(BOOKS) > 0:
    #     book.id = BOOKS[-1].id + 1
    # else:
    #     book.id = 1
    return book


@app.put('/books/update',status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book_request: BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if book_request.id == BOOKS[i].id:
            BOOKS[i] = book_request
            book_changed = true
            return BOOKS
    if not book_changed: raise HTTPException(status_code=404, detail='item not found ')

@app.delete('/books/delete/{book_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id:int = Path(gt=0)):
    book_changed= False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            book_changed = True
            return BOOKS.pop(i)
    if not book_changed: raise HTTPException(status_code=404,detail ='item not found')
            
