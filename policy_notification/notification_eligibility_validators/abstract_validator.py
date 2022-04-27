from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TypeVar, Callable, Union

from django.db.models import Prefetch

from policy_notification.models import IndicationOfPolicyNotifications, IndicationOfPolicyNotificationsDetails
from policy_notification.notification_eligibility_validators.dataclasses import IneligibleObject


class AbstractEligibilityValidator(ABC):
    NotificationCollection = TypeVar('NotificationCollection')
    _DEFAULT_COLLECTION = []

    @property
    def valid_collection(self):
        if self._eligible_collection is None:
            raise ValueError(
                "Collection was not yet validated. Call validate_notification_eligibility before "
                "accessing valid_collection."
            )
        else:
            return self._eligible_collection

    @property
    def invalid_collection(self):
        if self._ineligible_collection is None:
            raise ValueError(
                "Collection was not yet validated. Call validate_notification_eligibility before "
                "accessing invalid_collection."
            )
        else:
            self._assert_invalid_collection()
            return self._ineligible_collection

    def __init__(self, notification_collection: NotificationCollection, type_of_notification: str):
        """

        :param notification_collection: Collection of objects to be validated, type depends on implementation can be
        iterable or queryset.
        :param type_of_notification: type of notification.
        """
        self.notification_collection = notification_collection
        self.type_of_notification = type_of_notification
        self._eligible_collection = self._DEFAULT_COLLECTION.copy()
        self._ineligible_collection = self._DEFAULT_COLLECTION.copy()

    def validate_notification_eligibility(self):
        """
        For given collection return objects that passed validation.
        If notification for given type was not implemented then return whole collection.
        """
        self._eligible_collection = self._DEFAULT_COLLECTION.copy()
        self._ineligible_collection = self._DEFAULT_COLLECTION.copy()
        notification_collection, type_of_notification = self.notification_collection, self.type_of_notification
        base_validated = self.__base_validation(notification_collection, type_of_notification)
        validated = self.__notification_type_validation(base_validated, type_of_notification)
        self._eligible_collection = validated
        self._handle_not_valid_entries()

    @abstractmethod
    def _get_validation_for_notification_type(self, notification_type: str) \
            -> Union[Callable[[NotificationCollection], NotificationCollection], None]:
        """
        For given notification type returns function that'll validate NotificationCollection (e.g. Queryset of policies)
        in context of specific notification type.
        :param notification_type: Type of notification
        :return: Function that takes notification collection as argument and returns entries from this collection.
        """
        raise NotImplementedError("Has to be implemented")

    @abstractmethod
    def _base_eligibility_validation(self, notification_collection: NotificationCollection, type_of_notification: str) \
            -> NotificationCollection:
        """
        Generic validation which is applicable regardless of the specific type of notification.
        E.g. Check if family allows notification or if notification was already sent.
        :param notification_collection: Input from validate_notification_eligibility
        :return Valid entries from policies
        """
        raise NotImplementedError("Has to be implemented")

    @abstractmethod
    def _handle_not_valid_entries(self):
        """
        Responsible for handling not valid entries from NotificationCollection.
        :param notification_collection: Entries form validate_notification_eligibility that didn't pass validation.
        :param type_of_notification:
        :return: None
        """
        raise NotImplementedError("Has to be implemented")

    def _add_non_eligible_due_to_notification_type_validation(self, collection):
        raise NotImplementedError("Hast to be implemented")

    def _add_non_eligible(self, collection, reason):
        raise NotImplementedError("Hast to be implemented")

    def _assert_invalid_collection(self):
        pass

    def _add_non_eligible_due_to_base_validation(self, not_valid):
        raise NotImplementedError()

    def _substract_collections(self, collection_from, collection):
        """
        Return collection_from without elements from collection
        :param collection_from: All entries
        :param collection: Valid entries
        :return: Invalid entries
        """
        raise NotImplementedError()

    def __base_validation(self, notification_collection, type_of_notification):
        base_validated = self._base_eligibility_validation(notification_collection, type_of_notification)
        not_valid = self._substract_collections(notification_collection, base_validated)
        self._add_non_eligible_due_to_base_validation(not_valid)
        return base_validated

    def __notification_type_validation(self, notification_collection, type_of_notification):
        validation_func = self._get_validation_for_notification_type(type_of_notification)
        valid = validation_func(notification_collection) if validation_func else notification_collection
        not_valid = self._substract_collections(notification_collection, valid)
        self._add_non_eligible_due_to_notification_type_validation(not_valid)

        return valid


class QuerysetEligibilityValidationMixin:
    BASE_VALIDATION_REJECTION_REASON = None
    TYPE_VALIDATION_REJECTION_REASON = None
    TYPE_VALIDATION_REJECTION_DETAILS = None

    def _add_non_eligible_due_to_base_validation(self, not_valid):
        self._add_non_eligible(not_valid, self.BASE_VALIDATION_REJECTION_REASON)

    def _add_non_eligible_due_to_notification_type_validation(self, not_valid):
        self._add_non_eligible(not_valid, self.TYPE_VALIDATION_REJECTION_REASON, self.TYPE_VALIDATION_REJECTION_DETAILS)

    def _substract_collections(self, collection_from, collection):
        x = collection.values('id')
        return collection_from.exclude(id__in=x).all()

    def _add_non_eligible(self, collection, reason, detail=None):
        futures = []
        with ThreadPoolExecutor(max_workers=100) as executor:
            for element in collection:
                futures.append(executor.submit(self.__create_ineligible, element, reason, detail))

            completed = as_completed(futures)
            self._ineligible_collection.extend([f.result() for f in completed])

    def __create_ineligible(self, ineligible, reason, detail):
        return IneligibleObject(policy=ineligible, reason=reason, details=detail)
