from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
@views.route('/home')
def home():
    user = 'Arjun'
    age = 32
    return render_template('home.html', user=user, age=age)
