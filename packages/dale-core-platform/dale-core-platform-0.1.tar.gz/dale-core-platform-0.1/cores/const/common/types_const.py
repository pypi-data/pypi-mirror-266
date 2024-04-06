from ..__const import Const


class StringFormatConst(Const):
    REMOVE_ALL_CHARACTERS_EXCEPT_TEXT = r"[\n\t\s]+"
    FORMAT_AB_123_PATTERN = r'(\D+)(\d+)'
    FORMAT_AB_123_REPL = r'\1-\2'
