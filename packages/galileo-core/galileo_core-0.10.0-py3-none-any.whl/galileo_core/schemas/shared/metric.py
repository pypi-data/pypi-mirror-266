from typing import List, Union

SingleMetricValue = Union[float, int, str, None]
MetricValueType = Union[SingleMetricValue, List[SingleMetricValue]]
