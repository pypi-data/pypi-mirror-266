# Pre-release patches for dagster_insights

This package contains pre-release fixes and optimizations for the official `dagster_cloud.dagster_insights` module included in the [dagster-cloud](https://pypi.org/project/dagster-cloud/) package. To use the official version, run `pip install dagster-cloud` and import it as follows:

```
from dagster_cloud import dagster_insights
```

To enable the pre-release patches from this package, run `pip install dagster-insights` and import this module before importing `dagster_cloud.dagster_insights`:

```
import dagster_insights_prerelease  # Patches dagster_cloud.dagster_insights
from dagster_cloud import dagster_insights
```

This allows testing against a pre-release version of `dagster_insights` and provides a faster turnaround time for fixes and optimizations. All reliable fixes are eventually merged into `dagster_cloud.dagster_insights` and available in the official release.