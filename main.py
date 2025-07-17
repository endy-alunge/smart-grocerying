#required libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd

#http requests to websites and parsing html content
#_____________________________________________________________________________
#https://products.checkers.co.za/c-2413/All-Departments/Food
#https://www.woolworths.co.za/cat/Food/Milk-Dairy-Eggs/_/N-1sqo44p
#https://www.shoprite.co.za/c-2413/All-Departments/Food
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

url = "https://www.shoprite.co.za/c-2413/All-Departments/Food"
base_url = url
n = 0
while url:
    n = n + 1
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

    next_page = soup.find("li", class_="pagination-next")
    if next_page and next_page.a and "href" in next_page.a.attrs:
        next_href = next_page.a["href"]
        url = base_url + next_href

    # # printing out stored data
    # for name, price in zip(product_name, product_price):
    #     print(name.text+ " - "+price.text)

    with open("shoprite_products.txt", mode="a", encoding="utf-8") as file:
        for name, price in zip(product_name, product_price):
            file.write(f"{name.text.strip()} - {price.text.strip()}\n")
    
    # print("\n")
    # print(url)

    if n == 5:
        break
            
print("____________________________________________________________________________")
print("Products saved")
print("____________________________________________________________________________")

#reading files(txt/csv)
# with open("products.txt", mode="r", encoding="utf-8") as file:
#     for line in file:
#         if " - " in line:
#             name, price = line.strip().split(" - ")
#             price = float(price_str)
#             print(name + " - "+price)
#             products.append((name, price))

# capturing the products list from the user
def get_products_list():
    products_list = []

    print(" Enter your product names one by one. Press Enter after each. ")
    print(" Type 'submit' when you're done or 'exit' to cancel. ")

    while True:
        product = input("\n Enter product name (or type 'submit'): ").strip()

        if product.lower() == 'submit':
            print("\n Product list submitted.\n")
            break
        elif product.lower() == 'exit':
            print("\n Submission cancelled.")
            return []
        elif product == '':
            print(" Empty input. Please enter a valid product name.")
        else:
            products_list.append(product)
            print(f"{product}' added. Total so far: {len(products_list)}")

    return products_list

#extracting user products prices
def load_product_prices(file_path="products.txt"):
    product_prices = {}

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if " - R " in line:
                name, price_str = line.strip().split(" - R ")
                try:
                    product_prices[name.lower()] = float(price_str)
                except ValueError:
                    continue  # Skip bad lines

    return product_prices

#matching products with prices
def find_and_print_products(user_list, price_data):
    total = 0.0
    found = []

    print(" Here's your product list with prices:\n")

    for user_item in user_list:
        key = user_item.lower()
        matched = False

        for product_name in price_data:
            if key in product_name:  # partial match
                price = price_data[product_name]
                print(f"{product_name.title()} - R {price:.2f}")
                total += price
                matched = True
                break

        if not matched:
            print(f" '{user_item}' not found in product list.")
                  
    print("____________________________________________________________________________")
    print(f"\n Total Price: R {total:.2f}")


#main program
if __name__ == "__main__":
    product_list = get_products_list()

    if product_list:
        prices = load_product_prices()
        find_and_print_products(product_list, prices)
    else:
        print("No products were entered.")