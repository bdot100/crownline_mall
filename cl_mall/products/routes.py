"""
This file consists of the products routes.
All operations that has to do with products 
are in this Module.
"""
from flask import redirect, render_template, url_for, flash, request, session, current_app
from cl_mall import db, app, photos, search
from .models import Brand, Category, Addproduct
from .forms import Addproducts
import secrets, os


def brands():
    """This function lists out all brands that are associated with a product already."""
    brands = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    return brands

def categories():
    """This function lists out all categories that are associated with a product already."""
    categories = Category.query.join(Addproduct, (Category.id == Addproduct.category_id)).all()
    return categories


@app.route('/')
def home():
    """This route renders the home page, it queries the db for products and
    render them to the home page"""
    page = request.args.get('page', 1, type=int)
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(
        Addproduct.id.desc()).paginate(page=page, per_page=4)
    return render_template('home/index.html',
                           title='All products', 
                           products=products,
                           brands=brands(),
                           categories=categories())


@app.route('/admin/products')
def get_products():
    """This route gets all the products for an admin only"""
    page = request.args.get('page', 1, type=int)
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(
        Addproduct.id.desc()).paginate(page=page, per_page=4)
    return render_template('products/products.html',
                           title='All products',
                           products=products,
                           brands=brands(),
                           categories=categories())


@app.route('/products')
def all_products():
    """This route gets all products in the db"""
    page = request.args.get('page', 1, type=int)
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(
        Addproduct.id.desc()).paginate(page=page, per_page=4)
    return render_template('products/index.html',
                           title='All products',
                           products=products,
                           brands=brands(),
                           categories=categories())


@app.route('/result')
def result():
    """This route show the result from a search string"""
    searchword = request.args.get('q')
    products = Addproduct.query.msearch(searchword, fields=['name', 'description'], limit=3)
    return render_template('products/result.html', 
                           title='Search Product', 
                           products=products, 
                           brands=brands(), 
                           categories=categories())


@app.route('/product/<int:id>')
def single_page(id):
    """This route displays a product's details on a single page"""
    product = Addproduct.query.get_or_404(id)
    return render_template('products/single_page.html', 
                           title=product.name, 
                           product=product,
                           brands=brands(), 
                           categories=categories())


@app.route('/brand/<int:id>', methods=['GET', 'POST'])
def get_brand(id):
    """This route gets products based on a brand selected"""
    page = request.args.get('page', 1, type=int)
    get_b = Brand.query.filter_by(id=id).first_or_404()
    brand = Addproduct.query.filter_by(brand=get_b).paginate(page=page, per_page=4)
    return render_template('products/index.html',
                           title='All products',
                           brand=brand,
                           brands=brands(),
                           categories=categories(),
                           get_b=get_b)


@app.route('/categories/<int:id>')
def get_category(id):
    """This route gets products based on a category selected"""
    page = request.args.get('page', 1, type=int)
    get_cat = Category.query.filter_by(id=id).first_or_404()
    get_prod_cat = Addproduct.query.filter_by(category=get_cat).paginate(page=page, per_page=4)
    return render_template('products/index.html', 
                           title='All products', 
                           get_prod_cat=get_prod_cat, 
                           categories=categories(), 
                           brands=brands(),
                           get_cat=get_cat)


