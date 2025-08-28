from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv
from config import DATABASE_URI
import os
import re
import logging
from logging.handlers import RotatingFileHandler

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'cecc6799dcc70c096c8dfa228cb7d43e1839d1c0100c4ea254d5f0db023591b2')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['PROJECT_UPLOAD_FOLDER'] = 'static/project_images'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'

# Configure logging
if not app.debug:
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

# Ensure upload folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROJECT_UPLOAD_FOLDER'], exist_ok=True)

# User model for admin
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Blog model
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)

# Project model
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    client = db.Column(db.String(200))
    location = db.Column(db.String(200))
    site_area = db.Column(db.String(100))
    built_up_area = db.Column(db.String(100))
    cost = db.Column(db.String(100))
    duration = db.Column(db.String(100))
    dwelling_units = db.Column(db.String(100))

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def sanitize_filename(filename):
    filename = secure_filename(filename)
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    if not filename or not '.' in filename:
        return None
    return filename

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f"404 error: {str(error)}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    original = getattr(error, 'original_exception', error)
    app.logger.error(f"Internal Server Error: {str(original)}")
    return render_template('500.html', error=original), 500

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    app.logger.error(f"Unexpected error: {str(e)}")
    return render_template('500.html', error=str(e)), 500

# Routes
@app.route('/')
def index():
    blogs = Blog.query.all()
    app.logger.info(f"Fetched {len(blogs)} blogs")
    return render_template('index.html', blogs=blogs)

@app.route('/projects')
def projects():
    categories = ['Housing & Townships', 'Master Planning', 'Institutional',
                  'Commercial and Offices', 'Hospitality', 'Residence', 'Interior']
    projects = Project.query.all()
    app.logger.info(f"Fetched {len(projects)} projects")
    return render_template('projects.html', categories=categories, projects=projects)

@app.route('/projects/<category>')
def project_detail(category):
    projects = Project.query.filter_by(category=category).all()
    app.logger.info(f"Fetched {len(projects)} projects for category {category}")
    project_data = {
        'category': category,
        'description': projects[0].description if projects else f'{category} projects coming soon.',
        'images': [{'name': p.name, 'image_url': p.image_url, 'client': p.client or '', 'location': p.location or '',
                    'site_area': p.site_area or '', 'built_up_area': p.built_up_area or '', 'cost': p.cost or '',
                    'duration': p.duration or '', 'dwelling_units': p.dwelling_units or ''} for p in projects]
    }
    return render_template('project_detail.html', project=project_data)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        try:
            app.logger.info(f"Contact form submitted: Name={name}, Email={email}, Message={message}")
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            app.logger.error(f"Error processing contact form: {str(e)}")
            flash(f'Error sending message: {str(e)}', 'error')
    return render_template('contact.html')

@app.route('/blog')
def blog():
    blogs = Blog.query.all()
    app.logger.info(f"Fetched {len(blogs)} blogs")
    return render_template('blog.html', blogs=blogs)

@app.route('/store')
def store():
    categories = ['Housing & Townships', 'Master Planning', 'Institutional',
                  'Commercial and Offices', 'Hospitality', 'Residence', 'Interior']
    projects = Project.query.all()
    app.logger.info(f"Fetched {len(projects)} projects")
    return render_template('store.html', categories=categories, projects=projects)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            user = User(id='admin')
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/blogs', methods=['GET', 'POST'])
@login_required
def admin_blogs():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        file = request.files['image']
        if file:
            filename = sanitize_filename(file.filename)
            if filename:
                try:
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    image_url = f"/static/images/{filename}"
                    blog = Blog(title=title, content=content, image_url=image_url)
                    db.session.add(blog)
                    db.session.commit()
                    flash('Blog added successfully', 'success')
                except Exception as e:
                    app.logger.error(f"Error saving blog image: {str(e)}")
                    flash(f'Error saving blog image: {str(e)}', 'error')
            else:
                flash('Invalid image filename', 'error')
        else:
            flash('No image uploaded', 'error')
    blogs = Blog.query.all()
    app.logger.info(f"Fetched {len(blogs)} blogs for admin")
    return render_template('admin_blogs.html', blogs=blogs)

