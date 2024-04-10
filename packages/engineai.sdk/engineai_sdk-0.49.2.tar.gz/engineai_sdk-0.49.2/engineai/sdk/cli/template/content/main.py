"""Main file for Example project."""
# Import the necessary libraries.
from datetime import datetime as dt

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

from engineai.sdk.dashboard import dashboard
from engineai.sdk.dashboard.widgets import timeseries

# First, create a simple Dataframe that contains a DateTimeIndex and a column
# with random values.
# Instantiate Dashboard with a slug (a string that will designate the dashboard on the
# web browser) and a very simple Timeseries Widget, that receives the data, created
# above, as input.
index_range = pd.date_range(start=dt.now() - relativedelta(days=5 * 365), end=dt.now())
dashboard.Dashboard(
    slug="new_dashboard",
    content=timeseries.Timeseries(
        data=pd.DataFrame(
            {"values": np.random.uniform(low=0, high=100, size=len(index_range))},
            index_range,
        )
    ),
)
