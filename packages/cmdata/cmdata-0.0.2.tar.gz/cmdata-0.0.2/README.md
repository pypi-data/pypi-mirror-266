# cmdata 

> A python package to get started with CargoMetrics data products

The main goal of this python package is to get subscribers of the CargoMetrics data products up and running with our 
data as fast as possible. With that in mind we provide functions to quickly access the various datasets and perform 
the first couple of common transformations. After that, the universe is yours...  

# Getting started

The cmdata python package from CargoMetrics provides tools to get started with the _Advanced_ datasets, which are 
datasets that contain point-in-time data.

## Installation
The cmdata is available as a pip and can be installed into your python environment

```bash
> pip install cmdata
```

cmdata requires a python version > 3.9 and a pandas version > 1.0.

## Generating a view
The point-in-time Advanced datasets contain multiple time dimensions for each datapoint within the dataset 
(see [“Point-in-time deep dive”](#point-in-time-deep-dive)). To get started inspecting and assessing the data, 
the cmdata package provides a couple of views that reduce the dual time dimensionality to a single time-series. 
For a more in-depth example see [“Point-in-time deep dive”](#point-in-time-deep-dive).

To generate a view:

```python
from cmdata.commodities import point_in_time as pit

PATH = ’...’

pit_df = pit.read(PATH)
view = pit.standard_view(pit_df, asof=’2023-01-01’)
```

This view can be explored or transformed as any tabular one-dimensional dataset.

For example, to generate a plot:

```python
# plot Australian exports
ax = view[('export', 'AUS')].plot(figsize=(10, 3))
ax.set_xlabel('Date')
ax.set_ylabel('AUS exports of Iron Ore in mt / day')
```
![Australia Iron Ore exports - standard view](docs/images/standard-aus-iron-oir.png)

# Point-in-time deep dive

<blockquote>

**Terminology**

Throughout this document the following terms are used:

* **dataset**: a collection of (daily) increments
* **increment**: a collection of observations, published on day T, that contains information about the 
  last T-3 through T-90 days (i.e., a single csv file)
* **observation**: for the advanced commodity products an observation is the amount (in metric tons) of a 
  particular cargo that is imported or exported by a country on a given day
* **activity_date**: date associated with the observation, i.e., the date of import/export of cargo 
  into/out of country
* **publication_timestamp**: the time an increment was published, i.e., the time an increment is available 
  to the customer
* **lag**: the number of days difference between the _publication timestamp_ and the _activity date_
</blockquote>

The CargoMetrics’ _Advanced products_ are point-in-time datasets. This means that

* Each day, the CargoMetrics system use the input datasets, such as AIS, port, and vessel information, 
  available at that time to produce an estimate of global maritime trade covering the last 90 days 
  (this is referred to as the _increment_)
* Each observation in an increment has two associated times:
* The _publication timestamp_ (see box above)
* The _activity date_ (see box above)
* The collection of increments forms the point-in-time _dataset_, which provides the full history back  
  to 2013, and enables customers to train models without look-ahead bias and perform honest backtests.

The following section provides a step-by-step overview of how the _Advanced products_ are constructed.

## One increment

Each day (T), a single increment is added to the point-in-time dataset. This increment contains estimates 
of global maritime trade for activity dates T-3 through T-90. For example: the increment published on 2024-01-01 
contains activity dates ranging from 2023-10-03 (i.e., lag 90) through 2023-12-29 (i.e., lag 3).

The plot below shows a graphical representation of this increment in a two-dimensional time plot where:

* Each square represents an observation
* _Publication timestamp_ is along the vertical axis
* _Activity date_ is along the horizontal axis

![point-in-time visualization: one increment](docs/images/pit-legos-01.png)

## Multiple increments

The increment published 2024-01-02, i.e., the day after the increment depicted above, contains _activity dates_ 
ranging from 2023-10-03 through 2023-12-30. This means that 87 _activity dates_ are present in both increments. 
The graphical representation looks like

![point-in-time visualization: two increment](docs/images/pit-legos-02.png)

And three increments look like

![point-in-time visualization: three increment](docs/images/pit-legos-03.png)

Each increment, compared to the previous, adds one new day at the frontier of time (along the _activity date_ axes) 
and removes one day at the trailing end. 

A couple of things to note about this organization:

1: In the full dataset the same _activity date_ shows up in multiple increments. In other words, there are multiple 
observations for each _activity date_. 

![point-in-time visualization: multiple activity dates](docs/images/pit-legos-04.png) 

2: Each observation can be uniquely identified by its _activity date_ and _publication timestamp_ or _activity date_ 
and lag. 

![point-in-time visualization: uniqueness](docs/images/pit-legos-05.png)

## Lags 3 through 90

A note on why the _Advanced_ products contain only lags between three and 90 days for each increment:

* The upper limit of 90 days is set by the longest processes that occur in maritime shipping; 90 days 
  covers the longest voyages. For example, 90 days at 12 knots (a typical speed for tankers and dry bulk vessels)
  covers more distance than the circumference of the earth.
* The lower limit of 3 days is set by the update characteristics of the input data feeding the system. 
  Delays of up to 2 days between when characteristics change - such as the draft of a vessel - and when that change 
  is available in the input data are common.

# Building views

The two-dimensional point-in-time data provides crucial features that are important for training models on past data 
and for running honest backtests on those models. The main characteristic that facilitates this is the ability to 
select only the observations that were available at a particular time in the past.

To work with the point-in-time data, either to visualize it or to use it as an input to training a model, the dataset 
needs to be reduced to one time-dimension, hereafter referred to as a _view_. Typically, a time-series in terms of 
_activity dates_ is what is required.

A view is defined as a set of rules that results in exactly one publication for each _activity date_. The rules that 
define a view depend on the user’s needs. A few examples of views are depicted below. The `cmdata` package implements 
some of these views, which can be used as templates for other use cases.

> **Note**: New information is added each increment and the system modeling maritime trade becomes more accurate 
> the more information it has available. Long story short: the data matures over time, from increment to increment.

## A fixed lag view

The fixed lag view is defined by a single lag and selects only _activity dates_ that have the same lag. This view suits 
users interested in capturing the same level of maturation of the data for every activity date. A graphical 
representation of this view, selecting only the observations marked in black, looks like

![point-in-time visualization: fixed lag view](docs/images/pit-legos-06.png)

To create this view from a point-in-time dataset use:

```python
from cmdata.commodities import point_in_time as pit

PATH = ’...’

pit_df = pit.read(PATH)

# generate a fixed lag view at a 7-day lag, including data
#   available on or before 2023-01-01
#
view = pit.fixed_lag_view(pit_df, lag=7, asof=’2023-01-01’)
```

## A maturing view

The maturing view, which is provided in the Standard products for CargoMetrics Commodity products, selects the 
_activity date_ with the most up-to-date information from the available increments. This translates in selecting 
the _activity dates_ with lags 3 through 90 from the most recent increment; for the remaining increments select 
the _activity date_ with lag 90 only. The graphical representation is as follows, selecting the dark observations only:

![point-in-time visualization: standard view](docs/images/pit-legos-07.png)

To create this view from a point-in-time dataset use:

```python
from cmdata.commodities import point_in_time as pit

PATH = ’...’

pit_df = pit.read(PATH)

# generate a standard, aka maturing, view, including data
#   available on or before 2023-01-01
#
view = pit.standard_view(pit_df, asof=’2023-01-01’)
```