@app.route('/admin/blogs/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_blog(id):
    blog = Blog.query.get_or_404(id)
    if request.method == 'POST':
        blog.title = request.form['title']
        blog.content = request.form['content']
        file = request.files['image']
        if file:
            filename = sanitize_filename(file.filename)
            if filename:
                try:
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    blog.image_url = f"/static/images/{filename}"
                except Exception as e:
                    app.logger.error(f"Error saving blog image: {str(e)}")
                    flash(f'Error saving blog image: {str(e)}', 'error')
                    return redirect(url_for('admin_blogs'))
            else:
                flash('Invalid image filename', 'error')
                return redirect(url_for('admin_blogs'))
        db.session.commit()
        flash('Blog updated successfully', 'success')
        return redirect(url_for('admin_blogs'))
    return render_template('admin_blogs.html', blog=blog, blogs=Blog.query.all())

@app.route('/admin/blogs/delete/<int:id>')
@login_required
def delete_blog(id):
    blog = Blog.query.get_or_404(id)
    try:
        db.session.delete(blog)
        db.session.commit()
        flash('Blog deleted successfully', 'success')
    except Exception as e:
        app.logger.error(f"Error deleting blog: {str(e)}")
        flash(f'Error deleting blog: {str(e)}', 'error')
    return redirect(url_for('admin_blogs'))

@app.route('/admin/projects', methods=['GET', 'POST'])
@login_required
def admin_projects():
    if request.method == 'POST':
        category = request.form['category']
        name = request.form['name']
        description = request.form['description']
        client = request.form['client']
        location = request.form['location']
        site_area = request.form['site_area']
        built_up_area = request.form['built_up_area']
        cost = request.form['cost']
        duration = request.form['duration']
        dwelling_units = request.form['dwelling_units']
        file = request.files['image']
        if file:
            filename = sanitize_filename(file.filename)
            if filename:
                try:
                    file_path = os.path.join(app.config['PROJECT_UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    image_url = f"/static/project_images/{filename}"
                    project = Project(category=category, name=name, description=description, image_url=image_url,
                                     client=client, location=location, site_area=site_area, built_up_area=built_up_area,
                                     cost=cost, duration=duration, dwelling_units=dwelling_units)
                    db.session.add(project)
                    db.session.commit()
                    flash('Project added successfully', 'success')
                except Exception as e:
                    app.logger.error(f"Error saving project image: {str(e)}")
                    flash(f'Error saving project image: {str(e)}', 'error')
            else:
                flash('Invalid image filename', 'error')
        else:
            flash('No image uploaded', 'error')
    projects = Project.query.all()
    categories = ['Housing & Townships', 'Master Planning', 'Institutional',
                  'Commercial and Offices', 'Hospitality', 'Residence', 'Interior']
    app.logger.info(f"Fetched {len(projects)} projects for admin")
    return render_template('admin_projects.html', projects=projects, categories=categories)

@app.route('/admin/projects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    project = Project.query.get_or_404(id)
    if request.method == 'POST':
        project.category = request.form['category']
        project.name = request.form['name']
        project.description = request.form['description']
        project.client = request.form['client']
        project.location = request.form['location']
        project.site_area = request.form['site_area']
        project.built_up_area = request.form['built_up_area']
        project.cost = request.form['cost']
        project.duration = request.form['duration']
        project.dwelling_units = request.form['dwelling_units']
        file = request.files['image']
        if file:
            filename = sanitize_filename(file.filename)
            if filename:
                try:
                    file_path = os.path.join(app.config['PROJECT_UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    project.image_url = f"/static/project_images/{filename}"
                except Exception as e:
                    app.logger.error(f"Error saving project image: {str(e)}")
                    flash(f'Error saving project image: {str(e)}', 'error')
                    return redirect(url_for('admin_projects'))
            else:
                flash('Invalid image filename', 'error')
                return redirect(url_for('admin_projects'))
        db.session.commit()
        flash('Project updated successfully', 'success')
        return redirect(url_for('admin_projects'))
    categories = ['Housing & Townships', 'Master Planning', 'Institutional',
                  'Commercial and Offices', 'Hospitality', 'Residence', 'Interior']
    return render_template('admin_projects.html', project=project, projects=Project.query.all(), categories=categories)

@app.route('/admin/projects/delete/<int:id>')
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    try:
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted successfully', 'success')
    except Exception as e:
        app.logger.error(f"Error deleting project: {str(e)}")
        flash(f'Error deleting project: {str(e)}', 'error')
    return redirect(url_for('admin_projects'))

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.logger.info("Database tables created")
    app.run(debug=True)
else:
    with app.app_context():
        db.create_all()
        app.logger.info("Database tables created")