from flask import Flask, render_template, request, redirect, flash, session, url_for
from functools import wraps

app = Flask(__name__)
app.secret_key = 'qwerty1234'

contas_a_pagar = []
contas_pagas = []
renda = 0
saldo_restante = 0

# Segundo conjunto de renda e saldo restante
renda_2 = 0
saldo_restante_2 = 0

# Porcentagem
p1 = 0
p2 = 0


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
        return redirect('/menu')
    else:
        return render_template('login.html', error=True)
    




@app.route('/index')
@login_required
def index():
    total_contas_pagas = sum(conta['valor'] for conta in contas_pagas)
    saldo_restante = renda - total_contas_pagas
    
    return render_template('index.html', contas=contas_a_pagar, contas_pagas=contas_pagas, renda=renda, saldo_restante=saldo_restante, total_contas_pagas=total_contas_pagas)


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
    
    contas_a_pagar.append({'descricao': descricao, 'valor': valor})
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
        
        if not descricao or not valor_str:
            flash('Por favor, preencha todos os campos.', 'error')
            return redirect(f'/editar_conta/{indice}')
        
        try:
            valor = float(valor_str)
        except ValueError:
            flash('O valor inserido não é válido.', 'error')
            return redirect(f'/editar_conta/{indice}')
        
        contas_a_pagar[indice]['descricao'] = descricao
        contas_a_pagar[indice]['valor'] = valor
        flash('Conta atualizada com sucesso.', 'success')
        return redirect('/index')


@app.route('/logout')
@login_required
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


@app.route('/limpar')
@login_required
def limpar():
    global contas_a_pagar, contas_pagas, renda, saldo_restante
    contas_a_pagar = []
    contas_pagas = []
    renda = 0
    saldo_restante = 0
    return redirect('/index')


#menu
@app.route('/menu')
@login_required
def menu():
    return render_template('index_menu.html')

@app.route('/menu/conjunto')
@login_required
def conjunto_menu():
    return redirect('/conjunto')

@app.route('/menu/index')
@login_required
def index_menu():
    return redirect('/index')



#Conta Conjunta
@app.route('/conjunto')
@login_required
def index_conjunto():
    # Cálculo do saldo restante para o primeiro conjunto
    total_contas_pagas = sum(conta['valor'] for conta in contas_pagas)
    saldo_restante = renda - total_contas_pagas * (p1 / 100)

    # Cálculo do saldo restante para o segundo conjunto
    total_contas_pagas_2 = sum(conta['valor'] for conta in contas_pagas)
    saldo_restante_2 = renda_2 - total_contas_pagas_2 * (p2 / 100)

    return render_template('index_conjunto.html', contas=contas_a_pagar, contas_pagas=contas_pagas, renda=renda,
                           saldo_restante=saldo_restante, renda_2=renda_2, saldo_restante_2=saldo_restante_2,
                           total_contas_pagas=total_contas_pagas)


@app.route('/conjunto/configurar_saldo_conjunto', methods=['POST'])
@login_required
def configurar_saldo_conjunto():
    global renda, renda_2

    renda_str = request.form['renda'].strip()
    renda_2_str = request.form['renda_2'].strip()

    if not renda_str or not renda_2_str:
        flash('Por favor, preencha todos os campos.', 'error')
        return redirect('/conjunto')

    try:
        renda = float(renda_str)
        renda_2 = float(renda_2_str)
    except ValueError:
        flash('Os valores inseridos não são válidos.', 'error')
        return redirect('/conjunto')

    return redirect('/conjunto')


