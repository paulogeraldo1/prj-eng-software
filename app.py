from flask import Flask, render_template, request, redirect, flash, session, url_for, json
from functools import wraps
from autenticacao import *

app = Flask(__name__)
app.secret_key = 'qwerty1234'

contas_a_pagar = []
contas_pagas = []
renda = 0
saldo_restante = 0

# Segundo conjunto de renda e saldo restante
renda_2 = 0
saldo_restante_2 = 0
total_contas_pagas = 0 
total_contas_pagas_2 = 0

# Porcentagem
p1 = 0
p2 = 0

#autenticação
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def rota_autenticar():
    return autenticar();
    
@app.route('/logout')
@login_required
def rota_logout():
    return logout()

#salvar_dados
def salvar_dados_json(dados, arquivo):
    with open(arquivo, 'w') as arquivo:
        json.dump(dados, arquivo)

#carregar dados
def carregar_dados_json(arquivo):
    try:
        with open(arquivo, 'r') as arquivo:
            dados = json.load(arquivo)
            return dados
    except FileNotFoundError:
        return None
    
def carregar_dados_json_c(arquivo):
    try:
        with open(arquivo, 'r') as arquivo:
            dados = json.load(arquivo)
            return dados
    except FileNotFoundError:
        return None    

dados_salvos = carregar_dados_json('dados_contas.json')
if dados_salvos:
    contas_a_pagar = dados_salvos.get('contas_a_pagar', [])
    contas_pagas = dados_salvos.get('contas_pagas', [])
    renda = dados_salvos.get('renda', 0)
    saldo_restante = dados_salvos.get('saldo_restante', 0)
else:
    print('Arquivo de dados não encontrado. Iniciando com listas vazias.')
    contas_a_pagar = []
    contas_pagas = []
    renda = 0
    saldo_restante = 0

dados_salvos_c = carregar_dados_json_c('dados_contas_conjunta.json')
if dados_salvos_c:
    contas_a_pagar = dados_salvos_c.get('contas_a_pagar', [])
    contas_pagas = dados_salvos_c.get('contas_pagas', [])
    renda = dados_salvos_c.get('renda', 0)
    renda_2 = dados_salvos_c.get('renda_2', 0)
    saldo_restante = dados_salvos_c.get('saldo_restante', 0)
    saldo_restante_2 = dados_salvos_c.get('saldo_restante_2', 0)
else:
    print('Arquivo de dados não encontrado. Iniciando com listas vazias.')
    contas_a_pagar = []
    contas_pagas = []
    renda = 0
    renda_2 = 0
    saldo_restante = 0
    saldo_restante_2 = 0

#salvar contas
@app.route('/salvar_contas', methods=['GET'])
@login_required
def salvar_contas():
    global contas_a_pagar, contas_pagas, renda, saldo_restante
    dados_contas = {
        'contas_a_pagar': contas_a_pagar,
        'contas_pagas': contas_pagas,
        'renda': renda,
        'saldo_restante': saldo_restante
    }
    salvar_dados_json(dados_contas, 'dados_contas.json')
    return 'Dados das contas salvos com sucesso.'

@app.route('/salvar_contas_c', methods=['GET'])
@login_required
def salvar_contas_c():
    global contas_a_pagar, contas_pagas, renda, renda_2, saldo_restante, saldo_restante_2
    dados_contas_c = {
        'contas_a_pagar': contas_a_pagar,
        'contas_pagas': contas_pagas,
        'renda': renda,
        'renda_2': renda_2,
        'saldo_restante': saldo_restante,
        'saldo_restante_2': saldo_restante_2
    }
    salvar_dados_json(dados_contas_c, 'dados_contas_conjunta.json')
    return 'Dados das contas do conjunto salvos com sucesso.'

@app.route('/index')
@login_required
def index():
    total_contas_pagas = sum(conta['valor'] for conta in contas_pagas)
    saldo_restante = renda - total_contas_pagas
    
    salvar_contas()

    return render_template('index.html', contas=contas_a_pagar, contas_pagas=contas_pagas, renda=renda, 
                           saldo_restante=saldo_restante, total_contas_pagas=total_contas_pagas)


