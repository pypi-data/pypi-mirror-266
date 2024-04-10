import logging
import sys

from . import dagster_insights_patched


def patch_dagster_insights():
    logging.warning("Patching dagster_cloud.dagster_insights with pre-releases fixes.")
    sys.modules["dagster_cloud.dagster_insights"] = dagster_insights_patched


patch_dagster_insights()
