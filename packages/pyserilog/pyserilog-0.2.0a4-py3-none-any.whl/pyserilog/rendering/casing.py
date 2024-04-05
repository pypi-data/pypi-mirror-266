class Casing:

    @staticmethod
    def format(value: str, text_format: str | None):
        match text_format:
            case "u":
                return value.upper()
            case "w":
                return value.lower()
            case _:
                return value
