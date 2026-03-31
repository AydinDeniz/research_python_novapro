from flask import Flask, request, render_template_string, redirect, url_for, flash
from flask_mail import Mail, Message
import itsdangerous
import os
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with your actual secret key
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your-email-password'  # Replace with your email password

mail = Mail(app)
serializer = itsdangerous.URLSafeTimedSerializer(app.config['SECRET_KEY'])

users = {
    'user@example.com': 'password'  # Replace with your actual user data
}

def send_reset_email(user_email):
    token = serializer.dumps(user_email, salt='password-reset', expires_in=timedelta(minutes=15))
    msg = Message('Password Reset Request', sender='your-email@gmail.com', recipients=[user_email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_password', token=token, _external=True)}

If you did not make this request, simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        if email in users:
            send_reset_email(email)
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('forgot_password'))
        else:
            flash('Email address not found.', 'danger')
    return render_template_string('''
        <form method="post">
            <input type="email" name="email" required>
            <input type="submit" value="Reset Password">
        </form>
    ''')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset', max_age=900)
    except:
        flash('The token is invalid or has expired.', 'warning')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form['password']
        users[email] = new_password  # Replace with your actual password update logic
        flash('Your password has been updated!', 'success')
        return redirect(url_for('forgot_password'))
    
    return render_template_string('''
        <form method="post">
            <input type="password" name="password" required>
            <input type="submit" value="Reset Password">
        </form>
    ''')

if __name__ == '__main__':
    app.run(debug=True)