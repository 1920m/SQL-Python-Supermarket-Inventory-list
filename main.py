import sqlite3
import time

# Connect to SQLite database (or create it if it doesn't exist)
db_connection = sqlite3.connect('supermarket.db')
cursor = db_connection.cursor()
basket = []

# Set up the database (creating the tables if they don't exist)
def setup_database():
    # Drop the inventory table if it exists (clean slate)
    cursor.execute("DROP TABLE IF EXISTS inventory")

    # Create inventory table with the updated structure
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        code INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        price REAL NOT NULL,
        category TEXT NOT NULL,
        quantity INTEGER NOT NULL
    )
    """)

    # Drop the admin table if it exists (optional cleanup)
    cursor.execute("DROP TABLE IF EXISTS admin")

    # Create admin table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
    """)

    # Insert initial data into admin table
    cursor.executemany("""
    INSERT OR IGNORE INTO admin (username, password) 
    VALUES (?, ?)""", [
        ("admin1", "pass123"),
        ("admin2", "admin-pass"),
        ("manager", "manager-pass"),
        ("supervisor", "sup123"),
        ("user1", "userpass")
    ])

    # Insert initial data into inventory table
    cursor.executemany("""
    INSERT INTO inventory (code, product_name, price, category, quantity) 
    VALUES (?, ?, ?, ?, ?)""", [
        (1643, "Milk", 1.50, "Dairy", 100),
        (1644, "Cheese", 2.00, "Dairy", 50),
        (1645, "Butter", 1.75, "Dairy", 75),
        (1646, "Ice cream", 3.50, "Dairy", 30),
        (1647, "Cream", 2.50, "Dairy", 40),
        (1648, "Apple", 0.75, "Fruits", 150),
        (1649, "Banana", 0.60, "Fruits", 120),
        (1650, "Orange", 0.80, "Fruits", 80),
        (1651, "Strawberry", 2.20, "Fruits", 60),
        (1652, "Grapes", 2.50, "Fruits", 70),
        (1653, "Chicken", 5.00, "Meats", 90),
        (1654, "Beef", 6.00, "Meats", 40),
        (1655, "Pork", 5.50, "Meats", 50),
        (1656, "Lamb", 7.50, "Meats", 25),
        (1657, "Turkey", 5.75, "Meats", 35)
    ])

    # Commit changes
    db_connection.commit()
    print("Database setup complete!")


# Function to authenticate admin login
def admin_login():
    print("\nAdmin Login")
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    # Query the admin table to check credentials
    cursor.execute("SELECT * FROM admin WHERE username = ? AND password = ?", (username, password))
    admin = cursor.fetchone()

    if admin:
        print("\nLogin successful! Welcome, Admin.")
        time.sleep(2)
        manage_inventory()  # Proceed to inventory management
    else:
        print("\nInvalid credentials. Access denied.")


# Function to print the current inventory from the database
def print_inventory():
    print("\nCurrent Inventory:")

    categories = ['Dairy', 'Fruits', 'Meats']

    for category in categories:
        print(f"\n{category.capitalize()} Section:")
        print("+-------------------+------------------+---------+----------+")
        print("| Code              | Product Name     | Price   | Quantity |")
        print("+-------------------+------------------+---------+----------+")

        cursor.execute("SELECT * FROM inventory WHERE category = ?", (category,))
        products = cursor.fetchall()

        for code, product_name, price, category, quantity in products:
            print(f"| {code:<17} | {product_name:<16} | {price:<7.2f} | {quantity:<8} |")

        print("+-------------------+------------------+---------+----------+")


