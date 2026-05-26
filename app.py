from flask import Flask, request, jsonify

from flask_cors import CORS

from models import db, User, LoginHistory

from user_agents import parse

from datetime import datetime
from flask_mail import Mail, Message

import random

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'

app.config['MAIL_PORT'] = 587

app.config['MAIL_USE_TLS'] = True

app.config['MAIL_USERNAME'] = 'YOUR_GMAIL@gmail.com'

app.config['MAIL_PASSWORD'] = 'YOUR_APP_PASSWORD'
CORS(app)
mail = Mail(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)
otp_storage = {}
with app.app_context():
    db.create_all()


@app.route('/')
def home():

    return "Secure Login System Running"


@app.route('/register', methods=['POST'])
def register():

    data = request.json

    email = data['email']

    password = data['password']

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:

        return jsonify({
            "message": "User already exists"
        })

    new_user = User(
        email=email,
        password=password
    )

    db.session.add(new_user)

    db.session.commit()

    return jsonify({
        "message": "Registration successful"
    })


@app.route('/login', methods=['POST'])
def login():

    data = request.json

    email = data['email']

    password = data['password']

    user = User.query.filter_by(
        email=email,
        password=password
    ).first()

    if not user:

        return jsonify({
            "message": "Invalid credentials"
        })

    user_agent_string = request.headers.get('User-Agent')

    user_agent = parse(user_agent_string)

    browser = user_agent.browser.family

    os = user_agent.os.family

    if user_agent.is_mobile:
        device = "Mobile"

    elif user_agent.is_pc:
        device = "Desktop"

    else:
        device = "Other"

    ip_address = request.remote_addr

    current_time = str(datetime.now())

    ip_address = request.remote_addr

    now = datetime.now()

    current_time = str(now)

    current_hour = now.hour


    if device == "Mobile":

        if current_hour < 10 or current_hour >= 13:

            return jsonify({

                "message":
                "Mobile login allowed only between 10 AM and 1 PM"

            })


    if "Chrome" in browser:

        otp = random.randint(100000, 999999)

        otp_storage[email] = otp

        msg = Message(

            'Your Login OTP',

            sender=app.config['MAIL_USERNAME'],

            recipients=[email]
        )

        msg.body = f'Your OTP is: {otp}'

        mail.send(msg)

        message = "OTP sent to email"



    elif "Edge" in browser:

        message = "Login successful without OTP"


    else:

        message = "Login successful"


    history = LoginHistory(

        user_email=email,

        browser=browser,

        os=os,

        device=device,

        ip_address=ip_address,

        login_time=current_time
    )

    db.session.add(history)

    db.session.commit()

    return jsonify({

        "message": message,

        "browser": browser,

        "os": os,

        "device": device,

        "ip": ip_address
    })

    return jsonify({
        "message": "Login successful",

        "browser": browser,

        "os": os,

        "device": device,

        "ip": ip_address
    })

@app.route('/verify-otp', methods=['POST'])
def verify_otp():

    data = request.json

    email = data['email']

    entered_otp = data['otp']

    real_otp = otp_storage.get(email)

    if real_otp and str(real_otp) == str(entered_otp):

        return jsonify({

            "message": "OTP verified successfully"

        })

    return jsonify({

        "message": "Invalid OTP"

    })
@app.route('/history/<email>')
def history(email):

    logs = LoginHistory.query.filter_by(
        user_email=email
    ).all()

    result = []

    for log in logs:

        result.append({

            "browser": log.browser,

            "os": log.os,

            "device": log.device,

            "ip": log.ip_address,

            "time": log.login_time
        })

    return jsonify(result)

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)