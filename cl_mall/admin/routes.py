"""
This is the admin module, all admin logic are here.
All administrative tasks will be done here
"""
from flask import render_template, session, request, redirect, url_for, flash
from cl_mall import app, db, bcrypt 
from .forms import RegistrationForm, LoginForm
from .models import User
from cl_mall.products.models import Addproduct, Brand, Category
import os
from flask_login import login_required, current_user, logout_user, login_user
from datetime import datetime


@app.context_processor
def inject_now():
    """This function will make the variables in our DICT to be available throughout the application"""
    if 'email' in session:
        admin =  User.query.filter_by(email = session['email']).first()
    else:
        admin = None

    productscount = Addproduct.query.filter(Addproduct.stock > 0).order_by(
        Addproduct.id.desc()).count()
    return {'now': datetime.utcnow(), 'admin': admin, 'productscount': productscount}


@app.route('/admin')
def admin():
    """This route will take us to the admin dashboard
    if no admin is logged in, it will take us to the login page"""
    if 'email' not in session:
        flash(f'You must be logged in', 'danger')
        return redirect(url_for('login'))
    products = Addproduct.query.all()
    admin =  User.query.filter_by(email = session['email']).first()
    return render_template('admin/index.html', 
                           title='Admin Dashboard', 
                           products=products,
                           admin=admin,
                           page_name='Dashboard')


@app.route('/brands')
def brands():
    """Add new brand to the db"""
    if 'email' not in session:
        flash(f'You must be logged in', 'danger')
        return redirect(url_for('login'))
    brands = Brand.query.order_by(Brand.id.desc()).all()
    return render_template('admin/brand.html',
                           title='Brand page',
                           brands=brands)


@app.route('/category')
def category():
    """add new category to the db"""
    if 'email' not in session:
        flash(f'You must be logged in', 'danger')
        return redirect(url_for('login'))
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/brand.html',
                           title='Categories page',
                           categories=categories)


@app.route('/admin/register', methods=['GET', 'POST'])
def register():
    """Register an admin"""
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        user = User(name=form.name.data,
                    username=form.username.data, 
                    email=form.email.data,
                    password=hash_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Welcome {form.name.data} Thanks for registering', 'success')
        return redirect(url_for('login'))
    return render_template('admin/register.html',
                           form=form,
                           title='Registration page')


@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    """Admin Login"""
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email = email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['email'] = email
            flash(f'Welcome {email} You are logged in now ', 'success')
            return redirect(request.args.get('next') or url_for('admin'))
        else:
            flash('Wrong Password, Please try again', 'danger')
    return render_template('admin/login.html',
                           form=form,
                           title='Admin Login Page')


@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    logout_user()
    flash(f'Logged out successfully', 'info')
    return redirect(url_for('login'))