@app.route('/conjunto/adicionar_conta_conjunto', methods=['POST'])
@login_required
def adicionar_conta_conjunto():
    global saldo_restante, saldo_restante_2, p1, p2

    descricao = request.form['descricao'].strip()
    valor_str = request.form['valor'].strip()
    p1_str = request.form['p1'].strip()
    p2_str = request.form['p2'].strip()

    # Verifica se os campos estão vazios
    if not descricao or not valor_str or not p1_str or not p2_str:
        flash('Por favor, preencha todos os campos.', 'error')
        return redirect('/conjunto')

    # Tenta converter o valor para float
    try:
        valor = float(valor_str)
        p1 = float(p1_str)
        p2 = float(p2_str)
    except ValueError:
        flash('O valor inserido não é válido.', 'error')
        return redirect('/conjunto')

    # Verifica se a soma de p1 e p2 é igual a 100
    if p1 + p2 != 100:
        flash('A soma das porcentagens deve ser igual a 100.', 'error')
        return redirect('/conjunto')

    # Adiciona a conta ao primeiro conjunto
    contas_a_pagar.append({'descricao': descricao, 'valor': valor})
    flash('Conta adicionada com sucesso.', 'success')

    # Calcula o saldo restante para o primeiro conjunto
    total_contas_pagas = sum(conta['valor'] for conta in contas_pagas)
    saldo_restante = renda - total_contas_pagas

    # Calcula o saldo restante para o segundo conjunto
    total_contas_pagas_2 = sum(conta['valor'] for conta in contas_pagas)
    saldo_restante_2 = renda_2 - total_contas_pagas_2

    return redirect('/conjunto')


@app.route('/conjunto/pagar_conta_conjunto/<int:indice>')
@login_required
def pagar_conta_conjunto(indice):
    global saldo_restante
    global renda
    # Verifica se a lista contas_a_pagar está vazia
    if not contas_a_pagar:
        flash('Não há contas a pagar.', 'error')
        return redirect('/conjunto')

    conta = contas_a_pagar.pop(indice)
    contas_pagas.append(conta)
    return redirect('/conjunto')


@app.route('/conjunto/excluir_conta_conjunto/<int:indice>')
@login_required
def excluir_conta_conjunto(indice):
    del contas_a_pagar[indice]
    flash('Conta excluída com sucesso!', 'success')
    return redirect('/conjunto')


@app.route('/conjunto/editar_conta_conjunto/<int:indice>', methods=['GET', 'POST'])
@login_required
def editar_conta_conjunto(indice):
    global p1, p2

    if request.method == 'GET':
        if indice < 0 or indice >= len(contas_a_pagar):
            flash('Conta não encontrada.', 'error')
            return redirect('/conjunto')

        conta = contas_a_pagar[indice]
        return render_template('editar_conta_conjunto.html', indice=indice, conta=conta, p1=p1, p2=p2)

    elif request.method == 'POST':
        descricao = request.form['descricao'].strip()
        valor_str = request.form['valor'].strip()
        p1_str = request.form['p1'].strip()
        p2_str = request.form['p2'].strip()

        if not descricao or not valor_str or not p1_str or not p2_str:
            flash('Por favor, preencha todos os campos.', 'error')
            return redirect(f'/conjunto/editar_conta_conjunto/{indice}')

        try:
            valor = float(valor_str)
            p1 = float(p1_str)  # Adicione esta linha
            p2 = float(p2_str)  # Adicione esta linha
        except ValueError:
            flash('Os valores inseridos não são válidos.', 'error')
            return redirect(f'/conjunto/editar_conta_conjunto/{indice}')

        contas_a_pagar[indice]['descricao'] = descricao
        contas_a_pagar[indice]['valor'] = valor
        # Não é necessário atualizar p1 e p2 aqui, pois eles já foram atualizados acima

        flash('Conta atualizada com sucesso.', 'success')
        return redirect('/conjunto')


@app.route('/limpar_conjunto')
@login_required
def limpar_conjunto():
    global contas_a_pagar, contas_pagas, renda, saldo_restante, renda_2, saldo_restante_2
    contas_a_pagar = []
    contas_pagas = []
    renda = 0
    renda_2 = 0
    saldo_restante = 0
    saldo_restante_2 = 0
    return redirect('/conjunto')



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)


