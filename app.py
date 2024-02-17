from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Lista de contas a pagar
contas_a_pagar = []

# Saldo total (salário)
renda = 0

# Saldo restante
saldo_restante = 0

@app.route('/')
def index():
    return render_template('index.html', contas=contas_a_pagar, renda=renda, saldo_restante=saldo_restante)

@app.route('/adicionar_conta', methods=['POST'])
def adicionar_conta():
    global saldo_restante
    descricao = request.form['descricao']
    valor = float(request.form['valor'])
    contas_a_pagar.append({'descricao': descricao, 'valor': valor})
    return redirect('/')

@app.route('/pagar_conta/<int:indice>')
def pagar_conta(indice):
    global saldo_restante
    conta = contas_a_pagar.pop(indice)
    saldo_restante -= conta['valor']
    return redirect('/')

@app.route('/configurar_saldo', methods=['POST'])
def configurar_saldo():
    global renda
    global saldo_restante
    renda = float(request.form['renda'])
    saldo_restante = renda
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
