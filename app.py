from flask import Flask, render_template, request, redirect, flash

app = Flask(__name__)

# Variáveis globais
contas_a_pagar = []
contas_pagas = []
renda = 0
saldo_restante = 0

@app.route('/')
def index():
    # Cálculo do saldo restante
    total_contas_pagas = sum(conta['valor'] for conta in contas_pagas)
    saldo_restante = renda - total_contas_pagas
    
    return render_template('index.html', contas=contas_a_pagar, contas_pagas=contas_pagas, renda=renda, saldo_restante=saldo_restante, total_contas_pagas=total_contas_pagas)

@app.route('/configurar_saldo', methods=['POST'])
def configurar_saldo():
    global renda
    renda_str = request.form['renda'].strip()
    
    if not renda_str:
        flash('Por favor, preencha o campo de renda.', 'error')
        return redirect('/')
    
    try:
        renda = float(renda_str)
    except ValueError:
        flash('O valor da renda inserido não é válido.', 'error')
        return redirect('/')
    
    return redirect('/')


@app.route('/adicionar_conta', methods=['POST'])
def adicionar_conta():
    global saldo_restante
    descricao = request.form['descricao'].strip()  # Remove espaços em branco extras
    valor_str = request.form['valor'].strip()  # Remove espaços em branco extras
    
    # Verifica se os campos estão vazios
    if not descricao or not valor_str:
        flash('Por favor, preencha todos os campos.', 'error')
        return redirect('/')
    
    # Tenta converter o valor para float
    try:
        valor = float(valor_str)
    except ValueError:
        flash('O valor inserido não é válido.', 'error')
        return redirect('/')
    
    # Verifica se a conta já está na lista de contas pagas
    for conta in contas_pagas:
        if conta['descricao'] == descricao:
            flash('Esta conta já foi paga.', 'error')
            return redirect('/')
    
    # Verifica se a conta já está na lista de contas a pagar
    for conta in contas_a_pagar:
        if conta['descricao'] == descricao:
            flash('Esta conta já foi adicionada.', 'error')
            return redirect('/')
    
    contas_a_pagar.append({'descricao': descricao, 'valor': valor})
    flash('Conta adicionada com sucesso.', 'success')
    return redirect('/')

@app.route('/pagar_conta/<int:indice>')
def pagar_conta(indice):
    global saldo_restante
    global renda
    # Verifica se a lista contas_a_pagar está vazia
    if not contas_a_pagar:
        flash('Não há contas a pagar.', 'error')
        return redirect('/')
    
    conta = contas_a_pagar.pop(indice)
    contas_pagas.append(conta)
    return redirect('/')

@app.route('/excluir_conta/<int:indice>')
def excluir_conta(indice):
    del contas_a_pagar[indice]
    flash('Conta excluída com sucesso!', 'success')
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)