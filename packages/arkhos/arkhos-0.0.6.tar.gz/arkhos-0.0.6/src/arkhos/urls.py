from collections import OrderedDict

registered_urls = OrderedDict()

"""
['/books', books_list_handler,],
['/books/create/', books_create_handler,],
['/books/{book_number}/', book_view_handler],
"""


def register_urls(url_handlers, path=None):
    for path, handler in url_handlers:
        path_regex = path_to_regex(path)
