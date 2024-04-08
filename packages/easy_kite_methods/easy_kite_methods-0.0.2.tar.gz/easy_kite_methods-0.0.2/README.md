# easy_kite_methods

The `easy_kite_methods` package provides a seamless interface for interacting with the Kite Connect API for stock trading on the Zerodha platform.

## Installation

To install the `easy_kite_methods` package, run the following command:

```bash
pip install easy_kite_methods
```

## Configuration

Before using the `easy_kite_methods` package, you must configure your environment with necessary API keys and secrets. Follow these steps to set up your environment:

1. **Environment Variables**: Store your Kite Connect API key and secret in a `.env` file at the root of your project. This file should contain:

    ```
    KITE_API_KEY=your_api_key_here
    KITE_API_SECRET=your_api_secret_here
    ```

## Usage

Import the package using the alias `ekm` and utilize its functions for interacting with the Zerodha Kite Connect API.

### Example Imports

```python
import easy_kite_methods as ekm
```

### Placing Orders

-   **Place a Normal Order**:

    ```python
    order_id = ekm.place_normal_order(stock_name="RELIANCE", quantity=1, order_type="BUY")
    ```

-   **Place a Limit Order**:

    ```python
    order_id = ekm.place_limit_order(stock_name="TCS", quantity=2, price=3500, order_type="SELL")
    ```

### Modifying Orders

-   **Modify an Order**:

    ```python
    modified_order_id = ekm.modify_order(variety="regular", orderId="your_order_id_here", quantity=2, price=3550)
    ```

### Fetching Account Details

-   **Fetch Holdings**:

    ```python
    holdings = ekm.get_holdings()
    ```

-   **Fetch Positions**:

    ```python
    positions = ekm.get_positions()
    ```

### Additional Methods

Include more comprehensive functionalities for trading:

-   **Get Stock Price**:

    ```python
    stock_price = ekm.get_stock_price(name="RELIANCE")
    ```

-   **Get Stock Instrument Token**:

    ```python
    token = ekm.get_stock_instrument_token(stock_name="RELIANCE")
    ```

-   **Buy/Sell Intraday Normal Order**:

    ```python
    order_id = ekm.buy_intraday_normal_order(stock_name="INFY", quantity=10)
    ```

    ```python
    order_id = ekm.sell_intraday_normal_order(stock_name="INFY", quantity=5)
    ```

-   **Buy/Sell Intraday Limit Order**:

    ```python
    order_id = ekm.buy_intraday_limit_order(stock_name="INFY", quantity=10, price=1500)
    ```

    ```python
    order_id = ekm.sell_intraday_limit_order(stock_name="INFY", quantity=5, price=1500)
    ```

-   **Place Stop Loss Market Order**:

    ```python
    order_id = ekm.place_slm_order(stock_name="INFY", quantity=10, order_type="BUY", price=1500)
    ```

-   **Modify Order Properties**:

    ```python
    new_order_id = ekm.modify_order_quantity(variety="regular", order_id="order123", quantity=15)
    ```

    ```python
    new_order_id = ekm.modify_order_price(variety="regular", order_id="order123", price=1520)
    ```

-   **Cancel or Exit Orders**:

    ```python
    ekm.cancel_order(order_id="order123")
    ```

    ```python
    ekm.exit_orders(order_id="order123")
    ```
