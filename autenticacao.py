from flask import Flask, render_template, request, redirect, session, url_for
from functools import wraps

usuarios = {'user': '1234', 'user2':'4321'}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def autenticar():
    usuario = request.form['usuario']
    senha = request.form['senha']
    
    if usuario in usuarios and usuarios[usuario] == senha:
        session['usuario'] = usuario
        return redirect('/menu')
    else:
        return render_template('login.html', error=True)
    
def logout():
    global contas_a_pagar, contas_pagas, renda, saldo_restante, renda_2, saldo_restante_2
    contas_a_pagar = []
    contas_pagas = []
    renda = 0
    renda_2 = 0
    saldo_restante = 0
    saldo_restante_2 = 0
    session.pop('usuario', None)
    return redirect(url_for('login'))