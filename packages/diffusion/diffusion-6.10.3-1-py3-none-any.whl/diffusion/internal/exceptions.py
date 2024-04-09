""" Base exceptions module. """
import typing


class DiffusionError(Exception):
    """ Base exception class for all Diffusion errors. """
    default_description = "{message}"

    def __init__(self, message: typing.Optional[str] = "", *args, **kwargs):
        super().__init__(self.description(message=message, **kwargs), *args)

    @classmethod
    def description(cls, message: typing.Optional[str] = "", **kwargs):
        return message or cls.default_description.format(message=message, **kwargs)
