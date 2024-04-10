# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import abc
from typing import Collection, NamedTuple, Optional, Set

from dyff.schema.platform import (
    Analysis,
    Audit,
    Dataset,
    DataSource,
    Evaluation,
    InferenceService,
    InferenceSession,
    Measurement,
    Method,
    Model,
    Module,
    Report,
    SafetyCase,
)
from dyff.schema.requests import (
    AnalysisQueryRequest,
    AuditQueryRequest,
    DatasetQueryRequest,
    EvaluationQueryRequest,
    InferenceServiceQueryRequest,
    InferenceSessionQueryRequest,
    MeasurementQueryRequest,
    MethodQueryRequest,
    ModelQueryRequest,
    ModuleQueryRequest,
    ReportQueryRequest,
    SafetyCaseQueryRequest,
)


class Whitelist(NamedTuple):
    accounts: Set[str]
    entities: Set[str]

    @staticmethod
    def everything():
        return Whitelist(accounts=set(["*"]), entities=set(["*"]))

    @staticmethod
    def nothing():
        return Whitelist(accounts=set(), entities=set())


class QueryBackend(abc.ABC):
    @abc.abstractmethod
    def get_analysis(self, id: str) -> Optional[Analysis]:
        """Retrieve an Analysis entity.

        Parameters:
          id: The unique key of the Analysis.

        Returns:
          The Analysis, or None if no Analysis with the specified key exists.
        """

    @abc.abstractmethod
    def query_analyses(
        self, whitelist: Whitelist, query: AnalysisQueryRequest
    ) -> Collection[Analysis]:
        """Retrieve all Analysis entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the Analysis entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """

    @abc.abstractmethod
    def get_audit(self, id: str) -> Optional[Audit]:
        """Retrieve an Audit entity.

        Parameters:
          id: The unique key of the Audit.

        Returns:
          The Audit, or None if no Audit with the specified key exists.
        """

    @abc.abstractmethod
    def query_audits(
        self, whitelist: Whitelist, query: AuditQueryRequest
    ) -> Collection[Audit]:
        """Retrieve all Audit entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the Audit entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """

    @abc.abstractmethod
    def get_data_source(self, id: str) -> Optional[DataSource]:
        """Retrieve a DataSource entity.

        Parameters:
          id: The unique key of the DataSource.

        Returns:
          The DataSource, or None if no DataSource with the specified key exists.
        """

    @abc.abstractmethod
    def query_data_sources(
        self, whitelist: Whitelist, **query
    ) -> Collection[DataSource]:
        """Retrieve all DataSource entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the DataSource entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """

    @abc.abstractmethod
    def get_dataset(self, id: str) -> Optional[Dataset]:
        """Retrieve a Dataset entity.

        Parameters:
          id: The unique key of the Dataset.

        Returns:
          The Dataset, or None if no Dataset with the specified key exists.
        """

    @abc.abstractmethod
    def query_datasets(
        self, whitelist: Whitelist, query: DatasetQueryRequest
    ) -> Collection[Dataset]:
        """Retrieve all Dataset entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the Dataset entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """

    @abc.abstractmethod
    def get_evaluation(self, id: str) -> Optional[Evaluation]:
        """Retrieve an Evaluation entity.

        Parameters:
          id: The unique key of the Evaluation.

        Returns:
          The Evaluation, or None if no Evaluation with the specified key exists.
        """

    @abc.abstractmethod
    def query_evaluations(
        self, whitelist: Whitelist, query: EvaluationQueryRequest
    ) -> Collection[Evaluation]:
        """Retrieve all Evaluation entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the Evaluation entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """

    @abc.abstractmethod
    def get_inference_service(self, id: str) -> Optional[InferenceService]:
        """Retrieve an InferenceService entity.

        Parameters:
          id: The unique key of the InferenceService.

        Returns:
          The InferenceService, or None if no InferenceService with the specified key exists.
        """

    @abc.abstractmethod
    def query_inference_services(
        self, whitelist: Whitelist, query: InferenceServiceQueryRequest
    ) -> Collection[InferenceService]:
        """Retrieve all InferenceService entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the InferenceService entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """

    @abc.abstractmethod
    def get_inference_session(self, id: str) -> Optional[InferenceSession]:
        """Retrieve an InferenceSession entity.

        Parameters:
          id: The unique key of the InferenceSession.

        Returns:
          The InferenceSession, or None if no InferenceSession with the specified key exists.
        """

    @abc.abstractmethod
    def query_inference_sessions(
        self, whitelist: Whitelist, query: InferenceSessionQueryRequest
    ) -> Collection[InferenceSession]:
        """Retrieve all InferenceSession entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the InferenceSession entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """

    @abc.abstractmethod
    def get_measurement(self, id: str) -> Optional[Measurement]:
        """Retrieve a Measurement entity.

        Parameters:
          id: The unique key of the Measurement.

        Returns:
          The Measurement, or None if no Measurement with the specified key exists.
        """

    @abc.abstractmethod
    def query_measurements(
        self, whitelist: Whitelist, query: MeasurementQueryRequest
    ) -> Collection[Measurement]:
        """Retrieve all Measurement entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the Measurement entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """

    @abc.abstractmethod
    def get_method(self, id: str) -> Optional[Method]:
        """Retrieve a Method entity.

        Parameters:
          id: The unique key of the Method.

        Returns:
          The Method, or None if no Method with the specified key exists.
        """

    @abc.abstractmethod
    def query_methods(
        self, whitelist: Whitelist, query: MethodQueryRequest
    ) -> Collection[Method]:
        """Retrieve all Method entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the Method entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """

    @abc.abstractmethod
    def get_model(self, id: str) -> Optional[Model]:
        """Retrieve a Model entity.

        Parameters:
          id: The unique key of the Model.

        Returns:
          The Model, or None if no Model with the specified key exists.
        """

    @abc.abstractmethod
    def query_models(
        self, whitelist: Whitelist, query: ModelQueryRequest
    ) -> Collection[Model]:
        """Retrieve all Model entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the Model entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """

    @abc.abstractmethod
    def get_module(self, id: str) -> Optional[Module]:
        """Retrieve a Module entity.

        Parameters:
          id: The unique key of the Module.

        Returns:
          The Module, or None if no Module with the specified key exists.
        """

    @abc.abstractmethod
    def query_modules(
        self, whitelist: Whitelist, query: ModuleQueryRequest
    ) -> Collection[Module]:
        """Retrieve all Module entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the Module entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """

    @abc.abstractmethod
    def get_report(self, id: str) -> Optional[Report]:
        """Retrieve a Report entity.

        Parameters:
          id: The unique key of the Report.

        Returns:
          The Report, or None if no Report with the specified key exists.
        """

    @abc.abstractmethod
    def query_reports(
        self, whitelist: Whitelist, query: ReportQueryRequest
    ) -> Collection[Report]:
        """Retrieve all Report entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the Report entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """

    @abc.abstractmethod
    def get_safetycase(self, id: str) -> Optional[SafetyCase]:
        """Retrieve a SafetyCase entity.

        Parameters:
          id: The unique key of the SafetyCase.

        Returns:
          The SafetyCase, or None if no SafetyCase with the specified key exists.
        """

    @abc.abstractmethod
    def query_safetycases(
        self, whitelist: Whitelist, query: SafetyCaseQueryRequest
    ) -> Collection[SafetyCase]:
        """Retrieve all SafetyCase entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the SafetyCase entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """
