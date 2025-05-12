import requests
from bs4 import BeautifulSoup
import csv
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser
import os

BASE_URL = "https://www.abebooks.co.uk/book-search/isbn/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.137 Safari/537.36"
}
CHECK_INTERVAL = 3600  # seconds
CSV_FILE = "books.txt"

def get_book_details(isbn):
    url = f"{BASE_URL}{isbn}/n/100121502"
    response = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    title_tag = soup.find("span", {"data-test-id": "listing-title"})
    title = title_tag.text.strip() if title_tag else "Unknown Title"
    price_tag = soup.find("p", {"class": "item-price", "id": "item-price-1"})
    if price_tag:
        price = price_tag.text.strip()
        normalized_price = price.replace("Ł", "£").replace("£", "").replace(",", "").strip()
        price = float(normalized_price)
    else:
        raise ValueError(f"Price not found for ISBN {isbn}!")
    return title, price, url

def read_books():
    books = []
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["ISBN", "Price", "Title"])
            writer.writeheader()
    with open(CSV_FILE, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            books.append({
                "ISBN": row["ISBN"],
                "Price": float(row["Price"]),
                "Title": row.get("Title", "")
            })
    return books

def update_books(books):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["ISBN", "Price", "Title"])
        writer.writeheader()
        writer.writerows(books)

class PriceTrackerApp:
    def __init__(self, master):
        self.master = master
        master.title("Book Price Tracker")
        master.geometry("700x400")
        self.books = []
        self.create_widgets()
        self.refresh_books()
        self.monitor_thread = threading.Thread(target=self.monitor_prices, daemon=True)
        self.monitor_thread.start()

    def create_widgets(self):
        columns = ("ISBN", "Title", "Price (£)")
        self.tree = ttk.Treeview(self.master, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200 if col != "Title" else 300)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self.master)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(btn_frame, text="Add Book", command=self.add_book, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Remove Selected", command=self.remove_selected, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Refresh Now", command=self.refresh_prices, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Open in Browser", command=self.open_selected, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Exit", command=self.master.quit, width=10).pack(side=tk.RIGHT, padx=5)

    def refresh_books(self):
        self.books = read_books()
        self.tree.delete(*self.tree.get_children())
        for book in self.books:
            self.tree.insert("", tk.END, values=(
                book["ISBN"],
                book.get("Title", ""),
                f"{book['Price']:.2f}"
            ))

    def refresh_prices(self):
        threading.Thread(target=self.check_prices, daemon=True).start()

    def add_book(self):
        isbn = simpledialog.askstring("Add Book", "Enter ISBN:")
        if not isbn:
            return
        if any(book['ISBN'] == isbn for book in self.books):
            messagebox.showerror("Error", "This ISBN is already in your list.")
            return
        try:
            title, price, url = get_book_details(isbn)
            new_book = {"ISBN": isbn, "Price": price, "Title": title}
            self.books.append(new_book)
            update_books(self.books)
            self.refresh_books()
            messagebox.showinfo("Book Added", f"Added: {title}\nPrice: £{price:.2f}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not add book: {e}")

    def remove_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No selection", "Please select a book to remove.")
            return
        idx = self.tree.index(selected[0])
        book = self.books[idx]
        if messagebox.askyesno("Remove Book", f"Remove {book['Title']}?"):
            del self.books[idx]
            update_books(self.books)
            self.refresh_books()

    def open_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No selection", "Please select a book.")
            return
        idx = self.tree.index(selected[0])
        isbn = self.books[idx]["ISBN"]
        url = f"{BASE_URL}{isbn}/n/100121502"
        webbrowser.open(url)

    def show_price_popup(self, title, old_price, new_price, url):
        def open_url():
            webbrowser.open(url)
            popup.destroy()
        popup = tk.Toplevel(self.master)
        popup.title("Book Price Alert")
        popup.geometry("400x180")
        msg = f"{title}\nPrice changed:\nOld: £{old_price:.2f}\nNew: £{new_price:.2f}"
        tk.Label(popup, text=msg, padx=10, pady=10, wraplength=380, justify="left").pack()
        tk.Button(popup, text="Open Browser", command=open_url, width=15).pack(pady=5)
        tk.Button(popup, text="Close", command=popup.destroy, width=15).pack(pady=5)

    def check_prices(self):
        books = read_books()
        updated = False
        for book in books:
            isbn = book["ISBN"]
            old_price = book["Price"]
            try:
                title, new_price, url = get_book_details(isbn)
                if new_price != old_price:
                    self.master.after(0, self.show_price_popup, title, old_price, new_price, url)
                    book["Price"] = new_price
                    updated = True
                book["Title"] = title
            except Exception as e:
                print(f"Error for ISBN {isbn}: {e}")
        if updated:
            update_books(books)
        self.master.after(0, self.refresh_books)

    def monitor_prices(self):
        while True:
            self.check_prices()
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = PriceTrackerApp(root)
    root.mainloop()
