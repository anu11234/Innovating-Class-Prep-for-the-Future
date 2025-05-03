from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teachprep.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    lessons = db.relationship('Lesson', backref='author', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    grade_level = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    objectives = db.Column(db.Text, nullable=True)
    materials = db.Column(db.Text, nullable=True)
    introduction = db.Column(db.Text, nullable=True)
    main_activities = db.Column(db.Text, nullable=True)
    conclusion = db.Column(db.Text, nullable=True)
    assessment = db.Column(db.Text, nullable=True)
    extensions = db.Column(db.Text, nullable=True)
    standards = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='Draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    resource_type = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    grade_level = db.Column(db.String(50), nullable=False)
    format = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(500), nullable=True)
    file_path = db.Column(db.String(500), nullable=True)
    rating = db.Column(db.Float, default=0.0)
    downloads = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'resource_type': self.resource_type,
            'subject': self.subject,
            'grade_level': self.grade_level,
            'format': self.format,
            'rating': self.rating,
            'downloads': self.downloads
        }

class UserResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'), nullable=False)
    is_favorite = db.Column(db.Boolean, default=False)
    last_viewed = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('user_resources', lazy=True))
    resource = db.relationship('Resource', backref=db.backref('user_resources', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('signup'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    recent_lessons = Lesson.query.filter_by(user_id=current_user.id).order_by(Lesson.updated_at.desc()).limit(4).all()
    return render_template('dashboard.html', recent_lessons=recent_lessons)

@app.route('/dashboard/lessons')
@login_required
def lessons():
    all_lessons = Lesson.query.filter_by(user_id=current_user.id).order_by(Lesson.updated_at.desc()).all()
    return render_template('lessons.html', lessons=all_lessons)

@app.route('/lesson-planner', methods=['GET', 'POST'])
@login_required
def lesson_planner():
    if request.method == 'POST':
        # In a real application, this would call an AI service
        # For now, we'll just create a sample lesson plan
        lesson_data = {
            'title': request.form.get('topic', 'New Lesson'),
            'subject': request.form.get('subject', 'Science'),
            'grade_level': request.form.get('grade', '5th Grade'),
            'duration': request.form.get('duration', '45 minutes'),
            'objectives': request.form.get('objectives', ''),
            'materials': json.dumps([
                "Handouts",
                "Whiteboard",
                "Markers",
                "Textbooks"
            ]),
            'introduction': "Begin by asking students what they know about the topic.",
            'main_activities': json.dumps([
                "Introduce key concepts",
                "Guide students through examples",
                "Have students practice independently",
                "Review as a class"
            ]),
            'conclusion': "Summarize key points and preview the next lesson.",
            'assessment': "Students will be assessed on their participation and understanding.",
            'extensions': json.dumps([
                "For advanced students: Additional research",
                "For students needing support: Guided practice"
            ]),
            'standards': json.dumps([
                "Standard 1: Understanding key concepts",
                "Standard 2: Applying knowledge"
            ]),
            'user_id': current_user.id
        }
        
        new_lesson = Lesson(**lesson_data)
        db.session.add(new_lesson)
        db.session.commit()
        
        return jsonify({"success": True, "lesson_id": new_lesson.id})
    
    return render_template('lesson_planner.html')

@app.route('/resource-finder')
@login_required
def resource_finder():
    resources = Resource.query.all()
    user_resources = {ur.resource_id: ur for ur in UserResource.query.filter_by(user_id=current_user.id).all()}
    
    for resource in resources:
        resource.is_favorite = user_resources.get(resource.id, UserResource(is_favorite=False)).is_favorite
    
    return render_template('resource_finder.html', resources=resources)

@app.route('/api/toggle-favorite/<int:resource_id>', methods=['POST'])
@login_required
def toggle_favorite(resource_id):
    user_resource = UserResource.query.filter_by(user_id=current_user.id, resource_id=resource_id).first()
    
    if user_resource:
        user_resource.is_favorite = not user_resource.is_favorite
    else:
        user_resource = UserResource(user_id=current_user.id, resource_id=resource_id, is_favorite=True)
        db.session.add(user_resource)
    
    db.session.commit()
    return jsonify({"success": True, "is_favorite": user_resource.is_favorite})

@app.route('/api/generate-lesson', methods=['POST'])
@login_required
def generate_lesson():
    # This would connect to an AI service in a real application
    # For now, we'll return a sample lesson plan
    data = request.json
    
    lesson_plan = {
        "title": f"Introduction to {data.get('topic', 'Science')}",
        "gradeLevel": data.get('grade', '5th Grade'),
        "subject": data.get('subject', 'Science'),
        "duration": data.get('duration', '45 minutes'),
        "objectives": [
            "Define key concepts and explain their importance",
            "Identify the key components of the topic",
            "Describe the basic processes related to the topic"
        ],
        "materials": [
            "Handouts",
            "Visual aids",
            "Manipulatives",
            "Textbooks",
            "Notebooks"
        ],
        "introduction": "Begin by asking students what they know about the topic. Display relevant materials and ask students to hypothesize.",
        "mainActivities": [
            "Introduce key terminology and break down concepts.",
            "Use diagrams or models to illustrate important processes.",
            "Have students examine materials and make observations.",
            "Guide students in creating their own labeled diagrams or notes."
        ],
        "conclusion": "Summarize the key points. Have students complete an exit ticket where they explain in their own words what they learned.",
        "assessment": "Students will be assessed on their diagram accuracy, participation in discussions, and their exit ticket responses.",
        "extensions": [
            "For advanced students: Research how different factors affect the topic",
            "For students needing support: Work in small groups with teacher guidance"
        ],
        "standards": [
            f"Standard 1: Students will understand {data.get('topic', 'the topic')}.",
            "Standard 2: Students will apply their knowledge to real-world situations."
        ]
    }
    
    return jsonify(lesson_plan)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
