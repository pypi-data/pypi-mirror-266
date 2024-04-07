# just_design_phase

The `just_design_phase` package provides a seamless interface for interacting with the Kite Connect API for stock trading on the Zerodha platform.

## Installation

To install the `just_design_phase` package, run the following command:

```bash
pip install just_design_phase
```

## Configuration

Before using the `just_design_phase` package, you must configure your environment with necessary API keys and secrets. Follow these steps to set up your environment:

1. **Environment Variables**: Store your Kite Connect API key and secret in a `.env` file at the root of your project. This file should contain:

    ```
    KITE_API_KEY=your_api_key_here
    KITE_API_SECRET=your_api_secret_here
    ```

## Usage

After setting up your environment, you can begin using the `just_design_phase` package to interact with the Zerodha Kite Connect API. Here are the primary functionalities offered:

### Placing Orders

The package provides several functions to place different types of orders. Users do not need to manually log in; the package handles authentication and session management.

-   **Place a Normal Order**:

    ```python
    from just_design_phase import place_normal_order

    order_id = place_normal_order(stock_name="RELIANCE", quantity=1, order_type="BUY")
    ```

-   **Place a Limit Order**:

    ```python
    from just_design_phase import place_limit_order

    order_id = place_limit_order(stock_name="TCS", quantity=2, price=3500, order_type="SELL")
    ```

### Modifying Orders

To modify existing orders, use the following functions based on your requirement:

-   **Modify an Order**:

    ```python
    from just_design_phase import modify_order

    modified_order_id = modify_order(variety="regular", orderId="your_order_id_here", quantity=2, price=3550)
    ```

### Fetching Account Details

Get current holdings or positions:

-   **Fetch Holdings**:

    ```python
    from just_design_phase import get_holdings

    holdings = get_holdings()
    ```

-   **Fetch Positions**:

    ```python
    from just_design_phase import get_positions

    positions = get_positions()
    ```
