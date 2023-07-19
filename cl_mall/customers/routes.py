"""
This module is for the customers.
All logics that relates to the customers are here
"""
from flask import redirect, render_template, url_for, flash, request, session, current_app, make_response
from cl_mall import db, app, photos, search, bcrypt, login_manager
from flask_login import login_required, current_user, logout_user, login_user
from .forms import CustomerRegisterForm, CustomerLoginForm
from .models import Register, CustomerOrder
import secrets, os, json
import pdfkit
import stripe
from sqlalchemy.exc import SQLAlchemyError

publishable_key = 'pk_test_51NPmRxCMRdELeAGDlsRu5KEpIukuyJD6m7LKv1YL1rf4gYQZcljMsS1ZCtHst1wXwBKHII0FFHLNiqey3m5wBZHU00Y3noSqOh'
stripe.api_key = 'sk_test_51NPmRxCMRdELeAGDevAw2xfroeIkaAEuue8sZxnGY251SWxtQRBy9GECPCSMoJlYGBX0FfT8LaSELssGh4owgIWv008bBZI1na'


@app.route('/payment', methods=['POST'])
@login_required
def payment():
    """Execute payment"""
    invoice = request.form.get('invoice')
    amount = request.form.get('amount')
    customer = stripe.Customer.create(
        email = request.form['stripeEmail'],
        source = request.form['stripeToken'],
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        description='CL Mall',
        amount=amount,
        currency='usd',
    )
    orders = CustomerOrder.query.filter_by(customer_id=current_user.id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
    orders.status = 'Paid'
    db.session.commit()
    flash('Order with the invoice: '+orders.invoice+' has been paid successfully', 'success')
    return redirect(url_for('home'))


@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    """Register Customers"""
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        register = Register(name=form.name.data,
                            username=form.username.data,
                            email=form.email.data,
                            password=hash_password,
                            country=form.country.data,
                            state=form.state.data,
                            city=form.city.data,
                            address=form.address.data,
                            zipcode=form.zipcode.data
                            )
        try:
            db.session.add(register)
            db.session.commit()
            flash(f'Welcome {form.name.data}, Thank you for registering', 'success')
            return redirect(url_for('customerLogin'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('An error occurred while registering. Please try again later.', 'danger')
            # Optionally, log the error for further investigation
            # print(e)
    return render_template('customer/register.html',
                           title='Customer Registration',
                           form=form)


@app.route('/customer/login', methods=['GET', 'POST'])
def customerLogin():
    """Customer Login Route"""
    form = CustomerLoginForm()
    if form.validate_on_submit():
        try:
            user = Register.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('Login successful!', 'success')
                next = request.args.get('next')
                return redirect(next or url_for('home'))
            else:
                raise ValueError('Wrong email or password supplied!')
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('customerLogin'))

    return render_template('customer/login.html',
                           title='Login page',
                           form=form)


@app.route('/customer/logout')
def customer_logout():
    """Logout a customer"""
    logout_user()
    flash('Thanks for shopping with us. Bye', 'info')
    return redirect(url_for('home'))


#remove unwanted details from shoppingcart
def updateshoppingcart():
    """Remove unwanted details from shoppingcart"""
    for _key, product in session['Shoppingcart'].items():
        session.modified = True
        del product['image']
        del product['colors']
    return updateshoppingcart 


@app.route('/getorder')
@login_required
def get_order():
    """Get order"""
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        updateshoppingcart()
        try:
            order = CustomerOrder(
                invoice = invoice,
                customer_id = customer_id,
                orders = session['Shoppingcart']
            )
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash('Your order has been submitted successfully', 'success')
            return redirect(url_for('orders', invoice=invoice))
        except Exception as e:
            print(e)
            flash('Something went wrong!', 'danger')
            return redirect(url_for('getCart'))
        

@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    """Displays orders to customer"""
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
        for _key, product in orders.orders.items():
            discount = (product['discount']/100) * float(product['price'])
            subTotal += float(product['price']) * int(product['quantity'])
            subTotal -= discount
            tax = ("%.2f" % (.06 * float(subTotal)))
            grandTotal = ("%.2f" % (1.06 * float(subTotal)))

    else:
        return redirect(url_for('customerLogin'))
    return render_template('customer/order.html',
                           title='Orders',
                           invoice=invoice,
                           tax=tax,
                           subTotal=subTotal,
                           grandTotal=grandTotal, 
                           customer=customer,
                           orders=orders)


@app.route('/get_pdf/<invoice>', methods=['POST'])
@login_required
def get_pdf(invoice):
    """Generate pdf for customer"""
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        if request.method == 'POST':
            customer = Register.query.filter_by(id=customer_id).first()
            orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.desc()).first()
            for _key, product in orders.orders.items():
                discount = (product['discount']/100) * float(product['price'])
                subTotal += float(product['price']) * int(product['quantity'])
                subTotal -= discount
                tax = ("%.2f" % (.06 * float(subTotal)))
                grandTotal = float("%.2f" % (1.06 * subTotal))

            rendered = render_template('customer/pdf.html', 
                                title='Invoice_'+invoice,
                                invoice=invoice,
                                tax=tax,
                                grandTotal=grandTotal, 
                                customer=customer,
                                orders=orders)
            pdf = pdfkit.from_string(rendered, False)
            response = make_response(pdf)
            response.headers['content-Type'] = 'application/pdf'
            response.headers['content-Disposition'] = 'inline: filename=' +invoice+'.pdf'
            return response
        return redirect(url_for('orders'))


@app.route('/view_orders')
@login_required
def view_orders():
    """Display orders to customer"""
    if current_user.is_authenticated:
        customer_id = current_user.id
        customer = Register.query.filter_by(id=customer_id).first()
        # Retrieve all rows from the CustomerOrder table
        orders = CustomerOrder.query.filter_by(customer_id=current_user.id).order_by(CustomerOrder.id.desc()).all()
        
        return render_template('customer/view_orders.html',
                               orders=orders,
                               title='My Orders')
