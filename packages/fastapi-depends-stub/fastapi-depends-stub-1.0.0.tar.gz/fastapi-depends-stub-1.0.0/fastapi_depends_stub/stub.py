from typing import (
    Any,
    Callable,
)


class Stub:
    """Prevent FastAPI from digging into real dependencies attributes detecting them as request data."""

    def __init__(
        self,
        dependency: Callable,
        **kwargs: Any,
    ) -> None:
        """
        Initialize class object.

        :param dependency: dependency
        :type dependency: typing.Callable
        :param kwargs: arbitrary keyword arguments
        :type kwargs: typing.Any
        """

        self._dependency = dependency
        self._kwargs = kwargs

    def __call__(
        self,
    ) -> None:
        """
        Dummy __call__ method.

        :return: None
        :rtype: NoneType

        :raises NotImplementedError: you're not supposed to call Stub object
        """

        raise NotImplementedError

    def __eq__(
        self,
        other: Any,
    ) -> bool:
        """
        Check instances equality.

        :param other: object
        :type other: typing.Any

        :return: True if objects are equal, False otherwise
        :rtype: bool
        """

        if isinstance(other, Stub):
            return self._dependency == other._dependency and self._kwargs == other._kwargs  # noqa: WPS437

        if not self._kwargs:
            return self._dependency == other

        return False

    def __hash__(
        self,
    ) -> int:
        """
        Get hash value.

        :return: hash
        :rtype: int
        """

        if not self._kwargs:
            return hash(self._dependency)

        return hash(
            (
                self._dependency,
                *self._kwargs.items(),
            ),
        )
