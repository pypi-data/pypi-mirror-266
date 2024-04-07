# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module providing client for interacting with qBraid quantum services.

"""
import sys
from typing import Any, Dict, List, Optional

from qbraid_core.client import QbraidClient
from qbraid_core.exceptions import RequestsApiError
from qbraid_core.registry import register_client

from .exceptions import QuantumServiceRequestError
from .proxy import SUPPORTED_QJOB_LIBS, quantum_lib_proxy_state


@register_client()
class QuantumClient(QbraidClient):
    """Client for interacting with qBraid quantum services."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update_device(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates a quantum device with the given data."""
        try:
            return self.session.put("/quantum-devices", json=data).json()
        except RequestsApiError as err:
            raise QuantumServiceRequestError("Failed to update device") from err

    def update_job(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates a quantum job with the given data."""
        try:
            return self.session.put("/quantum-jobs", json=data).json()
        except RequestsApiError as err:
            raise QuantumServiceRequestError("Failed to update job") from err

    def search_devices(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Returns a list of quantum devices that match the given query filters."""
        query = query or {}

        # forward compatibility for casing transition
        if query.get("type") == "SIMULATOR":
            query["type"] = "Simulator"

        try:
            return self.session.get("/quantum-devices", params=query).json()
        except RequestsApiError as err:
            raise QuantumServiceRequestError("Failed to retrieve device data") from err

    def search_jobs(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Returns a list of quantum jobs run by the user that match the given query filters."""
        query = query or {}

        try:
            return self.session.get("/quantum-jobs", params=query).json()
        except RequestsApiError as err:
            raise QuantumServiceRequestError("Failed to retrieve job data") from err

    def get_device(
        self,
        qbraid_id: Optional[str] = None,
        vendor_id: Optional[str] = None,
        object_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Returns the metadata corresponding to the specified quantum device."""
        query = {}
        if qbraid_id is not None:
            query["qbraid_id"] = qbraid_id
        if vendor_id is not None:
            query["objArg"] = vendor_id
        if object_id is not None:
            if not self._is_valid_object_id(object_id):
                raise ValueError(
                    "Invalid object_id format: expected a 24-character hexadecimal string"
                )
            query["_id"] = object_id
        if len(query) == 0:
            raise ValueError("Must provide either qbraid_id, vendor_id, or object_id")

        devices = self.search_devices(query=query)

        if len(devices) == 0:
            raise QuantumServiceRequestError("No devices found matching given criteria")

        return devices[0]

    def get_job(
        self,
        qbraid_id: Optional[str] = None,
        vendor_id: Optional[str] = None,
        object_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Returns the metadata corresponding to the specified quantum job."""
        query = {}
        if qbraid_id is not None:
            query["qbraidJobId"] = qbraid_id
        if vendor_id is not None:
            query["vendorJobId"] = vendor_id
        if object_id is not None:
            if not self._is_valid_object_id(object_id):
                raise ValueError(
                    "Invalid object_id format: expected a 24-character hexadecimal string"
                )
            query["_id"] = object_id
        if len(query) == 0:
            raise ValueError("Must provide either qbraid_id, vendor_id, or object_id")

        jobs = self.search_jobs(query=query)

        if len(jobs) == 0:
            raise QuantumServiceRequestError("No jobs found matching given criteria")

        return jobs[0]

    def create_job(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new quantum job with the given data."""
        try:
            return self.session.post("/quantum-jobs", json=data).json()
        except RequestsApiError as err:
            raise QuantumServiceRequestError("Failed to create job") from err

    def qbraid_jobs_state(self, device_lib: Optional[str] = None) -> Dict[str, Any]:
        """
        Checks if qBraid Quantum Jobs are enabled in the current environment for the
        specified device library.

        Args:
            device_lib (Optional[str]): The name of the quantum device library. If None,
                                        checks all supported libraries.

        Returns:
            Dict[str, Any]: A dictionary containing the system's executable path and the states
                            of libraries relevant to qBraid Quantum Jobs. The libraries' states
                            include whether they are supported and enabled.
        """
        environment_state = {"exe": sys.executable}
        check_libs = [device_lib] if device_lib else SUPPORTED_QJOB_LIBS

        libs_state = {lib: quantum_lib_proxy_state(lib) for lib in check_libs}

        environment_state["libs"] = libs_state

        return environment_state
