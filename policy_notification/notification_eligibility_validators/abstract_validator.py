from abc import ABC, abstractmethod
from typing import TypeVar, Callable, Union


class AbstractEligibilityValidator(ABC):
    NotificationCollection = TypeVar('NotificationCollection')

    def validate_eligibility(self, notification_collection: NotificationCollection, type_of_notification: str) \
            -> NotificationCollection:
        """
        For given collection return objects that passed validation.
        If notification for given type was not implemented then return whole collection.

        :param notification_collection: Collection of objects to be validated, type depends on implementation can be
        iterable or queryset.
        :param type_of_notification: type of notification.
        :return: Elements of notification_collection that passed validation.
        """
        validation_func = self.get_validation_for_notification_type(type_of_notification)
        if not validation_func:
            return notification_collection
        else:
            return validation_func(notification_collection)

    @abstractmethod
    def get_validation_for_notification_type(self, notification_type: str) \
            -> Union[Callable[[NotificationCollection], NotificationCollection], None]:
        raise NotImplementedError("Has to be implemented")
