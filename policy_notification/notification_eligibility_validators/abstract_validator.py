from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TypeVar, Callable, Union, Iterable

from django.db.models import Prefetch

from policy_notification.models import IndicationOfPolicyNotifications, IndicationOfPolicyNotificationsDetails
from policy_notification.notification_eligibility_validators.dataclasses import IneligibleObject, ValidationDefinition


class AbstractEligibilityValidator(ABC):
    NotificationCollection = TypeVar('NotificationCollection')
    _DEFAULT_COLLECTION = []

    @property
    def valid_collection(self):
        return self._eligible_collection

    @property
    def invalid_collection(self):
        return self._ineligible_collection

    def __init__(self, notification_collection: NotificationCollection, type_of_notification: str):
        """

        :param notification_collection: Collection of objects to be validated, type depends on implementation can be
        iterable or queryset.
        :param type_of_notification: type of notification.
        """
        self.notification_collection = notification_collection
        self.type_of_notification = type_of_notification
        self._eligible_collection, self._ineligible_collection = None, None
        self.reset_collections()

    def validate_notification_eligibility(self):
        """
        For given collection return objects that passed validation.
        If notification for given type was not implemented then return whole collection.
        """
        validated = self.notification_collection
        for validation in self.registered_validations:
            validated = self._perform_validation(validated, validation)
        self._eligible_collection = validated
        self._handle_not_valid_entries()

    @property
    @abstractmethod
    def registered_validations(self) -> Iterable[ValidationDefinition]:
        ...

    def _perform_validation(self, notification_collection, validation_definition: ValidationDefinition):
        valid = validation_definition.validation_function(notification_collection, self.type_of_notification)
        not_valid = self._substract_collections(notification_collection, valid)
        self._collect_not_valid_information(not_valid, validation_definition)
        return valid

    @abstractmethod
    def _handle_not_valid_entries(self):
        """
        Responsible for handling not valid entries from NotificationCollection.
        :param notification_collection: Entries form validate_notification_eligibility that didn't pass validation.
        :param type_of_notification:
        :return: None
        """
        raise NotImplementedError("Has to be implemented")

    def _collect_not_valid_information(self, collection, validation_definition: ValidationDefinition):
        self._ineligible_collection.extend([
            self._create_ineligible(element, validation_definition) for element in collection
        ])

    def _create_ineligible(self, ineligible, validation_definition: ValidationDefinition):
        raise NotImplementedError()

    def _substract_collections(self, collection_from, collection):
        """
        Return collection_from without elements from collection
        :param collection_from: All entries
        :param collection: Valid entries
        :return: Invalid entries
        """
        raise NotImplementedError()

    def reset_collections(self):
        self._eligible_collection = self._DEFAULT_COLLECTION.copy()
        self._ineligible_collection = self._DEFAULT_COLLECTION.copy()


class QuerysetEligibilityValidationMixin:
    def _substract_collections(self, collection_from, collection):
        x = collection.values('id')
        return collection_from.exclude(id__in=x).all()
