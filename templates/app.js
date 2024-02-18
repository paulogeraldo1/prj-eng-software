new Vue({
    el: '#app',
    data: {
        renda: 0,
        saldo_restante: 0,
        novaRenda: 0,
        novaConta: {
            descricao: '',
            valor: ''
        },
        contas_a_pagar: [],
        contas_pagas: []
    },
    computed: {
        totalContasPagas: function() {
            return this.contas_pagas.reduce((total, conta) => total + conta.valor, 0);
        }
    },
    methods: {
        configurarSaldo: function() {
            this.renda = this.novaRenda;
            this.saldo_restante = this.renda - this.totalContasPagas;
        },
        adicionarConta: function() {
            this.contas_a_pagar.push({
                descricao: this.novaConta.descricao,
                valor: parseFloat(this.novaConta.valor)
            });
            this.novaConta.descricao = '';
            this.novaConta.valor = '';
        },
        pagarConta: function(index) {
            this.contas_pagas.push(this.contas_a_pagar[index]);
            this.contas_a_pagar.splice(index, 1);
            this.saldo_restante = this.renda - this.totalContasPagas;
        }
    }
});
