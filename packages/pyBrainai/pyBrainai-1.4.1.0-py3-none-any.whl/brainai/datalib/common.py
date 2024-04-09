INSTRUCTIONS = """

brainai error:

    missing `{library}`

This feature requires additional dependencies:

    $ pip install brainai[datalib]

"""

NUMPY_INSTRUCTIONS = INSTRUCTIONS.format(library="numpy")


class MissingDependencyError(Exception):
    pass
