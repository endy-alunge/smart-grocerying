#required libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask, render_template, request, jsonify

#http requests to websites and parsing html content
#_____________________________________________________________________________
#https://products.checkers.co.za/c-2413/All-Departments/Food
#https://www.woolworths.co.za/cat/Food/Milk-Dairy-Eggs/_/N-1sqo44p
#https://www.shoprite.co.za/c-95/All-Departments/Food/Fresh-Food
#https://www.makro.co.za/all/pr?sid=all&otracker=categorytree
#https://www.pnp.co.za/c/pnpbase (The last scrapping left, work on html)
#_____________________________________________________________________________

#browser headers for checkers and shoprite
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

url = "https://products.checkers.co.za/c-2413/All-Departments/Food"
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text,'html.parser')

#extracting products prices and store them
product_name = soup.find_all(
    lambda tag: (
        (tag.name == "a" and "range--title" in tag.get("class", [])) or
        (tag.name == "h2" and "product-card__name" in tag.get("class", [])) or
        (tag.name == "h3" and "item-product__name" in tag.get("class", [])) or
        (tag.name == "a" and "s1Q9rs" in tag.get("class", [])) # Makro
    )
)

product_price = soup.find_all(
    lambda tag: (
        (tag.name == "strong" and "price" in tag.get("class", [])) or
        (tag.name == "span" and "now" in tag.get("class", [])) or
        (tag.name == "span" and "_8TW4TR" in tag.get("class", [])) #still scrapping incorrect prices
    )
)

with open("products.txt", "w", encoding="utf-8") as file:
        for name, price in zip(product_name, product_price):
            file.write(f"{name.text.strip()} - {price.text.strip()}\n")

#printing out stored data
# for name, price in zip(product_name, product_price):
#     print(name.text+ " - "+price.text)

def load_product_prices(file_path="products.txt"):
    product_prices = {}

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if " - R" in line:
                name, price_str = line.strip().split(" - R")
                try:
                    product_prices[name.lower()] = float(price_str)
                except ValueError:
                    continue  # Skip bad lines

    return product_prices

#creating a flask app to display the data on a webpage
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("landingPage.html")

@app.route("/userInput", methods=["GET", "POST"])
def userInput():
    user_text = ""
    results_list = []
    
    if request.method == "POST":
        user_text = request.form.get("productInput", "")
        user_list = [item.strip().lower() for item in user_text.splitlines() if item.strip()]

        product_prices = load_product_prices()
        total = 0.0

        for user_item in user_list:
            matched = False
            for product_name in product_prices:
                if user_item in product_name:
                    price = product_prices[product_name]
                    results_list.append(f"{product_name.title()} - R {price:.2f}")
                    total += price
                    matched = True
                    break
            if not matched:
                results_list.append(f"'{user_item}' not found")

        results_list.append(f"Total: R {total:.2f}")

    return render_template(
        "userInput.html",
        user_text=user_text,
        results_list=results_list
    )

if __name__ == "__main__":
    app.run(debug=True)