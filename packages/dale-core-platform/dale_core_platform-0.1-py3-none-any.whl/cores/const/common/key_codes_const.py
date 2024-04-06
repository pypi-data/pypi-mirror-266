from ..__const import Const


class KeycodeConst(Const):
    # Reference: https://learn.microsoft.com/en-us/dotnet/api/android.views.keycode?view=xamarin-android-sdk-13
    key = {
        '0': 7,
        '1': 8,
        '2': 9,
        '3': 10,
        '4': 11,
        '5': 12,
        '6': 13,
        '7': 14,
        '8': 15,
        '9': 16,
        '@': 77,
        'A': 29,
        'B': 30,
        'C': 31,
        'D': 32,
        'E': 33,
        'F': 34,
        'G': 35,
        'H': 36,
        'I': 37,
        'J': 38,
        'K': 39,
        'L': 40,
        'M': 41,
        'N': 42,
        'O': 43,
        'P': 44,
        'Q': 45,
        'R': 46,
        'S': 47,
        'T': 48,
        'U': 49,
        'V': 50,
        'W': 51,
        'X': 52,
        'Y': 53,
        'Z': 54,
        ' ': 62,
        # Function key
        'COPY': 278,
        'PASTE': 279,
        'CUT': 277,
        'ENTER': 66,
        'TAB': 61,
    }

    class FunctionNameConst(Const):
        COPY = "COPY"
        PASTE = "PASTE"
        CUT = "CUT"
        ENTER = "ENTER"
        TAB = "TAB"
