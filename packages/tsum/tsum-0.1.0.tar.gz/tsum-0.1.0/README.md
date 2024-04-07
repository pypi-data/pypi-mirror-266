## TSum - Table Summarization

> Given a table where rows correspond to records and columns correspond to attributes, we want to find a small number of patterns that succinctly summarize the dataset. 

TSum is a [table summarization algorithm published by Google Research.](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/41683.pdf) This is a Python implementation of the algorithm using Dask Dataframes for scale.  

### Usage

```python
import dask.dataframe as dd
from tsum import summarize, Pattern
from dask.distributed import LocalCluster

cluster = LocalCluster(n_workers=1, nthreads=8, diagnostics_port=8787)
client = cluster.get_client()
ddf: dd.DataFrame = ...
patterns: list[Pattern] = summarize(ddf=ddf)
```
