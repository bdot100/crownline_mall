"""
This module deals with all the logics that has to with  cart
"""
from flask import redirect, render_template, url_for, flash, request, session, current_app
from cl_mall import db, app, photos
from cl_mall.products.models import Addproduct
from cl_mall.products.routes import brands, categories


def MergeDict(dict1, dict2):
    """merge different orders into a shopping cart"""
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False


@app.route('/addcart', methods=['POST', 'GET'])
def AddCart():
    """Add product to cart"""
    try:
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        color = request.form.get('colors')
        product = Addproduct.query.filter_by(id=product_id).first()

        if product_id and quantity and color and request.method == "POST":
            DictItems = {product_id: {'name': product.name, 'price': product.price, 'discount': product.discount,
                                      'color': color, 'quantity': quantity, 'image': product.image_1, 'colors': product.colors}}

            if 'Shoppingcart' in session:
                print(session['Shoppingcart'])
                if product_id in session['Shoppingcart']:
                    for key, item in session['Shoppingcart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item['quantity'] = int(item['quantity']) + 1
                            flash('Item added to your cart', 'success')
                else:
                    session['Shoppingcart'] = MergeDict(session['Shoppingcart'], DictItems)
                    flash('Item added to your cart', 'success')
                    return redirect(request.referrer)
            else:
                session['Shoppingcart'] = DictItems
                flash('Item added to your cart', 'success')
                return redirect(request.referrer)
            
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)
    

@app.route('/carts')
def getCart():
    """Display the content of your cart"""
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        flash('Your cart is currently empty', 'info')
        return redirect(url_for('home'))
    subtotal = 0
    grandtotal = 0
    for key, product in session['Shoppingcart'].items():
        discount = (product['discount']/100) * float(product['price'])
        subtotal += float(product['price']) * int(product['quantity'])
        subtotal -= discount
        tax = ("%.2f" % (.06 * float(subtotal)))
        grandtotal = float("%.2f" % (1.06 * subtotal))
    return render_template('products/carts.html',
                           title='My Cart',
                           tax=tax,
                           grandtotal=grandtotal,
                           brands=brands(),
                           categories=categories(),
                           subtotal=subtotal)


@app.route('/updatecart<int:code>', methods=['POST'])
def updatecart(code):
    """update the cart details based on the invoice provided"""
    if 'Shoppingcart' not in session and len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    if request.method == "POST":
        quantity = request.form.get('quantity')
        color = request.form.get('color')
        try:
            session.modified = True
            for key, item in session['Shoppingcart'].items():
                if int(key) == code:
                    item['color'] = color
                    item['quantity'] = quantity
                    flash('You cart items has been updated successfully', 'success')
                    return redirect(url_for('getCart'))
        except Exception as e:
            print(e)
            return redirect(url_for('getCart'))


@app.route('/deleteitem/<int:id>')
def deleteitem(id):
    """Delete an item from the cart"""
    if 'Shoppingcart' not in session and len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    try:
        session.modified = True
        for key, item in session['Shoppingcart'].items():
            if int(key) == id:
                session['Shoppingcart'].pop(key, None)
                flash('Item removed successfuly', 'success')
                return redirect(url_for('getCart'))
    except Exception as e:
        print(e)
        return redirect(url_for('getCart'))


@app.route('/clearcart')
def clearcart():
    """clear all items from the cart"""
    try:
        session.pop('Shoppingcart', None)
        flash('Your cart has been cleared. Keep shopping', 'success')
        return redirect(url_for('all_products'))
    except Exception as e:
        print(e)


@app.route('/empty')
def empty_cart():
    """clear cart"""
    try:
        session.clear()
        return redirect(url_for('home'))
    except Exception as e:
        print(e)
