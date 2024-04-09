from typing import Text
from kolibri.logger import get_logger

logger=get_logger(__name__)

class MissingArgumentError(ValueError):
    """Raised when a function is called and not all parameters can be
    filled from the context / config.

    Attributes:
        document -- explanation of which parameter is missing
    """

    def __init__(self, document, message):
        self.document = document
        logger.error(message)

    def __str__(self):
        return self.document

class ConfigError(Exception):
    """Any configuration error."""

    def __init__(self, message):
        super(ConfigError, self).__init__()
        self.message = message

    def __str__(self):
        return repr(self.message)


class UnsupportedLanguageError(Exception):
    """Raised when a component is created but the language is not supported.

    Attributes:
        component -- component name
        language -- language that component doesn't support
    """

    def __init__(self, component, language, message):
        self.component = component
        self.language = language

        logger.error(message)


    def __str__(self):
        return "component {} does not support language {}".format(
            self.component, self.language
        )


class InvalidConfigError(ValueError):
    """Raised if an invalid configuration is encountered."""

    def __init__(self, message):
        super(InvalidConfigError, self).__init__(message)

        logger.error(message)


class InvalidProjectError(Exception):
    """Raised when a model_type failed to load.

    Attributes:
        document -- explanation of why the model_type is invalid
    """

    def __init__(self, message, document=None):
        self.document = document
        logger.error(message)

    def __str__(self):
        return self.document


class UnsupportedModelError(Exception):
    """Raised when a model_type is too old to be loaded.

    Attributes:
        document -- explanation of why the model_type is invalid
    """

    def __init__(self, document, message):
        self.document = document
        logger.error(message)
    def __str__(self):
        return self.document

class AxisLabelsMismatchError(ValueError):
    """Raised when a pair of axis labels tuples do not match."""
    def __init__(self, message):
        Exception.__init__(self, message)
        logger.error(message)

class ConfigurationError(Exception):
    """Error raised when a configuration value is requested but not set."""
    def __init__(self, message):
        Exception.__init__(self, message)
        logger.error(message)

class MissingInputFiles(Exception):
    """Exception raised by a converter when input files are not found.

    Parameters
    ----------
    message : str
        The error message to be associated with this exception.
    filenames : list
        A list of filenames that were not found.

    """
    def __init__(self, message, filenames):
        self.filenames = filenames
        super(MissingInputFiles, self).__init__(message, filenames)
        logger.error(message)

class NeedURLPrefix(Exception):
    """Raised when a URL is not provided for a file."""
    def __init__(self, message):
        Exception.__init__(self, message)
        logger.error(message)

class MetricException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

        logger.error(message)


class InvalidDataError(Exception):
    """Error to raise when data is not valid."""

    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return (
            'The provided data does not match the metadata:\n' +
            '\n\n'.join(map(str, self.errors))
        )


class NotFittedError(Exception):
    """Error to raise when sample is called and the model is not fitted."""


class ConstraintsNotMetError(ValueError):
    """Exception raised when the given data is not valid for the constraints."""

    def __init__(self, message=''):
        self.message = message
        super().__init__(self.message)


class SynthesizerInputError(Exception):
    """Error to raise when a bad input is provided to a ``Synthesizer``."""


class SamplingError(Exception):
    """Error to raise when sampling gets a bad input or can't be used."""


class NonParametricError(Exception):
    """Exception to indicate that a model is not parametric."""

"""Data processing exceptions."""


class NotFittedError(Exception):
    """Error to raise when ``DataProcessor`` is used before fitting."""


class InvalidConstraintsError(Exception):
    """Error to raise when constraints are not valid."""

    def __init__(self, errors):
        errors = errors if isinstance(errors, list) else [errors]
        self.errors = errors

    def __str__(self):
        return (
            'The provided constraint is invalid:\n' +
            '\n\n'.join(map(str, self.errors))
        )


"""Constraint Exceptions."""


class MissingConstraintColumnError(Exception):
    """Error used when constraint is provided a table with missing columns."""

    def __init__(self, missing_columns):
        self.missing_columns = missing_columns


class AggregateConstraintsError(Exception):
    """Error used to represent a list of constraint errors."""

    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return '\n' + '\n\n'.join(map(str, self.errors))


class InvalidFunctionError(Exception):
    """Error used when an invalid function is utilized."""


class FunctionError(Exception):
    """Error used when an a function produces an unexpected error."""


class ConstraintMetadataError(Exception):
    """Error to raise when Metadata is not valid."""


"""Metadata Exceptions."""


class InvalidMetadataError(Exception):
    """Error to raise when Metadata is not valid."""


class MetadataNotFittedError(InvalidMetadataError):
    """Error to raise when Metadata is used before fitting."""
