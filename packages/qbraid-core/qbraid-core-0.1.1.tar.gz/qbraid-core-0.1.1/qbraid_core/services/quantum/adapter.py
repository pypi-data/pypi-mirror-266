# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module for processing qBraid quantum devices and jobs data into
formats that can be more easily served to and received by clients.

"""
import datetime
from typing import Any, Dict, List, Optional, Tuple

from .exceptions import QuantumServiceRuntimeError


def _device_status_msg(num_devices: int, lag: int) -> str:
    """Helper function to return a status message based on the
    number of devices and the lag time."""
    if num_devices == 0:
        return "No results matching given criteria"
    hours, minutes = divmod(lag, 60)
    min_10, _ = divmod(minutes, 10)
    min_display = min_10 * 10
    if hours > 0:
        if minutes > 30:
            return f"Device status updated {hours}.5 hours ago"
        hour_s = "hour" if hours == 1 else "hours"
        return f"Device status updated {hours} {hour_s} ago"
    if minutes < 10:
        min_display = minutes
    return f"Device status updated {min_display} minutes ago"


def _job_status_msg(num_jobs: int, query: Dict[str, Any]) -> str:
    """Helper function to return a status message based on the
    the number of of query parameters and number of jobs returned."""
    max_results = query.get("numResults", 10)
    num_query_params = len(query)
    if num_jobs == 0:
        if num_query_params == 0:
            return "No jobs found submitted by user"
        return "No jobs found matching given criteria"
    if num_jobs < max_results:
        return f"Displaying {num_jobs}/{num_jobs} jobs matching query"
    if num_query_params > 0:
        plural = "s" if num_jobs > 1 else ""
        return f"Displaying {num_jobs} most recent job{plural} matching query"
    return f"Displaying {num_jobs} most recent jobs"


def _process_device_data(devices: List[Dict[str, Any]]) -> Tuple[List[List[str]], str]:
    """Processes raw device data adn returns list where each device is represented by
    its own length-4 list containing the [provider, name, qbraid_id, status]."""
    device_data = []
    tot_dev = 0
    min_lag = 1e7
    for document in devices:
        qbraid_id = document["qbraid_id"]
        name = document["name"]
        provider = document["provider"]
        status_refresh = document["statusRefresh"]
        # timestamp = datetime.datetime.now(datetime.UTC)
        timestamp = datetime.datetime.utcnow()
        if status_refresh is not None:
            format_datetime = str(status_refresh)[:10].split("-") + str(status_refresh)[
                11:19
            ].split(":")
            format_datetime_int = [int(x) for x in format_datetime]
            mk_datime = datetime.datetime(*format_datetime_int)
            lag = (timestamp - mk_datime).seconds
            min_lag = min(lag, min_lag)
        status = document["status"]
        tot_dev += 1
        device_data.append([provider, name, qbraid_id, status])

    device_data.sort()
    lag, _ = divmod(min_lag, 60)

    return device_data, _device_status_msg(tot_dev, lag)


def _process_job_data(
    jobs: List[Dict[str, Any]], query: Dict[str, Any]
) -> Tuple[List[List[str]], str]:
    """Processes raw job data and returns list"""
    num_jobs = 0
    job_data = []
    for document in jobs:
        job_id = document.get("qbraidJobId", document.get("_id"))
        if job_id is None:
            continue
        created_at = document.get("createdAt")
        if created_at is None:
            timestamps = document.get("timestamps", {})
            created_at = timestamps.get("createdAt", timestamps.get("jobStarted"))
        status = document.get("qbraidStatus", document.get("status", "UNKNOWN"))
        num_jobs += 1
        job_data.append([job_id, created_at, status])

    return job_data, _job_status_msg(num_jobs, query)


def process_device_data(devices: List[Dict[str, Any]]) -> Tuple[List[List[str]], str]:
    """Processes raw device data adn returns list where each device is represented by its own
    length-4 list containing the [provider, name, qbraid_id, status], and a status message."""
    try:
        return _process_device_data(devices)
    except Exception as err:  # pylint: disable=broad-exception-caught
        raise QuantumServiceRuntimeError("Failed to process device data") from err


def process_job_data(
    jobs: List[Dict[str, Any]], params: Optional[Dict[str, Any]] = None
) -> Tuple[List[List[str]], str]:
    """Processes raw job data and returns list of jobs and a status message."""
    params = params or {}

    try:
        return _process_job_data(jobs, params)
    except Exception as err:  # pylint: disable=broad-exception-caught
        raise QuantumServiceRuntimeError("Failed to process job data") from err
