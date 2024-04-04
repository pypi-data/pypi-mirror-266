# whattoread/cli.py
"""Show New York Times nonfiction bestsellers of the week using cli."""

import os

import httpx

DOMAIN = 'https://api.nytimes.com'
CATEGORY = 'combined-print-and-e-book-nonfiction'


def main() -> str:
    """Provide top 15 nonfiction bestsellers of the week."""
    if not (api_key := os.getenv('NEW_YORK_TIMES_API_KEY')):
        return 'Please set NEW_YORK_TIMES_API_KEY environment variable.'

    url = f'{DOMAIN}/svc/books/v3/lists/current/{CATEGORY}?api-key={api_key}'
    resp = httpx.get(url)
    books_info = resp.json()['results']['books']

    book_titles = []
    for i, book_info in enumerate(books_info, start=1):
        book_title = f'{i}. {book_info["title"].title()}'
        book_titles.append(book_title)

    return '\n'.join(book_titles)
