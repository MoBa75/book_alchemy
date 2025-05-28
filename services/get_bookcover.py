import requests
import json

def get_cover_by_isbn(isbn):
    thumbnail = 'static/placeholder_cover.jpg'
    try:
        response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}')
        data = response.json()
        if data.get('totalItems') > 0:
            volume = data['items'][0]['volumeInfo']
            book_cover = volume.get('imageLinks', {}).get('thumbnail', thumbnail)
        else:
            book_cover = thumbnail
    except (requests.exceptions.RequestException, json.decoder.JSONDecodeError,
            IndexError, KeyError, TypeError):
        book_cover = thumbnail
    return book_cover
