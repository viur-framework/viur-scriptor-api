from .print import print
from .alert import alert
from .raw_html import raw_html
from .open_file import _open_file_dialog
from .save_file import _save_file_dialog
from .select import select
from .confirm import confirm
from .text import text
from .number import number
from .date import date
from .table import table
from .diff import show_diff
from .multiple import multiple


class Dialog:
    print = print
    alert = alert
    raw_html = raw_html
    _open_file_dialog = _open_file_dialog
    _save_file_dialog = _save_file_dialog
    select = select
    confirm = confirm
    text = text
    number = number
    date = date
    table = table
    diff = diff
    multiple = multiple
