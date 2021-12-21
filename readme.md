# Optimizing Crypto-Currencies Portfolio
<!--Remove the below lines and add yours -->
The Portfolio Engine class is used for constructing mean-variance portfolio of crypto-currencies. The script extracts crypto currencies data in 1 hour interval via ftx api from 2021-10-01T00 to 2021-10-31T23. The script assign random weighting to 2500 simulated portfolio and calculate their standard deviation and mean return. Max Sharpe Ratio portfolio weighting and Min Volaility portfolio weighting will be chosen among the simulated results. The script will output the weighting into txt file and plot out efficient frontier chart

### Prerequisites
<!--Remove the below lines and add yours -->
* json
* Run `pip install json` to install required modules.

### How to run the script
<!--Remove the below lines and add yours -->
#### Direct Execution
* Run 'code test v2.py' to run the portfolio calculation to output weighting and plot out efficient frontier chart
* the weighting of max Sharpe Ratio will be output as max_sharpRatio_weighting.txt
* the weighting of min Volailty will be output as min_vol_weighting.txt

#### Amend Crypto currencies
* Download the 'code test v2.py'
* change the naming of crypto currency inside the coins list
* Run all the code