# Function to add a product
def add_product():
    try:
        code = int(input("Enter the product code: "))

        # Check if the product already exists
        cursor.execute("SELECT product_name, quantity FROM inventory WHERE code = ?", (code,))
        result = cursor.fetchone()

        if result:
            # Existing product: update quantity
            product_name, current_quantity = result
            print(f"Product '{product_name}' already exists with quantity {current_quantity}.")
            additional_quantity = int(input("Enter the quantity to add: "))

            new_quantity = current_quantity + additional_quantity
            cursor.execute("UPDATE inventory SET quantity = ? WHERE code = ?", (new_quantity, code))
            db_connection.commit()
            print(f"Updated quantity for product '{product_name}'. New quantity: {new_quantity}")
        else:
            # New product: ask for additional details
            product_name = input("Enter product name: ").strip()
            price = float(input("Enter product price: "))
            quantity = int(input("Enter product quantity: "))
            category = input("Enter category (e.g., Dairy, Fruits, Meats): ").strip().capitalize()

            cursor.execute("""
                INSERT INTO inventory (code, product_name, price, category, quantity) 
                VALUES (?, ?, ?, ?, ?)
            """, (code, product_name, price, category, quantity))
            db_connection.commit()
            print(f"Product '{product_name}' added to {category} category with quantity {quantity}.")

    except ValueError:
        print("Invalid input. Please try again.")


# Function to update product quantity
def update_quantity(code, quantity):
    cursor.execute("""
    UPDATE inventory 
    SET quantity = ? 
    WHERE code = ?
    """, (quantity, code))
    db_connection.commit()
    print(f"Quantity updated for product code {code}.")


# Function to remove a product
def remove_product(code, quantity_to_remove):
    # Check if the product exists
    cursor.execute("SELECT quantity FROM inventory WHERE code = ?", (code,))
    result = cursor.fetchone()

    if result:
        current_quantity = result[0]

        # Check if there's enough quantity to remove
        if current_quantity >= quantity_to_remove:
            new_quantity = current_quantity - quantity_to_remove
            cursor.execute("UPDATE inventory SET quantity = ? WHERE code = ?", (new_quantity, code))
            print(f"Updated quantity for product {code}. New quantity: {new_quantity}")
        else:
            print(f"Not enough stock to remove. Current quantity: {current_quantity}")
    else:
        print(f"Product with code {code} does not exist.")

    db_connection.commit()


