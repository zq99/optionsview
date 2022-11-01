# optionsview

This library downloads option chain data for a given symbol from yahoo finance.

The data includes Calls and Puts for all future expiration dates and strike prices.

There are two formats provided:

- Straddle view: Call and Put data for the same expiration and strike is side by side.

- Stacked view: Call and Put data is stacked together.


## Installation

The library requires Python 3.7 or later.  
 
To install, type the following command on the python terminal:

    pip install optionsview
    
  
## Implementation

Here is a basic example of how to download options straddle view data:

    from options.data import download_options_view
    
    download_options_view('TSLA')

The following is an example of downloading the Call and Put data in a stacked format.

    from options.data import download_options_view, View
    
    folder = 'C:\Users\work\Documents'
    download_options_view('TSLA', View.STACKED, folder)
    
To read the data into dataframes (and not create files) you can do the following:

    from options.data import get_options_view_df

    straddle_df, stacked_df = get_options_view_df('TSLA')

    print(straddle_df.head())
    print(stacked_df.head())
    

## Examples

The folder 'samples' in this repository, has some examples of the output from the library.


## Contributions

Contributions are welcome, all modifications should come with appropriate tests.

All tests can be run by doing the following:

    from testing.tests import run_all_tests
    run_all_tests()

## Acknowledgements

This project makes use of the [yfinance](https://github.com/ranaroussi/yfinance) library.
