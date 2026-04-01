"""
Yüz Tanıma Sistemi - Flask Web Uygulaması
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os
from face_registration import register_face_web
from face_login import login_face_web
from face_db import get_registered_users, delete_user
from face_liveness import check_liveness
import threading

app = Flask(__name__)
app.secret_key = 'yuz_tanima_secret_key_2026'

# Global değişkenler
registration_in_progress = False
login_in_progress = False

@app.route('/')
def index():
    """Ana menü sayfası"""
    users = get_registered_users()
    return render_template('menu.html', users=users)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Yüz kayıt sayfası"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        
        if not name:
            return render_template('register.html', error='Lütfen bir isim girin')
        
        # Kayıt işlemini başlat
        success, message = register_face_web(name, duration=15)
        
        if success:
            return render_template('register.html', success=message)
        else:
            return render_template('register.html', error=message)
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Yüz tanıma giriş sayfası"""
    if request.method == 'POST':
        # Giriş işlemini başlat
        recognized_user, message = login_face_web()
        
        if recognized_user:
            # Başarılı giriş
            session['user'] = recognized_user
            return redirect(url_for('success', user=recognized_user))
        else:
            return render_template('login.html', error=message)
    
    return render_template('login.html')

@app.route('/success')
def success():
    """Başarılı giriş sayfası"""
    user = request.args.get('user') or session.get('user')
    
    if not user:
        return redirect(url_for('login'))
    
    return render_template('success.html', user=user)

@app.route('/logout')
def logout():
    """Oturumu kapat"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/users-list')
def users_list():
    """Kayıtlı kullanıcılar"""
    users = get_registered_users()
    return render_template('users_list.html', users=users)

@app.route('/delete-user/<user_name>', methods=['POST'])
def delete_user_route(user_name):
    """Kullanıcı sil"""
    success, message = delete_user(user_name)
    return jsonify({'success': success, 'message': message})

@app.route('/liveness', methods=['GET', 'POST'])
def liveness_detection():
    """Canlılık testi sayfası"""
    if request.method == 'POST':
        # Canlılık testi başlat
        is_live, message = check_liveness(duration=8)
        
        if is_live:
            return render_template('liveness.html', success=message)
        else:
            return render_template('liveness.html', error=message)
    
    return render_template('liveness.html')

if __name__ == '__main__':
    # Debug modu açın
    app.run(debug=True, host='127.0.0.1', port=5000)
