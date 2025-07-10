from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from openpyxl import Workbook
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    destination = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(80), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    people = db.Column(db.Integer, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    tour_type = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Пожалуйста, заполните все поля', 'danger')
            return redirect(url_for('register'))

        # Проверяем, есть ли пользователь с таким именем
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Пользователь с таким именем уже существует', 'danger')
            return redirect(url_for('register'))

        # Создаем нового пользователя
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Вы успешно зарегистрировались', 'success')
        return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/enter')
def enter():
    return render_template('enter.html')

@app.route('/pro_nas')
def pro_nas():
    return render_template('pro_nas.html')

@app.route('/ot_zov')
def ot_zov():
    return render_template('ot_zov.html')

@app.route('/find')
def find():
    return render_template('find.html')

@app.route('/submit', methods=['POST'])
def submit():
    destination = request.form['destination']
    city = request.form['city']
    date = request.form['date']
    duration = request.form['duration']
    people = request.form['people']
    budget = request.form['budget']
    tour_type = request.form['tour-type']
    email = request.form['email']

    # Save data to the database
    new_application = Application(
        destination=destination,
        city=city,
        date=date,
        duration=duration,
        people=people,
        budget=budget,
        tour_type=tour_type,
        email=email
    )

    db.session.add(new_application)
    db.session.commit()

    # Create Excel file
    wb = Workbook()
    ws = wb.active
    ws.title = "Заявка"

    ws.append(["Направление", "Город вылета", "Дата", "Продолжительность", "Количество людей", "Бюджет", "Тип тура", "Ваш Email"])
    ws.append([destination, city, date, duration, people, budget, tour_type, email])

    file_stream = io.BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    return send_file(
        file_stream,
        as_attachment=True,
        download_name="Заявка.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
