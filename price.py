import requests
from bs4 import BeautifulSoup
import csv
import time
import tkinter as tk
from tkinter import messagebox
import webbrowser

# Constants
BASE_URL = "https://www.abebooks.co.uk/book-search/isbn/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.137 Safari/537.36"}
CHECK_INTERVAL = 3600  # Check every hour (in seconds)
CSV_FILE = "books.txt"  # CSV file with ISBN and last recorded price

# Function to fetch the book details (title and price) from the webpage
def get_book_details(isbn):
    url = f"{BASE_URL}{isbn}/n/100121502"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the book title
    title_tag = soup.find("span", {"data-test-id": "listing-title"})
    title = title_tag.text.strip() if title_tag else "Unknown Title"

    # Extract the book price
    price_tag = soup.find("p", {"class": "item-price", "id": "item-price-1"})
    if price_tag:
        price = price_tag.text.strip()  # Extract text and strip any whitespace
        normalized_price = price.replace("Ł", "£").replace("£", "").strip()
        price = float(normalized_price)  # Convert to float for comparison
    else:
        raise ValueError(f"Price not found for ISBN {isbn}!")

    return title, price, url

# Function to show a popup notification with two options
def show_popup(title, old_price, new_price, url):
    def open_browser():
        webbrowser.open(url)  # Open the URL in the default browser
        popup.destroy()  # Close the popup window

    def close_popup():
        popup.destroy()  # Close the popup window

    # Create a popup window
    popup = tk.Tk()
    popup.title("Book Price Alert")
    popup.geometry("400x200")

    # Message
    message = (
        f"{title} has changed in price.\n"
        f"Old: £{old_price:.2f}\n"
        f"New: £{new_price:.2f}"
    )
    tk.Label(popup, text=message, padx=10, pady=10, wraplength=380, justify="left").pack()

    # Buttons
    tk.Button(popup, text="Open Browser", command=open_browser, width=15).pack(pady=5)
    tk.Button(popup, text="Close", command=close_popup, width=15).pack(pady=5)

    popup.mainloop()

# Function to read books from the CSV file
def read_books():
    books = []
    with open(CSV_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            books.append({"ISBN": row["ISBN"], "Price": float(row["Price"])})
    return books

# Function to write updated prices back to the CSV file
def update_books(books):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["ISBN", "Price"])
        writer.writeheader()
        writer.writerows(books)

# Main function to monitor price changes
def monitor_prices():
    while True:
        books = read_books()
        for book in books:
            isbn = book["ISBN"]
            old_price = book["Price"]
            try:
                title, new_price, url = get_book_details(isbn)
                if new_price != old_price:
                    print(f"Price changed for '{title}' (ISBN {isbn}): £{old_price} -> £{new_price}")
                    show_popup(title, old_price, new_price, url)
                    book["Price"] = new_price  # Update the price
                else:
                    print(f"No change for '{title}' (ISBN {isbn}). Current price: £{new_price}")
            except Exception as e:
                print(f"Error for ISBN {isbn}: {e}")

        # Save the updated prices back to the file
        update_books(books)

        # Wait before checking again
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_prices()