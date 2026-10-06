from sly import Lexer


class NeoLexer:
    """
    Lexical analyzer for the Neo language.

    Practice 1:
    Implement this class using SLY's Lexer class so that it
    recognizes the lexical elements of the Neo P1 language.
    """

    def __init__(self):
        raise NotImplementedError(
            "NeoLexer has not been implemented yet."
        )


# ---------------------------------------------------------
# TODO
# ---------------------------------------------------------
#
# Replace the provisional NeoLexer class above with a
# lexical analyzer based on:
#
#     class NeoLexer(Lexer):
#
# Your implementation must define:
#
#   - the tokens required by Neo P1
#   - the literal characters
#   - ignored characters
#   - lexical rules
#   - reserved words
#   - integer constants
#   - comments
#   - line counting
#
# Lexical errors must be reported by raising ValueError.
#
# Example:
#
#     raise ValueError(
#         f"Line {self.lineno}: unrecognized character ..."
#     )
#
# ---------------------------------------------------------