@app.route('/addbrand', methods=['GET', 'POST'])
def addbrand():
    """This route adds a new brand to the database"""
    if 'email' not in session:
        flash(f'You must be logged in', 'danger')
        return redirect(url_for('login'))

    if request.method == "POST":
        getbrand = request.form.get('brand')
        
        if not getbrand:
            flash('Please enter a brand name', 'danger')
            return redirect(url_for('addbrand'))

        brand = Brand(name=getbrand)

        try:
            db.session.add(brand)
            db.session.commit()
            flash(f'The Brand {getbrand} has been added successfully', 'success')
            return redirect(url_for('addbrand'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the brand. Please try again later.', 'danger')
            # Optionally, we can log the error for further investigation
            # print(e)
    return render_template('products/addbrand.html', brands='brands')



@app.route('/updatebrand/<int:id>', methods=['GET', 'POST'])
def updatebrand(id):
    """This route updates a brand's name based on the id supplied"""
    if 'email' not in session:
        flash(f'You must be logged in', 'danger')
        return redirect(url_for('login'))
    updatebrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    if request.method == "POST":
        updatebrand.name = brand
        flash(f'Brand has been updated successfully', 'success')
        db.session.commit()
        return redirect(url_for('brands'))
    return render_template('products/updatebrand.html',
                           title='Update brand page',
                           updatebrand=updatebrand)


@app.route('/deletebrand/<int:id>', methods=['POST'])
def deletebrand(id):
    """This route deletes a brand based on the id supplied"""
    brand = Brand.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(brand)
        db.session.commit()
        flash(f'Brand name {brand.name} has been deleted successfully', 'success')
        return redirect(url_for('brands'))
    flash(f'{brand.name} can\'t be deleted', 'warning')
    return redirect(url_for('brands'))


@app.route('/addcat', methods=['GET', 'POST'])
def addcat():
    """This route adds a new category to the database"""
    if 'email' not in session:
        flash(f'You must be logged in', 'danger')
        return redirect(url_for('login'))

    if request.method == "POST":
        getcat = request.form.get('category')

        if not getcat:
            flash('Please enter a category name', 'danger')
            return redirect(url_for('addcat'))

        cat = Category(name=getcat)

        try:
            db.session.add(cat)
            db.session.commit()
            flash(f'The Category {getcat} has been added successfully', 'success')
            return redirect(url_for('addcat'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the category. Please try again later.', 'danger')
            # Optionally, log the error for further investigation
            # print(e)

    return render_template('products/addbrand.html')



@app.route('/updatecat/<int:id>', methods=['GET', 'POST'])
def updatecat(id):
    """this route updates a category based on the id supplied"""
    if 'email' not in session:
        flash(f'You must be logged in', 'danger')
        return redirect(url_for('login'))
    updatecat = Category.query.get_or_404(id)
    category = request.form.get('category')
    if request.method == "POST":
        updatecat.name = category
        flash(f'Category name has been updated successfully', 'success')
        db.session.commit()
        return redirect(url_for('category'))
    return render_template('products/updatebrand.html',
                           title='Update brand page',
                           updatecat=updatecat)


@app.route('/deletecategory/<int:id>', methods=['POST'])
def deletecategory(id):
    """This route deletes a catgory based on the id supplied"""
    category = Category.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(category)
        db.session.commit()
        flash(f'Category name {category.name} has been deleted successfully', 'success')
        return redirect(url_for('categories'))
    flash(f'{category.name} can\'t be deleted', 'warning')
    return redirect(url_for('categories'))


@app.route('/addproduct', methods=['POST', 'GET'])
def addproduct():
    """This route adds a new product to the database"""
    if 'email' not in session:
        flash(f'You must be logged in', 'danger')
        return redirect(url_for('login'))

    brands = Brand.query.all()
    categories = Category.query.all()
    form = Addproducts(request.form)

    if request.method == "POST" and form.validate():
        try:
            name = form.name.data
            price = form.price.data
            discount = form.discount.data
            stock = form.stock.data
            colors = form.colors.data
            description = form.description.data
            brand = request.form.get('brand')
            category = request.form.get('category')
            
            image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            
            addpro = Addproduct(name=name, price=price, discount=discount, stock=stock, colors=colors,
                                description=description, brand_id=brand, category_id=category, image_1=image_1,
                                image_2=image_2, image_3=image_3)
            
            db.session.add(addpro)
            db.session.commit()
            flash(f'The product {name} has been added to your database', 'success')
            return redirect(url_for('admin'))
        
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the product. Please try again later.', 'danger')

    return render_template('products/addproduct.html',
                           form=form,
                           title='Add Product Page',
                           brands=brands,
                           categories=categories)



@app.route('/updateproduct/<int:id>', methods=['GET', 'POST'])
def updateproduct(id):
    """This route updates a product based on the id supplied"""
    brands = Brand.query.all()
    categories = Category.query.all()
    product = Addproduct.query.get_or_404(id)
    brand = request.form.get('brand')
    category = request.form.get('category')
    form = Addproducts(request.form)
    if request.method == "POST":
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.stock = form.stock.data
        product.brand_id = brand
        product.category_id = category
        product.colors = form.colors.data
        product.description = form.description.data
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, 'static/images/' + product.image_1))
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
                
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, 'static/images/' + product.image_2))
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            except:
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
                
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, 'static/images/' + product.image_3))
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            except:
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        db.session.commit()
        flash(f'Product updated successfully', 'success')
        return redirect(url_for('admin'))
    
    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.colors.data = product.colors
    form.description.data = product.description
    return render_template('products/updateproduct.html',
                           form=form, 
                           title='Update product',
                           brands=brands, 
                           categories=categories, product=product)
    
    
@app.route('/deleteproduct/<int:id>', methods=['POST'])
def deleteproduct(id):
    """This route deletes a product based on the id supplied"""
    product = Addproduct.query.get_or_404(id)
    if request.method == 'POST':
        try:
            os.unlink(os.path.join(current_app.root_path, 'static/images/' + product.image_1))
            os.unlink(os.path.join(current_app.root_path, 'static/images/' + product.image_2))
            os.unlink(os.path.join(current_app.root_path, 'static/images/' + product.image_3))
        except Exception as e:
            print(e)
        db.session.delete(product)
        db.session.commit()
        flash(f'The product {product.name} has been deleted successfully', 'success')
        return redirect(url_for('admin'))
    flash(f'Error deleting the product', 'danger')        
    return redirect(url_for('admin'))