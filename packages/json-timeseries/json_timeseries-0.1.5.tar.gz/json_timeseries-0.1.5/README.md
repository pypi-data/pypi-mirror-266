# JSON Time Series

[![Documentation Status](https://readthedocs.org/projects/json-timeseries-py/badge/?version=latest)](https://json-timeseries-py.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/json-timeseries.svg)](https://badge.fury.io/py/json-timeseries)

[JSON Time Series](https://docs.eagle.io/en/latest/reference/historic/jts.html) (JTS specification) handling Python library - Time Series data construction, manipulation and serialisation.

## Installation

```shell
pip install json-timeseries
```

Import or require module
```python
from json_timeseries import TsRecord, TimeSeries, JtsDocument
```

## Usage

```python
from json_timeseries import TsRecord, TimeSeries, JtsDocument
from datetime import datetime

# Create Time Series
timeseries1 = TimeSeries(identifier='series_1', name='Series 1', data_type='NUMBER', 
    records=[
    TsRecord(**{"timestamp": datetime.now(), "value": '1.23', "quality": 192, "annotation": 'comment'}),
    TsRecord(**{"timestamp": datetime.now(), "value": '2.34', "quality": 245, "annotation": 'comment number 2'})])

timeseries2 = TimeSeries(identifier='series_2', name='Series 2', data_type='NUMBER', units="C", 
                         records=TsRecord(timestamp=datetime.now(), value=1.11, quality=111, annotation="comment ts2 111")
                         )

# Add record(s)
timeseries1.insert(TsRecord(**{ timestamp: datetime.now(), value: 30 }))

# Output in JSON Time Series document format
jts_doc = JtsDocument([timeseries1, timeseries2])
json_str = jts_doc.toJSONString()
````

## TimeSeries
`TimeSeries` is a class for constructing and manipulating a single dataset.

```python
from json_timeseries import TsRecord, TimeSeries
from datetime import datetime

time_series = TimeSeries(identifier='series_2', name='Series 2', data_type='NUMBER', units="m/s", 
                         records=TsRecord(timestamp=datetime.now(), value=1.11, quality=0, annotation="example comment")
                         )
```
### Options
Optionally provide configuration used for certain output formats such as JTS Document. 
- `data_type`: data type of record **value** attribute. `NUMBER | TEXT | TIME | COORDINATES`
- `id`: string or number to uniquely identify the series to use instead of the automatically assigned id.
- `name`: string
- `units`: string
- `records`: list of data records
  
Alternatively set later:
```python
time_series.data_type = 'NUMBER'
time_series.id = 'Series_1'
time_series.name = 'My Series'
time_series.units = 'm/s'
```

## TsRecord
`TsRecord` is a class for constructing and manipulating a single record.

```python
from json_timeseries import TsRecord
from datetime import datetime

ts_record1 = TsRecord(timestamp=datetime.now(), value=1.11, quality=0, annotation="example comment")
# Or as dict of parameters using ** operator
ts_record2 = TsRecord(**{"timestamp": datetime.now(), "value": 1.11, "quality": 0, "annotation": 'example comment'})
```
### Record attributes
Records require a timestamp and at least one attribute: value, quality or annotation
- `timestamp`: date object. Type of datetime. e.g.`datetime.now()`
- `value` *(optional)*:  number, string, date, null
- `quality` *(optional)*: number (quality code) associated with value
- `annotation` (optional): string description or comment related to the record

### Methods 

See [full documentation](https://json-timeseries-py.readthedocs.io).

### Properties

See [full documentation](https://json-timeseries-py.readthedocs.io).



## JTS Document

`JtsDocument` is a class for outputting `TimeSeries` in 
[JSON Time Series](https://docs.eagle.io/en/latest/reference/historic/jts.html) document format.


```python
# Create a JTS Document from one or more timeseries
jts_document = JtsDocument(series=[timeseries1, timeseries2])
# Output series in JTS Document format
json_str = jts_document.toJSONString()
```

### Options

- `series`: array of `TimeSeries` to include in JTS Document

### Methods 

See [full documentation](https://json-timeseries-py.readthedocs.io).

### Properties

See [full documentation](https://json-timeseries-py.readthedocs.io).

## License
MIT
