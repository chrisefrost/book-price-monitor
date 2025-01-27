
# Book Price Monitor

A Python script that monitors book prices on **AbeBooks** using ISBN numbers. It checks for price changes at regular intervals and notifies the user with a popup if a price change is detected. The script also allows the user to open the book's page directly in their browser.

---

## Features

- **Price Monitoring**: Fetches the latest price of a book using its ISBN number.
- **Price Change Notification**: Displays a popup notification if the price changes.
- **Open in Browser**: Provides an option to open the book's page in the default browser.
- **CSV File Support**: Reads and writes book details (ISBN and price) to a CSV file.
- **Customizable Check Interval**: Allows you to set how often the script checks for price changes.

---

## Requirements

- Python 3.x
- Libraries:
  - `requests`
  - `beautifulsoup4`
  - `tkinter` (usually included with Python installations)
  - `csv`
  - `webbrowser`

You can install the required libraries using pip:
```bash
pip install requests beautifulsoup4
```

---

## Installation

1. Clone the repository (if applicable):
   ```bash
   git clone https://github.com/yourusername/book-price-monitor.git
   ```

2. Navigate to the project directory:
   ```bash
   cd book-price-monitor
   ```

3. Create a `books.txt` file with the following format:
   ```
   ISBN,Price
   9781234567890,10.99
   9780987654321,15.99
   ```
   Replace the ISBNs and prices with the books you want to monitor.

---

## Usage

1. Run the script:
   ```bash
   python price.py
   ```

2. The script will start monitoring the prices of the books listed in `books.txt`. It will check for price changes every hour (default interval).

3. If a price change is detected, a popup will appear with the following information:
   - Book title
   - Old price
   - New price
   - Option to open the book's page in the browser or close the popup.

4. The script will update the `books.txt` file with the latest prices.

---

## Example

### Input (`books.txt`):
```
ISBN,Price
9781234567890,10.99
9780987654321,15.99
```

### Output (in the console):
```
No change for 'Example Book Title' (ISBN 9781234567890). Current price: £10.99
Price changed for 'Another Book Title' (ISBN 9780987654321): £15.99 -> £12.99
```

### Popup Notification:
```
Another Book Title has changed in price.
Old: £15.99
New: £12.99
```

---

## Customization

- **Check Interval**: You can change the `CHECK_INTERVAL` variable in the script to adjust how often the script checks for price changes (in seconds).
- **CSV File**: You can change the `CSV_FILE` variable to use a different file for storing book details.

---

## Acknowledgments

- This script uses **AbeBooks** for fetching book prices.
- Libraries used: `requests`, `beautifulsoup4`, `tkinter`, `csv`, and `webbrowser`.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.txt) file for details.

---
