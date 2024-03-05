from flask import Flask, render_template, request, redirect, flash, session, url_for
from functools import wraps

app = Flask(__name__)
app.secret_key = 'qwerty1234'

contas_a_pagar = []
contas_pagas = []
renda = 0
saldo_restante = 0

usuarios = {'user': '1234', 'user2':'4321'}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def autenticar():
    usuario = request.form['usuario']
    senha = request.form['senha']
    
    if usuario in usuarios and usuarios[usuario] == senha:
        session['usuario'] = usuario
        return redirect('/index')
    else:
        return render_template('login.html', error=True)
    

@app.route('/index')
@login_required
def index():
    total_contas_pagas = sum(conta['valor'] for conta in contas_pagas)
    saldo_restante = renda - total_contas_pagas
    
    return render_template('index.html', contas=contas_a_pagar, contas_pagas=contas_pagas, renda=renda, saldo_restante=saldo_restante, total_contas_pagas=total_contas_pagas)

@app.route('/logout')
@login_required
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))


@app.route('/configurar_saldo', methods=['POST'])
@login_required
def configurar_saldo():
    global renda
    renda_str = request.form['renda'].strip()
    
    if not renda_str:
        flash('Por favor, preencha o campo de renda.', 'error')
        return redirect('index')
    
    try:
        renda = float(renda_str)
    except ValueError:
        flash('O valor da renda inserido não é válido.', 'error')
        return redirect('/index')
    
    return redirect('/index')


@app.route('/adicionar_conta', methods=['POST'])
@login_required
def adicionar_conta():
    global saldo_restante
    descricao = request.form['descricao'].strip()
    valor_str = request.form['valor'].strip() 
    categoria = request.form['categoria'].strip()
    
    if not descricao or not valor_str:
        flash('Por favor, preencha todos os campos.', 'error')
        return redirect('/index')
    
    try:
        valor = float(valor_str)
    except ValueError:
        flash('O valor inserido não é válido.', 'error')
        return redirect('/index')
    
    for conta in contas_pagas:
        if conta['descricao'] == descricao:
            flash('Esta conta já foi paga.', 'error')
            return redirect('/index')
    
    for conta in contas_a_pagar:
        if conta['descricao'] == descricao:
            flash('Esta conta já foi adicionada.', 'error')
            return redirect('/index')
    
    contas_a_pagar.append({'descricao': descricao, 'valor': valor, 'categoria': categoria})
    flash('Conta adicionada com sucesso.', 'success')
    return redirect('/index')

@app.route('/pagar_conta/<int:indice>')
@login_required
def pagar_conta(indice):
    global saldo_restante
    global renda
    if not contas_a_pagar:
        flash('Não há contas a pagar.', 'error')
        return redirect('/index')
    
    conta = contas_a_pagar.pop(indice)
    contas_pagas.append(conta)
    return redirect('/index')

@app.route('/excluir_conta/<int:indice>')
@login_required
def excluir_conta(indice):
    del contas_a_pagar[indice]
    flash('Conta excluída com sucesso!', 'success')
    return redirect('/index')

@app.route('/editar_conta/<int:indice>', methods=['GET', 'POST'])
@login_required
def editar_conta(indice):
    if request.method == 'GET':
        if indice < 0 or indice >= len(contas_a_pagar):
            flash('Conta não encontrada.', 'error')
            return redirect('/index')
        
        conta = contas_a_pagar[indice]
        return render_template('editar_conta.html', indice=indice, conta=conta)
    
    elif request.method == 'POST':
        descricao = request.form['descricao'].strip()
        valor_str = request.form['valor'].strip()
        categoria = request.form['categoria'].strip()
        
        if not descricao or not valor_str or not categoria:
            flash('Por favor, preencha todos os campos.', 'error')
            return redirect(f'/editar_conta/{indice}')
        
        try:
            valor = float(valor_str)
        except ValueError:
            flash('O valor inserido não é válido.', 'error')
            return redirect(f'/editar_conta/{indice}')
        
        contas_a_pagar[indice]['descricao'] = descricao
        contas_a_pagar[indice]['valor'] = valor
        contas_a_pagar[indice]['categoria'] = categoria
        flash('Conta atualizada com sucesso.', 'success')
        return redirect('/index')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)