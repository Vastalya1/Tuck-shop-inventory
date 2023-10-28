from flask import Flask, render_template, request, redirect, url_for,flash
import mysql.connector
app = Flask(__name__)
app.secret_key = 'secret_key' 
db = mysql.connector.connect(host="localhost", user='root', password='a.vastalya', database ='tci')

from datetime import datetime
admin_login=False
print(admin_login)

#generating recipt
def generate_receipt(item_name, quantity_bought):
    current_date = current_date = datetime.now().strftime("%Y-%m-%d %h-")
    cur = current_date = datetime.now().strftime("%Y-%m-%d")

    # Create a receipt content with the date
    receipt = f"Receipt\nDate: {current_date}\nItem Name: {item_name}\nQuantity Bought: {quantity_bought}"


    # Create a receipt content with the date
    receipt = f"Receipt\nDate: {current_date}\nItem Name: {item_name}\nQuantity Bought: {quantity_bought}"

    # Save the receipt to a text file
    r = "Receipt_" + cur+ ".txt"
    with open(r, "w") as file:
        file.write(receipt)



cursor=db.cursor()

# Sreplace this with a database)
inventory = []




@app.route('/')
def entering_page():
    return render_template('entering_page.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    
    global admin_login
    
    if request.method == 'POST':
        admin_name=request.form['admin_name']
        password=request.form['password']
        
        cursor.execute("SELECT admin_name, password FROM login_data WHERE admin_name=%s AND password=%s", (admin_name,password,))
        user=cursor.fetchone()
        if user:
            admin_login=True
            print(admin_login)
            return redirect(url_for('home'))
        else:
            flash('Please check your login details and try again', 'error')

    return render_template('login.html')




@app.route('/home')
def home():
    global admin_login
    if admin_login==True:
        #flash(f"Successfully bought the item!", category="success")

        # Fetch data from the database
        cursor.execute("SELECT item, quantity, price FROM inventory")
        data = cursor.fetchall()

        # Conve
        inventory = [{'item': item[0], 'quantity': item[1], 'price':item[2]} for item in data]
        print(inventory)
        return render_template('home.html', inventory=inventory)
    else:
        return render_template('entering_page.html')




@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        item_name = request.form['item_name']
        quantity = int(request.form['quantity'])
        price = int(request.form['price'])

        inventory.append({'item_name': item_name, 'quantity': quantity, 'price':price})
        
        
        insert_query = "INSERT INTO inventory (item,quantity,price) VALUES (%s, %s,%s)"
 
        cursor.execute(insert_query, (item_name, quantity,price))
        db.commit()
        return redirect(url_for('home'))
    
    
    return render_template('add_item.html')




@app.route('/edititem', methods=['GET', 'POST'])
def edit_item():
    if request.method == 'POST':
        selected_item = request.form['select_item']
        new_item_name = request.form['new_item_name']
        new_quantity = int(request.form['new_quantity'])
        new_price = int(request.form['new_price'])

        try:
            # Update the selected item in the database
            update_query = "UPDATE inventory SET item = %s, quantity = %s, price=%s WHERE item = %s"
            cursor.execute(update_query, (new_item_name, new_quantity,new_price, selected_item))
            db.commit()
        except mysql.connector.Error as err:
            print("MySQL Error:", err)

        return redirect(url_for('home'))

    # Fetch the items from the database to populate the select list
    cursor.execute("SELECT item FROM inventory")
    items_data = cursor.fetchall()
    items = [item[0] for item in items_data]

    return render_template('edititem.html', items=items)




@app.route('/deleteitem', methods=['GET','POST'])
def delete_item():
    if request.method == 'POST':
        selected_item = request.form['selected_item']

        # Use a prepared statement to safely delete the selected item
        delete_query = "DELETE FROM inventory WHERE item = %s"
        cursor.execute(delete_query, (selected_item,))

        # Commit the changes to the database
        db.commit()
        return redirect(url_for('home'))
    cursor.execute("SELECT item FROM inventory")
    items_data = cursor.fetchall()
    items = [item[0] for item in items_data]
    # Redirect to the home page or wherever you want to go after the deletion
    return render_template('deleteitem.html',items=items)




@app.route('/view')
def view():
    cursor.execute("SELECT item, quantity, price FROM inventory")
    data = cursor.fetchall()
    # Conve
    inventory = [{'item': item[0], 'quantity': item[1], 'price':item[2]} for item in data]
    print(inventory)
    return render_template('view.html', inventory=inventory)




@app.route('/buy', methods=['GET', 'POST'])
def buy_item():
    if request.method == 'POST':
        item_name = request.form['select_item']
        quantity_to_buy = int(request.form['quantity'])

        # Fetch the item's current quantity from the database
        cursor.execute("SELECT item, quantity FROM inventory WHERE item = %s", (item_name,))
        item_data = cursor.fetchone()

        if item_data:
            item_name, current_quantity = item_data

            if current_quantity >= quantity_to_buy:
                # Update the database with the new quantity (subtract the bought quantity)
                new_quantity = current_quantity - quantity_to_buy
                update_query = "UPDATE inventory SET quantity = %s WHERE item = %s"
                cursor.execute(update_query, (new_quantity, item_name))
                db.commit()

                # Generate and save the PDF receipt
                generate_receipt(item_name, quantity_to_buy)


                return redirect(url_for('view'))

                
            else:
                return "Not enough quantity available to buy."
        else:
            return "Item not found."
        
    cursor.execute("SELECT item FROM inventory")
    items_data = cursor.fetchall()
    items = [item[0] for item in items_data]
    print(items)
    
    return render_template('buy.html', items=items)



cart = []

@app.route('/cart', methods=['GET', 'POST'])
def view_cart():
    if request.method == 'POST':
        item_name = request.form['item_name']
        quantity = int(request.form['quantity'])
        price = int(request.form['price'])

        # Add the selected item to the cart
        cart.append({'name': item_name, 'quantity': quantity, 'price': price})

    total_price = sum(item['quantity'] * item['price'] for item in cart)

    return render_template('cart.html', cart=cart, total_price=total_price)


if __name__ == '__main__':
    app.run(debug=True)
