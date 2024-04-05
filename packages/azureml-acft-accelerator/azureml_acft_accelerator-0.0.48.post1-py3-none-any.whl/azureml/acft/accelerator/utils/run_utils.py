# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
This file contains functions for getting run parameters
"""
import os
from typing import Optional, Dict, Any

from azureml.core import Run
from azureml.core.run import _OfflineRun
from azureml.core.compute import ComputeTarget
from azureml.acft.common_components import get_logger_app

from .config import Config


logger = get_logger_app(__name__)
run = Run.get_context()


def _get_run_id():
    """
    Returns run ID of parent of current run
    """

    if "OfflineRun" in run.id:
        return run.id
    return run.parent.id


def _get_sub_id():
    """
    Returns subscription ID of workspace where current run is executing
    """

    if "OfflineRun" in run.id:
        return Config.OFFLINE_RUN_MESSAGE
    return run.experiment.workspace.subscription_id


def _get_ws_name():
    """
    Returns name of the workspace where current run is submitted
    """

    if "OfflineRun" in run.id:
        return Config.OFFLINE_RUN_MESSAGE
    return run.experiment.workspace.name


def _get_region():
    """
    Returns the region of the workspace
    """

    if "OfflineRun" in run.id:
        return Config.OFFLINE_RUN_MESSAGE
    return run.experiment.workspace.location


def _get_compute():
    """
    Returns compute target of current run
    """

    if "OfflineRun" in run.id:
        return Config.OFFLINE_RUN_MESSAGE
    details = run.get_details()
    return details.get("target", "")


def _get_compute_vm_size():
    """
    Returns VM size on which current run is executing
    """

    if "OfflineRun" in run.id:
        return Config.OFFLINE_RUN_MESSAGE
    compute_name = _get_compute()
    if compute_name == "":
        return "No compute found."

    try:
        cpu_cluster = ComputeTarget(workspace=run.experiment.workspace, name=compute_name)
    except Exception:
        # cannot log here, logger is not yet instantiated
        return f"could not retrieve vm size for compute {compute_name}"

    return cpu_cluster.vm_size


def find_root(run):
    """
    Return the root run of current run.
    """

    if isinstance(run, _OfflineRun):
        logger.info("Found offline run. Skipping finding root.")
        return run

    if not run.parent:
        return run

    root_run = run.parent
    while root_run.parent:
        root_run = root_run.parent

    return root_run


def add_run_properties(
    properties_to_add: Dict[str, Any],
    add_to_root: bool = False,
    custom_run: Optional[Run] = None,
    skip_add_properties_if_any_already_exist: bool = False
):
    """Add properties to the current context run object / root run object / custom run object. The default behavior
    to add properties is to ignore properties that already exists in current run.

    :param properties_to_add: properties to add to the run object
    :type Dict[str, Any]
    :param add_to_root: If enabled, the properties will be added to the root run object
    :type: boolean
    :param custom_run: custom run object other than the current context run or root run to add the parameters. The
    custom run object takes precedence when both add_to_root is True and custom_run is not None
    :type: Optional[Run]
    :param skip_add_properties_if_any_already_exist: Enabling this flag wil override the default behavior. Instead of
    skipping the existing properties, the entire property dictionary would not be added if any of the keys in
    :param properties_to_add are already part current properties.
    """

    # Identify run object to use
    if custom_run is not None:
        logger.info("Adding properties to custom run object.")
        run_obj_to_use = custom_run
    elif add_to_root:
        logger.info("Adding properties to root run object.")
        run_obj_to_use = find_root(run)
    else:
        logger.info("Adding properties to current run object.")
        run_obj_to_use = run

    # Skip adding properties for offline run
    if isinstance(run_obj_to_use, _OfflineRun):
        logger.info("Found offline run. Skipping addition of properties.")
        return

    # Fetch already added properties for the run
    existing_run_properties = run_obj_to_use.get_properties()
    if skip_add_properties_if_any_already_exist:
        any_property_exists = any([prop in existing_run_properties for prop in properties_to_add])
        if any_property_exists:
            logger.info(
                "Atleast one of the existing property already exists."
                f"Skipping addition of properties: {properties_to_add}"
            )
            return

    # deleting the already existing properties from properties_to_add
    new_properties_to_add = {}
    for property, value in properties_to_add.items():
        if property in existing_run_properties:
            logger.info(f"The property {property} already exists. Not adding it.")
            continue
        new_properties_to_add[property] = value

    # adding the remaining properties
    logger.info(f"Adding the properties: {new_properties_to_add}")
    run_obj_to_use.add_properties(new_properties_to_add)


def is_main_process():
    """
    Function for determining whether the current process is master.
    :return: Boolean for whether this process is master.
    """
    return os.environ.get('AZUREML_PROCESS_NAME', 'main') in {'main', 'rank_0'}