#operacoes
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
    
    salvar_contas()

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

    salvar_contas()

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

    salvar_contas()

    return redirect('/index')

@app.route('/excluir_conta/<int:indice>')
@login_required
def excluir_conta(indice):
    del contas_a_pagar[indice]
    flash('Conta excluída com sucesso!', 'success')

    salvar_contas()

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

        salvar_contas()

        return redirect('/index')

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

#conta conjunta
@app.route('/conjunto')
@login_required
def index_conjunto():

    total_contas_pagas = sum(conta['valor'] for conta in contas_pagas)
    saldo_restante = renda - total_contas_pagas * (p1 / 100)
    total_contas_pagas_2 = sum(conta['valor'] for conta in contas_pagas)
    saldo_restante_2 = renda_2 - total_contas_pagas_2 * (p2 / 100)

    salvar_contas_c()

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
        flash('Por favor, preencha todas as rendas.', 'error')
        return redirect('/conjunto')

    try:
        renda = float(renda_str)
        renda_2 = float(renda_2_str)
    except ValueError:
        flash('Os valores inseridos não são válidos.', 'error')
        return redirect('/conjunto')
    
    salvar_contas_c()

    return redirect('/conjunto')



@app.route('/conjunto/adicionar_conta_conjunto', methods=['POST'])
@login_required
def adicionar_conta_conjunto():
    global saldo_restante, saldo_restante_2, p1, p2

    descricao = request.form['descricao'].strip()
    valor_str = request.form['valor'].strip()
    p1_str = request.form['p1'].strip()
    p2_str = request.form['p2'].strip()
    categoria = request.form['categoria'].strip()

    if not descricao or not valor_str or not p1_str or not p2_str or not categoria:
        flash('Por favor, preencha todos os campos.', 'error')
        return redirect('/conjunto')

    try:
        valor = float(valor_str)
        p1 = float(p1_str)
        p2 = float(p2_str)
    except ValueError:
        flash('O valor inserido não é válido.', 'error')
        return redirect('/conjunto')

    if p1 + p2 != 100:
        flash('A soma das porcentagens deve ser igual a 100.', 'error')
        return redirect('/conjunto')

    contas_a_pagar.append({'descricao': descricao, 'valor': valor, 'categoria':categoria})
    flash('Conta adicionada com sucesso.', 'success')

    total_contas_pagas = sum(conta['valor'] for conta in contas_pagas)
    saldo_restante = renda - total_contas_pagas

    total_contas_pagas_2 = sum(conta['valor'] for conta in contas_pagas)
    saldo_restante_2 = renda_2 - total_contas_pagas_2

    salvar_contas_c()

    return redirect('/conjunto')


@app.route('/conjunto/pagar_conta_conjunto/<int:indice>')
@login_required
def pagar_conta_conjunto(indice):
    global saldo_restante
    global renda
    if not contas_a_pagar:
        flash('Não há contas a pagar.', 'error')
        return redirect('/conjunto')

    conta = contas_a_pagar.pop(indice)
    contas_pagas.append(conta)

    salvar_contas_c()

    return redirect('/conjunto')


@app.route('/conjunto/excluir_conta_conjunto/<int:indice>')
@login_required
def excluir_conta_conjunto(indice):
    del contas_a_pagar[indice]
    flash('Conta excluída com sucesso!', 'success')

    salvar_contas_c()

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
        categoria = request.form['categoria'].strip()

        if not descricao or not valor_str or not p1_str or not p2_str or not categoria:
            flash('Por favor, preencha todos os campos.', 'error')
            return redirect(f'/conjunto/editar_conta_conjunto/{indice}')

        try:
            valor = float(valor_str)
            p1 = float(p1_str)  
            p2 = float(p2_str)
        except ValueError:
            flash('Os valores inseridos não são válidos.', 'error')
            return redirect(f'/conjunto/editar_conta_conjunto/{indice}')

        contas_a_pagar[indice]['descricao'] = descricao
        contas_a_pagar[indice]['valor'] = valor
        contas_a_pagar[indice]['categoria'] = categoria
        flash('Conta atualizada com sucesso.', 'success')

        salvar_contas_c()

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