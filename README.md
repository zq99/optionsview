# optionsview

This library downloads option chain data for a given symbol from yahoo finance.

The library retrieves call and put data for all expiration dates and strikes available through yfinance.

There are two formats provided:

- Straddle view: Call and Put data for the same expiration and strike is side by side.

- Stacked view: Call and Put data is stacked together.


## Installation

The library requires Python 3.7 or later.  
 
To install, type the following command on the python terminal:

    pip install optionsview
    
  
## Implementation

Here is a basic example of how to download options straddle view data:

    from optionsview.data import download_options_view
    
    download_options_view('TSLA')

The following is an example of downloading the Call and Put data in a stacked format.

    from optionsview.data import download_options_view, View
    
    folder = r"C:\Users\work\Documents"
    download_options_view('TSLA', View.STACKED, folder)
    
To read the data into dataframes (and not create files) you can do the following:

    from optionsview.data import get_options_view
    
    result = get_options_view('TSLA')
    
    if result is not None:
        print(result.straddle.head())
        print(result.stacked.head())
    

## Examples

The folder 'samples' in this repository, has some examples of the output from the library.


## Contributions

Contributions are welcome, all modifications should come with appropriate tests.

All tests can be run by doing the following:

    from testing.tests import run_all_tests
    run_all_tests()

These tests download live data and delete existing files in testing/exports before running.

## Acknowledgements

This project makes use of the [yfinance](https://github.com/ranaroussi/yfinance) library.