# Customer Role Functions
#  to display customer menu
def customer_menu():
    while True:
        print("\nAvailable Products:")
        print_inventory()  # Display the product menu first

        print("\nCustomer Menu:")
        print("[1] View Basket  [2] Add to Basket  [3] Checkout  [4] Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            view_basket(basket)
        elif choice == "2":
            add_to_basket(basket)
        elif choice == "3":
            checkout(basket)
            break
        elif choice == "4":
            print("Thank you for visiting! Have a good day.")
            break
        else:
            print("Invalid choice. Please try again.")


def view_basket(basket):
    if not basket:
        print("\nYour basket is empty.")
        return

    print("\nYour Basket:")
    for item in basket:
        print(f"{item[0]} (x{item[2]}): ${item[1] * item[2]:.2f}")

    return_shopping = input("\nWould you like to return to shopping? (Yes/No): ").strip().lower()

    if return_shopping == 'yes':
        customer_option_menu()  # This will take the user back to the main shopping menu
    elif return_shopping == 'no':
        checkout(basket)  # Proceed to checkout if they don't want to continue shopping
    else:
        print("Invalid input. Please enter 'Yes' or 'No'.")
        view_basket(basket)  # Re-run the basket view if the input was invalid


def add_to_basket(basket):
    # print_inventory()
    try:
        code = int(input("Enter the product code: "))
        quantity = int(input("Enter the quantity: "))

        cursor.execute("SELECT product_name, price, quantity FROM inventory WHERE code = ?", (code,))
        result = cursor.fetchone()

        if result:
            product_name, price, stock_quantity = result

            if quantity > stock_quantity:
                print("Insufficient stock. Please try again.")
            else:
                basket.append((product_name, price, quantity))
                cursor.execute("UPDATE inventory SET quantity = quantity - ? WHERE code = ?", (quantity, code))
                db_connection.commit()
                print(f"Added {quantity} x {product_name} to basket.")
                time.sleep(1.5)
                print("Processing...")
                time.sleep(3.25)
        else:
            print("Invalid product code.")
    except ValueError:
        print("Invalid input. Please try again.")


# Initialize customer balance at the start
customer_balance = 300


# Function to display the customer menu
def customer_option_menu():
    global customer_balance  # Use the global variable for customer balance

    while True:
        print("\nAvailable Products:")
        print_inventory()  # Display the product menu first

        print("\nCustomer Menu:")
        print("[1] View Basket  [2] Add to Basket  [3] Checkout  [4] Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            view_basket(basket)
        elif choice == "2":
            add_to_basket(basket)
        elif choice == "3":
            checkout(basket)
            break
        elif choice == "4":
            print("Thank you for visiting! Have a good day.")
            break
        else:
            print("Invalid choice. Please try again.")


# Updated checkout function with the customer balance
def checkout(basket):
    global customer_balance  # Access the global variable for customer balance

    if not basket:
        print("\nYour basket is empty. Have a good day!")
        return

    # Calculate total cost and display basket
    total_cost = 0
    print("\nYour Basket Summary:")
    print("+-------------------+------------------+--------------------+----------+")
    print("| Product Name      | Price per Item   | Quantity           | Total    |")
    print("+-------------------+------------------+--------------------+----------+")

    for item in basket:
        product_name, price, quantity = item
        item_total = price * quantity
        total_cost += item_total
        print(f"| {product_name:<17} | ${price:<7.2f}         | {quantity:<8}           | ${item_total:<8.2f}| ")

    print("+-------------------+------------------+--------------------+----------+")

    # Optionally, you can apply tax and display total with tax:
    tax_rate = 0.05  # Example tax rate: 5%
    tax_amount = total_cost * tax_rate
    total_with_tax = total_cost + tax_amount
    balance_left = customer_balance - total_with_tax

    print(f"\nSubtotal: ${total_cost:.2f}")
    print(f"Tax (5%): ${tax_amount:.2f}")
    print(f"Total (with tax): ${total_with_tax:.2f}")

    # Display the customer's balance
    print(f"\nYour balance: ${customer_balance:.2f}")
    print(f"\n${customer_balance} - ${total_with_tax:.2f} = ${balance_left:.2f}")
    print(f"\nYour current balance: ${balance_left:.2f}")

    # Check if the customer has enough money
    if customer_balance >= total_with_tax:
        print("\nCheckout successful. Thank you for shopping!")
        customer_balance -= total_with_tax  # Deduct the total from the balance
        basket.clear()  # Clear the basket after successful checkout
        time.sleep(1)
        main()  # Return to the main menu
    else:
        print(f"\nInsufficient funds. You need ${total_with_tax - customer_balance:.2f} more to complete the purchase.")
        retry = input("Would you like to add more money or return to the shopping menu? (Add/Return): ").strip().lower()
        if retry == "add":
            add_money = float(input("\nEnter the amount of money you want to add: $"))
            customer_balance += add_money  # Add money to balance
            print(f"Your new balance is: ${customer_balance:.2f}")
            checkout(basket)  # Re-run checkout to allow the customer to proceed
        else:
            print("Returning to shopping menu...")
            time.sleep(1)
            customer_option_menu()  # Return to shopping menu


# Main function to manage the inventory
def manage_inventory():
    try:
        while True:
            print_inventory()
            action = input("Do you want to '[1] Add', '[2] Remove' a product, or type '[3] Exit' to quit: ").lower()

            if action == '3':
                print("Exiting inventory management. Goodbye!")
                break

            if action == '2':
                code = int(input("Enter the product code: "))
                quantity_to_remove = int(input("Enter the quantity to remove: "))
                remove_product(code, quantity_to_remove)
            elif action == '1':
                add_product()
            else:
                print("Invalid action. Please try again.")
    except KeyboardInterrupt:
        print("\nExiting inventory management...")


# Role Selection Function
def main():
    setup_database()
    while True:
        try:
            print("\nWelcome to the Supermarket System")
            role = input("Are you an '[1] Admin' or '[2] Customer'? (Type '[3] exit' to quit): ").strip()#.lower()

            if role == '1':
                admin_login()
            elif role == '2':
                customer_option_menu()
            elif role == '3':
                print("\nExiting program...")
                break
            else:
                print("Invalid role. Please try again.")
        except KeyboardInterrupt:
            print("")
            print("\nExiting program...")
            break


main()
