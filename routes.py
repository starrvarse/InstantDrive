import os
import shutil
import uuid
from flask import render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

shared_items = {}

def find_file_by_unique_id(unique_id):
    return shared_items.get(unique_id)

def init_routes(app):
    @app.route('/')
    @app.route('/folder/<path:folder_path>')
    @login_required
    def index(folder_path=''):
        user_dir = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username, folder_path)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        files = os.listdir(user_dir)
        folders = [f for f in files if os.path.isdir(os.path.join(user_dir, f))]
        files = [f for f in files if os.path.isfile(os.path.join(user_dir, f))]

        if folder_path:
            parent_folder = folder_path.rsplit('/', 1)[0]
        else:
            parent_folder = None

        return render_template('index.html', files=files, folders=folders, folder_path=folder_path, parent_folder=parent_folder)

    # File Upload route (multiple files)
    @app.route('/upload', methods=['POST'])
    @login_required
    def upload_file():
        folder_path = request.form.get('folder_path', '')
        user_dir = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username, folder_path)

        if 'files[]' not in request.files:
            return jsonify(success=False, message='No files part'), 400

        files = request.files.getlist('files[]')
        for file in files:
            if file.filename == '':
                return jsonify(success=False, message='No selected file'), 400
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(user_dir, filename))

        return jsonify(success=True, message='Files successfully uploaded')

    @app.route('/create_folder', methods=['POST'])
    @login_required
    def create_folder():
        folder_name = request.form['folder_name']
        folder_path = request.form.get('folder_path', '')
        user_dir = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username, folder_path)
        folder_path_full = os.path.join(user_dir, secure_filename(folder_name))

        if not os.path.exists(folder_path_full):
            os.makedirs(folder_path_full)
            flash(f'Folder "{folder_name}" created')
        else:
            flash(f'Folder "{folder_name}" already exists')

        new_folder_path = os.path.join(folder_path, secure_filename(folder_name))
        return redirect(url_for('index', folder_path=new_folder_path))

    @app.route('/move_file', methods=['POST'])
    @login_required
    def move_file():
        filename = request.form['filename']
        folder_path = request.form['folder_path']
        target_folder = request.form['target_folder']

        user_dir = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username)
        current_file_path = os.path.join(user_dir, folder_path, filename)
        target_folder_path = os.path.join(user_dir, target_folder)

        if not os.path.exists(target_folder_path):
            flash(f'Target folder "{target_folder}" does not exist')
        else:
            new_file_path = os.path.join(target_folder_path, filename)
            shutil.move(current_file_path, new_file_path)
            flash(f'File "{filename}" moved to folder "{target_folder}"')

        return redirect(url_for('index', folder_path=folder_path))

    @app.route('/download/<path:filename>')
    @login_required
    def download_file(filename):
        user_dir = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username)
        return send_from_directory(user_dir, filename)

    @app.route('/delete/<path:filename>', methods=['POST'])
    @login_required
    def delete_file(filename):
        user_dir = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username)
        file_path = os.path.join(user_dir, filename)

        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                flash(f'File {filename} deleted')
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                flash(f'Folder {filename} deleted')
            else:
                flash(f'{filename} not found')
        except PermissionError as e:
            flash(f'Permission denied: {str(e)}')
        except Exception as e:
            flash(f'Error deleting {filename}: {str(e)}')

        return redirect(url_for('index'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name = request.form['name']
            username = request.form['username']
            email = request.form['email']
            dob = request.form['dob']
            phone = request.form['phone']
            password = request.form['password']

            if User.query.filter_by(username=username).first():
                flash('Username already exists')
                return redirect(url_for('register'))

            new_user = User(name=name, username=username, email=email, dob=dob, phone=phone)
            new_user.password = generate_password_hash(password)

            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('index'))

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index'))

            flash('Invalid credentials')
            return redirect(url_for('login'))

        return render_template('login.html')

    @app.route('/profile')
    @login_required
    def profile():
        return render_template('profile.html', username=current_user.username, email=current_user.email)

    @app.route('/edit_profile', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        if request.method == 'POST':
            current_user.name = request.form['name']
            current_user.email = request.form['email']
            current_user.dob = request.form['dob']
            current_user.phone = request.form['phone']

            db.session.commit()
            flash('Profile updated successfully')
            return redirect(url_for('profile'))

        return render_template('edit_profile.html', user=current_user)

    @app.route('/generate_link/<path:item>', methods=['POST'])
    @login_required
    def generate_link(item):
        unique_id = str(uuid.uuid4())
        view_only = 'view' in request.form
        user_dir = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username)
        shared_items[unique_id] = {'path': os.path.join(user_dir, item), 'view_only': view_only}
        
        flash(f'Shareable link generated: {request.host_url}shared/{unique_id}')
        return redirect(url_for('index'))

    @app.route('/shared/<unique_id>', methods=['GET'])
    def shared_file(unique_id):
        shared_item = find_file_by_unique_id(unique_id)

        if shared_item and os.path.isfile(shared_item['path']):
            return send_from_directory(os.path.dirname(shared_item['path']), os.path.basename(shared_item['path']))
        
        elif shared_item and os.path.isdir(shared_item['path']):
            files = os.listdir(shared_item['path'])
            folders = [f for f in files if os.path.isdir(os.path.join(shared_item['path'], f))]
            files = [f for f in files if os.path.isfile(os.path.join(shared_item['path'], f))]
            return render_template('shared_folder.html', files=files, folders=folders, folder_path=shared_item['path'])

        flash('File or folder not found')
        return redirect(url_for('index'))

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))
