from inventory import (
    search_product,
    get_product_locations,
    get_total_stock,
    check_low_stock
)


# Search product
print("----- PRODUCT SEARCH -----")

products = search_product("Wireless Mouse")

for product in products:
    print("Product ID:", product[0])
    print("Name:", product[1])
    print("SKU:", product[2])
    print("Category:", product[3])


# Get locations
print("\n----- PRODUCT LOCATIONS -----")

product_id = products[0][0]

locations = get_product_locations(product_id)

for location in locations:
    print("Warehouse:", location[0])
    print("Row:", location[1])
    print("Bin:", location[2])
    print("Quantity:", location[3])
    print()


# Total stock
print("----- TOTAL STOCK -----")

total = get_total_stock(product_id)

print("Total Stock:", total)


# Low stock
print("\n----- LOW STOCK CHECK -----")

low_stock = check_low_stock(product_id)

if low_stock:
    print("!!!Low Stock!!!")
else:
    print("Stock Level OK✅")