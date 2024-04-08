#### finmodels

`finmodels` is a Python package designed for financial analysis and optimization. It includes a collection of financial models, such as Discounted Cash Flow (DCF) valuation and Mean-Variance Portfolio Optimization. With finmodels, you can perform essential financial calculations to support investment decisions and portfolio management.

#### Key Features
`Discounted Cash Flow (DCF) Valuation`: Calculate the present value of future cash flows to assess the intrinsic value of an investment.

`Portfolio Optimization`: Optimize portfolio allocations using Mean-Variance Optimization to balance returns and risk.

`The Leveraged Buyout (LBO) Model`: LBO Model is a financial analysis tool used in corporate finance for 

evaluating the acquisition of a company using a significant amount of borrowed funds.

`IPO Model`: IPO Model is a simple Python script for calculating the Initial Public Offering (IPO) valuation using a discounted cash flow (DCF) model.


#### Installation

You can install the package using `pip`:

```
pip install finmodels
```
Usage
Discounted Cash Flow (DCF) Valuation
#### Example usage of DCF valuation

```
import finmodels as fm
cash_flows = [100, 150, 200, 250]
discount_rate = 0.1
dcf_value = fm.calculate_dcf(cash_flows, discount_rate)
print("DCF Value:", dcf_value)
```
#### Example usage of  Portfolio Optimization
```
import finmodels as fm
import numpy as np

# Example usage of portfolio optimization
expected_returns = np.array([0.05, 0.08, 0.12])
covariance_matrix = np.array([[0.001, 0.0005, 0.0002],
                              [0.0005, 0.002, 0.001],
                              [0.0002, 0.001, 0.003]])
optimal_weights = fm.optimize_portfolio(expected_returns, covariance_matrix)
print("Optimal Portfolio Weights:", optimal_weights)

```

#### Example usage of Leveraged Buyout (LBO) Model
```
import finmodels as fm
# Example usage
acquisition_price_example = 1000
equity_percentage_example = 0.3
debt_interest_rate_example = 0.05
projection_years_example = 5

# Create an instance of LBOModel
lbo_model = fm.LBOModel(acquisition_price_example, equity_percentage_example,
                     debt_interest_rate_example, projection_years_example)

# Calculate and print equity returns
equity_returns_result = lbo_model.calculate_equity_returns()
print(f"Equity Returns for each year: {equity_returns_result}")
```

#### Example usage of IPO Model
```
import finmodels as fm
# Example usage
initial_valuation = 500000000  # Initial company valuation before IPO
funds_raised = 100000000  # Funds raised during the IPO
operating_income = 75000000  # Annual operating income before IPO
growth_rate = 0.05  # Annual growth rate of operating income
years = 5  # Number of years for the IPO model

ipo_model = fm.IPOModel(initial_valuation, funds_raised, operating_income, growth_rate, years)
ipo_model.print_summary()
```

#### Contributors
Tamilselvan Arjunan
#### License
This project is licensed under the MIT License - see the LICENSE file for details.