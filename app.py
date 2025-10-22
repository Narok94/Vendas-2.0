from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
import json
import os

app = Flask(__name__)
app.secret_key = "ivone_vendas_2025"

# Arquivo para persistência de dados
DATA_FILE = "dados_vendas.json"

# Inicializar dados
def carregar_dados():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                d = json.load(f)
                # Garantir chaves mínimas incluindo stock
                if 'clients' not in d: d['clients'] = []
                if 'sales' not in d: d['sales'] = []
                if 'payments' not in d: d['payments'] = []
                if 'stock' not in d: d['stock'] = []
                return d
        except:
            return {"clients": [], "sales": [], "payments": [], "stock": []}
    return {"clients": [], "sales": [], "payments": [], "stock": []}

def salvar_dados(dados):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2, default=str)

# Função para formatar valores monetários brasileiros
def formatar_moeda(valor):
    """Formatar valor para moeda brasileira"""
    try:
        return f"R$ {float(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        return "R$ 0,00"

# Carregar dados globais
data = carregar_dados()

# Base HTML otimizada com header de estatísticas e tamanhos reduzidos
BASE_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ivone Sistema de Vendas Profissional </title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #ff1493;
            --secondary-color: #ffe6f2;
            --accent-color: #d63384;
            --text-color: #2e1435;
            --success-color: #28a745;
            --danger-color: #dc3545;
            --warning-color: #ffc107;
        }
        
        body {
            background: linear-gradient(135deg, #ffe6f2 0%, #fff0f5 100%);
            color: var(--text-color);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 13px;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .navbar {
            background: linear-gradient(135deg, var(--primary-color) 0%, #ff69b4 100%);
            box-shadow: 0 3px 10px rgba(255, 20, 147, 0.3);
            padding: 0.5rem 0;
        }
        
        .navbar-brand {
            font-size: 1.3rem;
            font-weight: bold;
            color: white !important;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
        }
        
        /* Header de Estatísticas - Novo */
        .stats-header {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 10px 0;
            padding: 10px 15px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            align-items: center;
        }
        
        .stat-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            background: linear-gradient(135deg, var(--accent-color) 0%, var(--primary-color) 100%);
            color: white;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        .stat-icon {
            font-size: 1.2rem;
        }
        
        .container-main {
            margin-top: 1rem;
            margin-bottom: 1rem;
            padding: 0 10px;
        }
        
        .menu-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 15px;
            margin-top: 1.5rem;
        }
        
        .menu-item {
            background: white;
            border-radius: 12px;
            padding: 1.2rem;
            text-align: center;
            text-decoration: none;
            color: var(--text-color);
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }
        
        .menu-item:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.12);
            border-color: var(--accent-color);
            color: var(--text-color);
        }
        
        .menu-icon {
            font-size: 2.2rem;
            color: var(--accent-color);
            margin-bottom: 0.8rem;
        }
        
        .menu-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.3rem;
        }
        
        .menu-description {
            color: #666;
            font-size: 0.8rem;
        }
        
        .form-container {
            background: white;
            border-radius: 12px;
            padding: 1.2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 1.5rem;
        }
        
        .form-title {
            color: var(--text-color);
            font-size: 1.4rem;
            font-weight: bold;
            margin-bottom: 1.2rem;
            text-align: center;
            border-bottom: 2px solid var(--accent-color);
            padding-bottom: 0.8rem;
        }
        
        .form-group {
            margin-bottom: 1rem;
        }
        
        .form-label {
            font-weight: bold;
            color: var(--text-color);
            margin-bottom: 0.3rem;
            display: block;
            font-size: 1rem;
        }
        
        .required {
            color: var(--danger-color);
        }
        
        .form-control, .form-select {
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 8px 10px;
            font-size: 0.85rem;
            transition: all 0.3s ease;
        }
        
        .form-control:focus, .form-select:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 0.15rem rgba(214, 51, 132, 0.2);
        }
        
        .btn {
            border-radius: 6px;
            padding: 6px 12px;
            font-weight: 600;
            font-size: 0.8rem;
            transition: all 0.3s ease;
            margin: 2px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--accent-color) 0%, var(--primary-color) 100%);
            border: none;
        }
        
        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(214, 51, 132, 0.3);
        }
        
        .btn-secondary {
            background: #6c757d;
            border: none;
        }
        
        .btn-sm {
            padding: 4px 8px;
            font-size: 0.75rem;
        }
        
        .table-container {
            background: white;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            overflow-x: auto;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .table {
            margin-bottom: 0;
            font-size: 0.8rem;
        }
        
        .table th {
            background: linear-gradient(135deg, var(--accent-color) 0%, var(--primary-color) 100%);
            color: white;
            border: none;
            padding: 8px 10px;
            font-weight: 600;
            text-align: center;
            font-size: 0.8rem;
        }
        
        .table td {
            padding: 6px 8px;
            vertical-align: middle;
            text-align: center;
            border-bottom: 1px solid #e9ecef;
            font-size: 0.8rem;
        }
        
        .table tbody tr:hover {
            background-color: #f8f9fa;
        }
        
        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 6px;
        }
        
        .status-paid { background-color: var(--success-color); }
        .status-pending { background-color: var(--danger-color); }
        
        .badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 600;
        }
        
        .badge-success { background-color: var(--success-color); color: white; }
        .badge-danger { background-color: var(--danger-color); color: white; }
        .badge-warning { background-color: var(--warning-color); color: var(--text-color); }
        
        .alert {
            border-radius: 8px;
            border: none;
            padding: 0.8rem 1rem;
            margin-bottom: 1rem;
            font-size: 0.85rem;
        }
        
        .footer {
            background: var(--text-color);
            color: white;
            text-align: center;
            padding: 1.5rem 0;
            margin-top: 2rem;
            font-size: 0.8rem;
        }
        
        .search-box {
            background: white;
            border-radius: 8px;
            padding: 0.8rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        
        .quick-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-bottom: 1.5rem;
        }
        
        .stat-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        
        .stat-number {
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--accent-color);
        }
        
        .stat-label {
            color: #666;
            font-size: 0.8rem;
            margin-top: 0.3rem;
        }
        
        .btn-group-sm .btn {
            padding: 2px 6px;
            font-size: 0.7rem;
        }
        
        /* Estilos para estoque zerado */
        .estoque-zerado { 
            background-color: #ffebee !important; 
            color: var(--danger-color) !important; 
            font-weight: bold;
        }
        .quantidade-zero {
            color: var(--danger-color) !important;
            font-weight: bold;
            background-color: #ffebee;
            padding: 2px 6px;
            border-radius: 4px;
        }
        .produto-indisponivel {
            color: #999 !important;
            font-style: italic;
        }
        
        @media (max-width: 768px) {
            .menu-grid {
                grid-template-columns: 1fr;
            }
            .stats-grid {
                grid-template-columns: 1fr;
            }
            .container-main {
                padding: 0 5px;
            }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="container-fluid">
            <span class="navbar-brand">
                <i class="fas fa-store"></i> Ivone  Sistema de Vendas
            </span>
        </div>
    </nav>

    <!-- Header de Estatísticas -->
    <div class="container-fluid">
        <div class="stats-header">
            <div class="stats-grid">
                <div class="stat-item">
                    <i class="fas fa-users stat-icon"></i>
                    <span>{{ total_clients }} Clientes</span>
                </div>
                <div class="stat-item">
                    <i class="fas fa-chart-line stat-icon"></i>
                    <span>{{ vendas_totais }}</span>
                </div>
                <div class="stat-item">
                    <i class="fas fa-money-bill-wave stat-icon"></i>
                    <span>{{ recebimentos_totais }}</span>
                </div>
                <div class="stat-item">
                    <i class="fas fa-clock stat-icon"></i>
                    <span>{{ saldo_pendente }}</span>
                </div>
            </div>
        </div>
    </div>

    <div class="container-fluid container-main">
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, msg in messages %}
              <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }}">
                <i class="fas fa-{{ 'check-circle' if category == 'success' else 'exclamation-triangle' }}"></i>
                {{ msg }}
              </div>
            {% endfor %}
          {% endif %}
        {% endwith %}
        
        {{ content|safe }}
    </div>

    <footer class="footer">
        <div class="container">
            <p><i class="fas fa-heart"></i>  2025 Henrique Costa Sistema de Vendas Profissional <i class="fas fa-heart"></i></p>
            
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Limpar formulário automaticamente após submissão
        document.addEventListener('DOMContentLoaded', function() {
            const forms = document.querySelectorAll('form');
            forms.forEach(form => {
                form.addEventListener('submit', function() {
                    // Aguardar processamento e limpar formulário
                    setTimeout(function() {
                        if (window.location.href.includes('cadastrar_cliente') || 
                            window.location.href.includes('vendas') || 
                            window.location.href.includes('pagamentos')) {
                            form.reset();
                        }
                    }, 100);
                });
            });
        });
        
        // Função para limpar formulário manualmente
        function limparFormulario() {
            const forms = document.querySelectorAll('form');
            forms.forEach(form => form.reset());
        }
        
        // Confirm delete actions
        function confirmDelete(message) {
            return confirm(message || 'Tem certeza que deseja excluir este item?');
        }
        
        // Máscara para CPF
        function mascaraCPF(input) {
            let value = input.value.replace(/\\D/g, '');
            value = value.replace(/(\\d{3})(\\d)/, '$1.$2');
            value = value.replace(/(\\d{3})(\\d)/, '$1.$2');
            value = value.replace(/(\\d{3})(\\d{1,2})$/, '$1-$2');
            input.value = value;
        }
        
        // Máscara para telefone
        function mascaraTelefone(input) {
            let value = input.value.replace(/\\D/g, '');
            if (value.length <= 10) {
                value = value.replace(/(\\d{2})(\\d)/, '($1) $2');
                value = value.replace(/(\\d{4})(\\d)/, '$1-$2');
            } else {
                value = value.replace(/(\\d{2})(\\d)/, '($1) $2');
                value = value.replace(/(\\d{5})(\\d)/, '$1-$2');
            }
            input.value = value;
        }
    </script>
</body>
</html>
"""

def render_page(content, **kwargs):
    # Calcular estatísticas para o header
    total_clients = len(data['clients'])
    
    # Calcular vendas totais
    total_vendas_valor = 0
    for sale in data['sales']:
        try:
            total_vendas_valor += float(sale.get('amount', 0))
        except (ValueError, TypeError):
            continue
    
    # Calcular recebimentos totais
    total_recebimentos_valor = 0
    for payment in data['payments']:
        try:
            total_recebimentos_valor += float(payment.get('value', 0))
        except (ValueError, TypeError):
            continue
    
    # Calcular saldo pendente
    saldo_pendente_valor = total_vendas_valor - total_recebimentos_valor
    
    template_vars = {
        'content': content,
        'total_clients': total_clients,
        'vendas_totais': f"Vendas: {formatar_moeda(total_vendas_valor)}",
        'recebimentos_totais': f"Recebimentos: {formatar_moeda(total_recebimentos_valor)}",
        'saldo_pendente': f"Pendente: {formatar_moeda(abs(saldo_pendente_valor))}"
    }
    template_vars.update(kwargs)
    
    return render_template_string(BASE_HTML, **template_vars)

@app.route('/')
def dashboard():
    # Dashboard agora inclui o menu de estoque
    content = """
    <div class="menu-grid">
        <a href="/cadastrar_cliente" class="menu-item">
            <div class="menu-icon"><i class="fas fa-user-plus"></i></div>
            <div class="menu-title">Cadastrar Cliente</div>
            <div class="menu-description">Adicionar novos clientes</div>
        </a>
        <a href="/estoque" class="menu-item">
            <div class="menu-icon"><i class="fas fa-boxes"></i></div>
            <div class="menu-title">🧺 Estoque</div>
            <div class="menu-description">Gerenciar produtos em estoque</div>
        </a>
        <a href="/vendas" class="menu-item">
            <div class="menu-icon"><i class="fas fa-shopping-cart"></i></div>
            <div class="menu-title">Nova Venda</div>
            <div class="menu-description">Registrar vendas</div>
        </a>
        <a href="/pagamentos" class="menu-item">
            <div class="menu-icon"><i class="fas fa-credit-card"></i></div>
            <div class="menu-title">Receber Pagamento</div>
            <div class="menu-description">Registrar pagamentos</div>
        </a>
        <a href="/clientes" class="menu-item">
            <div class="menu-icon"><i class="fas fa-address-book"></i></div>
            <div class="menu-title">Gerenciar Clientes</div>
            <div class="menu-description">Visualizar e editar</div>
        </a>
        <a href="/relatorios" class="menu-item">
            <div class="menu-icon"><i class="fas fa-chart-bar"></i></div>
            <div class="menu-title">Relatorios</div>
            <div class="menu-description">Anlises e estatsticas</div>
        </a>
        <a href="/historico" class="menu-item">
            <div class="menu-icon"><i class="fas fa-history"></i></div>
            <div class="menu-title">Historico</div>
            <div class="menu-description">Todas as transaes</div>
        </a>
    </div>
    """
    
    return render_page(content)

# --- Estoque ---
@app.route('/estoque', methods=['GET','POST'])
def estoque():
    # Adicionar produto
    if request.method == 'POST':
        nome = request.form.get('name','').strip()
        categoria = request.form.get('category','').strip()
        codigo = request.form.get('code','').strip()
        tamanho = request.form.get('size','').strip()
        quantidade = request.form.get('quantity','0').strip()
        
        try:
            quantidade_int = int(quantidade)
            if quantidade_int < 0:
                raise ValueError()
        except:
            flash("Quantidade inválida!", "danger")
            return redirect(url_for('estoque'))
        
        if not nome or not categoria or not codigo:
            flash("Nome, categoria e código são obrigatórios!", "danger")
            return redirect(url_for('estoque'))
        
        # Verificar se produto já existe
        for produto in data['stock']:
            if produto.get('code','').lower() == codigo.lower():
                flash(f"Produto com código {codigo} já existe!", "danger")
                return redirect(url_for('estoque'))
        
        novo = {
            'id': len(data['stock']) + 1,
            'name': nome,
            'category': categoria,
            'code': codigo,
            'size': tamanho if tamanho else None,
            'quantity': quantidade_int
        }
        data['stock'].append(novo)
        salvar_dados(data)
        flash(f"Produto '{nome}' adicionado ao estoque!", "success")
        return redirect(url_for('estoque'))

    # Listar estoque
    rows = ""
    produtos_zerados = 0
    if not data['stock']:
        rows = "<tr><td colspan='7' class='text-center py-3'>Nenhum produto no estoque.</td></tr>"
    else:
        for p in data['stock']:
            size_display = p.get('size') or '-'
            quantidade = p.get('quantity', 0)
            
            # Aplicar estilo para estoque zerado
            row_class = "estoque-zerado" if quantidade == 0 else ""
            quantidade_class = "quantidade-zero" if quantidade == 0 else ""
            
            if quantidade == 0:
                produtos_zerados += 1
            
            rows += f"""
            <tr class="{row_class}">
                <td>{p.get('id')}</td>
                <td>{p.get('name')}</td>
                <td>{p.get('category')}</td>
                <td>{p.get('code')}</td>
                <td>{size_display}</td>
                <td><span class="{quantidade_class}">{quantidade}</span></td>
                <td>
                    <a href="/editar_produto/{p.get('id')}" class="btn btn-sm btn-outline-primary">Editar</a>
                    <a href="/excluir_produto/{p.get('id')}" class="btn btn-sm btn-outline-danger" onclick="return confirm('Excluir produto?')">Excluir</a>
                </td>
            </tr>
            """
    
    # Alerta para produtos com estoque zerado
    alerta_estoque = ""
    if produtos_zerados > 0:
        alerta_estoque = f'<div class="alert alert-danger"><i class="fas fa-exclamation-triangle"></i> <strong>Atenção!</strong> Você tem {produtos_zerados} produto(s) com estoque zerado.</div>'
    
    content = f"""
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h4><i class="fas fa-boxes"></i> Estoque</h4>
    </div>
    {alerta_estoque}
    <div class="form-container">
        <h5>Adicionar Produto</h5>
        <form method="post">
            <div class="row">
                <div class="col-md-4"><div class="form-group"><label class="form-label">Nome do Produto</label><input class="form-control" name="name" required></div></div>
                <div class="col-md-3"><div class="form-group"><label class="form-label">Categoria</label>
                    <select class="form-control" name="category" required onchange="toggleSize(this.value)">
                        <option value="">Selecione</option>
                        <option value="Natura">Natura</option>
                        <option value="Boticário">Boticário</option>
                        <option value="Ouseuse">Ouseuse</option>
                    </select></div></div>
                <div class="col-md-2"><div class="form-group"><label class="form-label">Código</label><input class="form-control" name="code" required></div></div>
                <div class="col-md-1"><div class="form-group"><label class="form-label">Tamanho</label><input class="form-control" name="size" placeholder="(opcional)"></div></div>
                <div class="col-md-2"><div class="form-group"><label class="form-label">Quantidade</label><input class="form-control" type="number" name="quantity" value="1" min="0" required></div></div>
            </div>
            <div class="mt-2"><button class="btn btn-primary" type="submit"><i class="fas fa-plus"></i> Adicionar</button></div>
        </form>
    </div>
    <div class="table-container mt-3">
        <table class="table table-striped">
            <thead><tr><th>ID</th><th>Nome</th><th>Categoria</th><th>Código</th><th>Tamanho</th><th>Quantidade</th><th>Ações</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    <div class="mt-3"><a href='/' class='btn btn-secondary btn-sm'><i class='fas fa-home'></i> Voltar ao Dashboard</a></div>
    <script>
        function toggleSize(val) {{ /* reserve - caso queira lógica no futuro */ }}
    </script>
    """
    return render_page(content)

@app.route('/editar_produto/<int:prod_id>', methods=['GET','POST'])
def editar_produto(prod_id):
    produto = next((p for p in data['stock'] if p.get('id')==prod_id), None)
    if not produto:
        flash("Produto não encontrado!", "danger")
        return redirect(url_for('estoque'))
    
    if request.method == 'POST':
        nome = request.form.get('name','').strip()
        categoria = request.form.get('category','').strip()
        codigo = request.form.get('code','').strip()
        tamanho = request.form.get('size','').strip()
        quantidade = request.form.get('quantity','0').strip()
        
        try:
            quantidade_int = int(quantidade)
            if quantidade_int < 0: 
                raise ValueError()
        except:
            flash("Quantidade inválida!", "danger")
            return redirect(url_for('editar_produto', prod_id=prod_id))
        
        if not nome or not categoria or not codigo:
            flash("Nome, categoria e código são obrigatórios!", "danger")
            return redirect(url_for('editar_produto', prod_id=prod_id))
        
        produto.update({'name':nome,'category':categoria,'code':codigo,'size':tamanho or None,'quantity':quantidade_int})
        salvar_dados(data)
        flash("Produto atualizado!", "success")
        return redirect(url_for('estoque'))
    
    content = f"""
    <div class="form-container">
        <h4>Editar Produto</h4>
        <form method="post">
            <div class="row">
                <div class="col-md-4"><label class="form-label">Nome</label><input class="form-control" name="name" value="{produto.get('name')}" required></div>
                <div class="col-md-3"><label class="form-label">Categoria</label>
                    <select class="form-control" name="category" required>
                        <option value="Natura" {'selected' if produto.get('category')=='Natura' else ''}>Natura</option>
                        <option value="Boticário" {'selected' if produto.get('category')=='Boticário' else ''}>Boticário</option>
                        <option value="Ouseuse" {'selected' if produto.get('category')=='Ouseuse' else ''}>Ouseuse</option>
                    </select></div>
                <div class="col-md-2"><label class="form-label">Código</label><input class="form-control" name="code" value="{produto.get('code')}" required></div>
                <div class="col-md-1"><label class="form-label">Tamanho</label><input class="form-control" name="size" value="{produto.get('size') or ''}"></div>
                <div class="col-md-2"><label class="form-label">Quantidade</label><input class="form-control" type="number" name="quantity" value="{produto.get('quantity')}" min="0" required></div>
            </div>
            <div class="mt-2"><button class="btn btn-primary" type="submit">Salvar</button> <a class="btn btn-secondary" href="/estoque">Cancelar</a></div>
        </form>
    </div>
    """
    return render_page(content)

@app.route('/excluir_produto/<int:prod_id>')
def excluir_produto(prod_id):
    produto = next((p for p in data['stock'] if p.get('id')==prod_id), None)
    if not produto:
        flash("Produto não encontrado!", "danger")
    else:
        data['stock'] = [p for p in data['stock'] if p.get('id')!=prod_id]
        salvar_dados(data)
        flash("Produto excluído do estoque!", "success")
    return redirect(url_for('estoque'))

# API para buscar produto por código
@app.route('/api/produto/<codigo>')
def api_produto(codigo):
    produto = next((p for p in data['stock'] if p.get('code','').lower() == codigo.lower()), None)
    if produto:
        return jsonify({
            'success': True,
            'produto': {
                'id': produto.get('id'),
                'name': produto.get('name'),
                'code': produto.get('code'),
                'quantity': produto.get('quantity', 0),
                'category': produto.get('category'),
                'size': produto.get('size')
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Produto não encontrado'})

@app.route('/cadastrar_cliente', methods=['GET', 'POST'])
def cadastrar_cliente():
    if request.method == 'POST':
        nome = request.form.get('name', '').strip()
        telefone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        endereco = request.form.get('address', '').strip()
        cpf = request.form.get('cpf', '').strip()
        observacoes = request.form.get('observacoes', '').strip()
        
        if not nome:
            flash("Nome é obrigatório!", "danger")
            return redirect(url_for('cadastrar_cliente'))
        
        if not telefone:
            flash("Telefone é obrigatório!", "danger")
            return redirect(url_for('cadastrar_cliente'))
        
        # Verificar se cliente já existe
        for cliente in data['clients']:
            if cliente['name'].lower() == nome.lower():
                flash(f"Cliente {nome} já está cadastrado!", "danger")
                return redirect(url_for('cadastrar_cliente'))
        
        try:
            novo_cliente = {
                'id': len(data['clients']) + 1,
                'name': nome,
                'phone': telefone,
                'email': email,
                'address': endereco,
                'cpf': cpf,
                'data_cadastro': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'observacoes': observacoes
            }
            
            data['clients'].append(novo_cliente)
            salvar_dados(data)
            flash(f"Cliente {novo_cliente['name']} cadastrado com sucesso!", "success")
            return redirect(url_for('listar_clientes'))
            
        except Exception as e:
            flash(f"Erro ao cadastrar cliente: {str(e)}", "danger")
            return redirect(url_for('cadastrar_cliente'))

    content = """
    <div class="form-container">
        <h2 class="form-title"><i class="fas fa-user-plus"></i> Cadastrar Novo Cliente</h2>
        <form method="post" id="clienteForm" onsubmit="return validarFormulario()">
            <div class="row">
                <div class="col-md-6">
                    <div class="form-group">
                        <label class="form-label">Nome Completo <span class="required">*</span></label>
                        <input type="text" class="form-control" name="name" required 
                               pattern="[A-Za-zÀ-ÿ\\s]+" title="Digite apenas letras e espaços"
                               minlength="2" maxlength="100">
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="form-group">
                        <label class="form-label">Telefone <span class="required">*</span></label>
                        <input type="tel" class="form-control" name="phone" required
                               placeholder="(11) 99999-9999" onkeyup="mascaraTelefone(this)" maxlength="15">
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <div class="form-group">
                        <label class="form-label">E-mail</label>
                        <input type="email" class="form-control" name="email" 
                               placeholder="cliente@email.com">
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="form-group">
                        <label class="form-label">CPF</label>
                        <input type="text" class="form-control" name="cpf" 
                               placeholder="000.000.000-00" onkeyup="mascaraCPF(this)" maxlength="14">
                    </div>
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">Endereço Completo</label>
                <input type="text" class="form-control" name="address" 
                       placeholder="Rua, número, bairro, cidade" maxlength="200">
            </div>
            <div class="form-group">
                <label class="form-label">Observações</label>
                <textarea class="form-control" name="observacoes" rows="2" 
                          placeholder="Informações adicionais sobre o cliente" maxlength="500"></textarea>
            </div>
            <div class="d-flex gap-2">
                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-save"></i> Cadastrar Cliente
                </button>
                <button type="button" class="btn btn-secondary" onclick="limparFormulario()">
                    <i class="fas fa-eraser"></i> Limpar
                </button>
                <a href="/" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Voltar
                </a>
            </div>
        </form>
    </div>
    
    <script>
        function validarFormulario() {
            const nome = document.querySelector('input[name="name"]').value.trim();
            const telefone = document.querySelector('input[name="phone"]').value.trim();
            
            if (nome.length < 2) {
                alert('Nome deve ter pelo menos 2 caracteres');
                return false;
            }
            
            if (telefone.length < 10) {
                alert('Telefone deve ter pelo menos 10 dígitos');
                return false;
            }
            
            return true;
        }
    </script>
    """
    
    return render_page(content)

@app.route('/clientes')
def listar_clientes():
    search = request.args.get('search', '')
    
    clients_filtered = data['clients']
    if search:
        clients_filtered = [c for c in data['clients'] 
                          if search.lower() in c['name'].lower() 
                          or search.lower() in c.get('phone', '').lower()]
    
    if not clients_filtered:
        rows = "<tr><td colspan='8' class='text-center py-3'>Nenhum cliente encontrado.</td></tr>"
    else:
        rows = ""
        for i, c in enumerate(clients_filtered):
            # Calcular saldo do cliente
            vendas_cliente = 0
            pagamentos_cliente = 0
            
            for venda in data['sales']:
                if venda.get('client') == c['name']:
                    try:
                        vendas_cliente += float(venda.get('amount', 0))
                    except (ValueError, TypeError):
                        continue
            
            for pagamento in data['payments']:
                if pagamento.get('client') == c['name']:
                    try:
                        pagamentos_cliente += float(pagamento.get('value', 0))
                    except (ValueError, TypeError):
                        continue
            
            saldo = vendas_cliente - pagamentos_cliente
            
            status_class = "status-pending" if saldo > 0 else "status-paid"
            status_text = "Devendo" if saldo > 0 else "Em dia"
            badge_class = "badge-danger" if saldo > 0 else "badge-success"
            
            client_index = data['clients'].index(c)
            vendas_count = len([v for v in data['sales'] if v.get('client') == c['name']])
            
            rows += f"""
            <tr>
                <td><span class="status-indicator {status_class}"></span></td>
                <td><strong>{c['name']}</strong></td>
                <td>{c.get('phone', 'N/A')}</td>
                <td>{c.get('email', 'N/A')}</td>
                <td>{formatar_moeda(abs(saldo))}</td>
                <td><span class="badge {badge_class}">{status_text}</span></td>
                <td>{vendas_count}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <a href="/editar_cliente/{client_index}" class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-edit"></i>
                        </a>
                        <a href="/excluir_cliente/{client_index}" class="btn btn-outline-danger btn-sm" 
                           onclick="return confirmDelete('Excluir cliente {c['name']}?')">
                            <i class="fas fa-trash"></i>
                        </a>
                    </div>
                </td>
            </tr>
            """
    
    content = f"""
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h4><i class="fas fa-users"></i> Gerenciar Clientes</h4>
        <a href="/cadastrar_cliente" class="btn btn-primary btn-sm">
            <i class="fas fa-plus"></i> Novo Cliente
        </a>
    </div>
    
    <div class="search-box">
        <form method="get" class="d-flex gap-2">
            <input type="text" class="form-control" name="search" value="{search}" 
                   placeholder="Buscar por nome ou telefone...">
            <button type="submit" class="btn btn-primary btn-sm">
                <i class="fas fa-search"></i> Buscar
            </button>
            <a href="/clientes" class="btn btn-secondary btn-sm">
                <i class="fas fa-times"></i> Limpar
            </a>
        </form>
    </div>
    
    <div class="table-container">
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Status</th>
                    <th>Nome</th>
                    <th>Telefone</th>
                    <th>E-mail</th>
                    <th>Saldo</th>
                    <th>Situação</th>
                    <th>Vendas</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    
    <div class="mt-3">
        <a href="/" class="btn btn-secondary btn-sm">
            <i class="fas fa-home"></i> Voltar ao Dashboard
        </a>
    </div>
    """
    
    return render_page(content)

@app.route('/vendas', methods=['GET', 'POST'])
def registrar_venda():
    if request.method == 'POST':
        try:
            cliente = request.form.get('client', '').strip()
            codigo_produto = request.form.get('product_code', '').strip()
            product_id = request.form.get('product_id', '').strip()
            amount = request.form.get('amount', '').strip()
            quantity = request.form.get('quantity', '1').strip()
            data_venda = request.form.get('data_venda', '').strip()
            observacoes = request.form.get('observacoes', '').strip()
            
            if not cliente:
                flash("Selecione um cliente!", "danger")
                return redirect(url_for('registrar_venda'))
            
            if not product_id:
                flash("Selecione um produto!", "danger")
                return redirect(url_for('registrar_venda'))
            
            try:
                quantidade_int = int(quantity)
                if quantidade_int <= 0:
                    flash("Quantidade deve ser maior que zero!", "danger")
                    return redirect(url_for('registrar_venda'))
            except:
                flash("Quantidade inválida!", "danger")
                return redirect(url_for('registrar_venda'))
            
            try:
                valor_float = float(amount)
                if valor_float <= 0:
                    flash("Valor deve ser maior que zero!", "danger")
                    return redirect(url_for('registrar_venda'))
            except:
                flash("Valor inválido!", "danger")
                return redirect(url_for('registrar_venda'))

            produto = next((p for p in data['stock'] if str(p.get('id'))==str(product_id)), None)
            if not produto:
                flash("Produto não encontrado no estoque!", "danger")
                return redirect(url_for('registrar_venda'))

            # Verificação específica para estoque zerado
            if produto.get('quantity',0) == 0:
                flash(f"❌ PRODUTO SEM ESTOQUE! O produto '{produto.get('name')}' está com estoque zerado e não pode ser vendido.", "danger")
                return redirect(url_for('registrar_venda'))

            if produto.get('quantity',0) < quantidade_int:
                flash(f"Estoque insuficiente para '{produto.get('name')}'. Disponível: {produto.get('quantity',0)} unidade(s)", "danger")
                return redirect(url_for('registrar_venda'))

            # Registrar venda e abater do estoque
            nova_venda = {
                'id': len(data['sales']) + 1,
                'client': cliente,
                'product_id': produto.get('id'),
                'product': produto.get('name'),
                'amount': valor_float * quantidade_int,
                'unit_price': valor_float,
                'quantity': quantidade_int,
                'data_venda': data_venda,
                'observacoes': observacoes,
                'data_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            data['sales'].append(nova_venda)
            produto['quantity'] = produto.get('quantity',0) - quantidade_int
            salvar_dados(data)
            flash(f"✅ Venda registrada: {quantidade_int}x {produto.get('name')} por {formatar_moeda(nova_venda['amount'])}", "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f"Erro ao registrar venda: {str(e)}", "danger")
            return redirect(url_for('registrar_venda'))

    client_options = "".join([f"<option value='{c['name']}'>{c['name']}</option>" for c in data['clients']]) or "<option value=''>Nenhum cliente cadastrado</option>"
    
    # Separar produtos disponíveis dos indisponíveis
    produtos_disponiveis = []
    produtos_indisponiveis = []
    
    for p in data['stock']:
        if p.get('quantity', 0) > 0:
            produtos_disponiveis.append(f"<option value='{p['id']}' data-qty='{p.get('quantity',0)}' data-name='{p.get('name')}' data-code='{p.get('code')}' data-size='{p.get('size') or ''}'>{p['name']} (Disponível: {p.get('quantity',0)})</option>")
        else:
            produtos_indisponiveis.append(f"<option value='' class='produto-indisponivel' disabled>❌ {p['name']} (SEM ESTOQUE)</option>")
    
    product_options = ""
    if produtos_disponiveis:
        product_options += "".join(produtos_disponiveis)
    if produtos_indisponiveis:
        product_options += "".join(produtos_indisponiveis)
    
    if not product_options:
        product_options = "<option value=''>Nenhum produto disponível</option>"
    
    data_hoje = date.today().strftime("%Y-%m-%d")
    
    warning_clients = '<div class="alert alert-warning"><i class="fas fa-exclamation-triangle"></i> Cadastre pelo menos um cliente antes de registrar vendas. <a href="/cadastrar_cliente">Cadastrar Cliente</a></div>' if not data['clients'] else ''
    warning_stock = '<div class="alert alert-warning"><i class="fas fa-exclamation-triangle"></i> Cadastre pelo menos um produto no estoque antes de registrar vendas. <a href="/estoque">Ir para Estoque</a></div>' if not data['stock'] else ''
    
    content = f"""
    <div class="form-container">
        <h2 class="form-title"><i class="fas fa-shopping-cart"></i> Registrar Nova Venda</h2>
        {warning_clients}
        {warning_stock}
        <form method="post" id="vendaForm">
            <div class="row">
                <div class="col-md-6"><div class="form-group"><label class="form-label">Cliente</label><select class="form-control" name="client" required><option value=''>Selecione um cliente</option>{client_options}</select></div></div>
                <div class="col-md-3"><div class="form-group"><label class="form-label">Data da Venda</label><input class="form-control" type="date" name="data_venda" value="{data_hoje}" required></div></div>
            </div>
            <div class="row mt-2">
                <div class="col-md-3"><div class="form-group"><label class="form-label">Código do Produto</label><input class="form-control" type="text" name="product_code" id="productCode" placeholder="Digite o código"></div></div>
                <div class="col-md-5"><div class="form-group"><label class="form-label">Produto</label><select class="form-control" name="product_id" required id="productSelect"><option value=''>Selecione um produto</option>{product_options}</select></div></div>
                <div class="col-md-2"><div class="form-group"><label class="form-label">Quantidade</label><input class="form-control" type="number" name="quantity" value="1" min="1" required id="quantityInput"></div></div>
                <div class="col-md-2"><div class="form-group"><label class="form-label">Valor unitário (R$)</label><input class="form-control" type="number" step="0.01" name="amount" required id="unitPrice"></div></div>
            </div>
            <div class="form-group mt-2"><label class="form-label">Observações</label><textarea class="form-control" name="observacoes" rows="2"></textarea></div>
            <div class="mt-2"><button class="btn btn-primary" type="submit" {'disabled' if not data['clients'] or not any(p.get('quantity', 0) > 0 for p in data['stock']) else ''}><i class="fas fa-save"></i> Registrar Venda</button> <a class="btn btn-secondary" href="/">Voltar</a></div>
        </form>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function(){{
            const productCode = document.getElementById('productCode');
            const productSelect = document.getElementById('productSelect');
            const unitPrice = document.getElementById('unitPrice');
            const quantityInput = document.getElementById('quantityInput');
            
            // Buscar produto por código
            productCode.addEventListener('blur', function(){{
                const codigo = this.value.trim();
                if (codigo) {{
                    fetch(`/api/produto/${{codigo}}`)
                        .then(response => response.json())
                        .then(data => {{
                            if (data.success) {{
                                productSelect.value = data.produto.id;
                                updateFields();
                            }} else {{
                                alert('Produto não encontrado com este código');
                                productCode.value = '';
                            }}
                        }})
                        .catch(error => console.error('Erro:', error));
                }}
            }});
            
            function updateFields(){{
                const opt = productSelect.options[productSelect.selectedIndex];
                if(!opt || !opt.value) {{
                    quantityInput.max = 0;
                    return;
                }}
                const available = opt.getAttribute('data-qty') || '0';
                const code = opt.getAttribute('data-code') || '';
                quantityInput.max = available;
                quantityInput.value = Math.min(quantityInput.value, available);
                productCode.value = code;
                
                if(parseInt(available) <= 5 && parseInt(available) > 0) {{
                    console.log('Produto com estoque baixo: ' + available + ' unidades');
                }}
            }}
            productSelect.addEventListener('change', updateFields);
            updateFields();
        }});
    </script>
    """
    return render_page(content)

@app.route('/pagamentos', methods=['GET', 'POST'])
def registrar_pagamento():
    if request.method == 'POST':
        try:
            cliente = request.form.get('client', '').strip()
            valor = request.form.get('value', '').strip()
            data_pagamento = request.form.get('data_pagamento', '').strip()
            observacoes = request.form.get('observacoes', '').strip()
            
            if not cliente:
                flash("Selecione um cliente!", "danger")
                return redirect(url_for('registrar_pagamento'))
            
            if not valor:
                flash("Valor é obrigatório!", "danger")
                return redirect(url_for('registrar_pagamento'))
            
            try:
                valor_float = float(valor.replace(',', '.'))
                if valor_float <= 0:
                    flash("Valor deve ser maior que zero!", "danger")
                    return redirect(url_for('registrar_pagamento'))
            except ValueError:
                flash("Valor inválido!", "danger")
                return redirect(url_for('registrar_pagamento'))
            
            # Verificar saldo do cliente
            vendas_cliente = 0
            pagamentos_cliente = 0
            
            for venda in data['sales']:
                if venda.get('client') == cliente:
                    try:
                        vendas_cliente += float(venda.get('amount', 0))
                    except (ValueError, TypeError):
                        continue
            
            for pagamento in data['payments']:
                if pagamento.get('client') == cliente:
                    try:
                        pagamentos_cliente += float(pagamento.get('value', 0))
                    except (ValueError, TypeError):
                        continue
            
            saldo_devedor = vendas_cliente - pagamentos_cliente
            
            if valor_float > saldo_devedor:
                flash(f"Atenção! Pagamento maior que o saldo devedor. Saldo atual: {formatar_moeda(saldo_devedor)}", "danger")
                return redirect(url_for('registrar_pagamento'))
            
            novo_pagamento = {
                'id': len(data['payments']) + 1,
                'client': cliente,
                'value': valor_float,
                'data_pagamento': data_pagamento,
                'observacoes': observacoes,
                'data_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            data['payments'].append(novo_pagamento)
            salvar_dados(data)
            
            flash(f"Pagamento de {formatar_moeda(valor_float)} registrado para {cliente}!", "success")
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash(f"Erro ao registrar pagamento: {str(e)}", "danger")
            return redirect(url_for('registrar_pagamento'))

    # Clientes com saldo devedor
    clientes_com_saldo = []
    for client in data['clients']:
        vendas_cliente = 0
        pagamentos_cliente = 0
        
        for venda in data['sales']:
            if venda.get('client') == client['name']:
                try:
                    vendas_cliente += float(venda.get('amount', 0))
                except (ValueError, TypeError):
                    continue
        
        for pagamento in data['payments']:
            if pagamento.get('client') == client['name']:
                try:
                    pagamentos_cliente += float(pagamento.get('value', 0))
                except (ValueError, TypeError):
                    continue
        
        saldo = vendas_cliente - pagamentos_cliente
        if saldo > 0:
            clientes_com_saldo.append({
                'name': client['name'],
                'saldo': saldo
            })
    
    client_options = "".join([
        f"<option value='{c['name']}'>{c['name']} (Saldo: {formatar_moeda(c['saldo'])})</option>" 
        for c in clientes_com_saldo
    ])
    
    data_hoje = date.today().strftime("%Y-%m-%d")
    
    content = f"""
    <div class="form-container">
        <h2 class="form-title"><i class="fas fa-credit-card"></i> Registrar Pagamento</h2>
        
        {'<div class="alert alert-warning"><i class="fas fa-info-circle"></i> Nenhum cliente possui saldo devedor no momento.</div>' if not clientes_com_saldo else ''}
        
        <form method="post" id="pagamentoForm" onsubmit="return validarPagamento()">
            <div class="row">
                <div class="col-md-6">
                    <div class="form-group">
                        <label class="form-label">Cliente <span class="required">*</span></label>
                        <select class="form-control" name="client" required>
                            <option value="">Selecione um cliente</option>
                            {client_options}
                        </select>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="form-group">
                        <label class="form-label">Data do Pagamento <span class="required">*</span></label>
                        <input type="date" class="form-control" name="data_pagamento" value="{data_hoje}" required>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <div class="form-group">
                        <label class="form-label">Valor Recebido (R$) <span class="required">*</span></label>
                        <input type="number" class="form-control" name="value" step="0.01" min="0.01" required 
                               placeholder="0,00">
                    </div>
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">Observações</label>
                <textarea class="form-control" name="observacoes" rows="2" 
                          placeholder="Forma de pagamento, observações, etc." maxlength="500"></textarea>
            </div>
            <div class="d-flex gap-2">
                <button type="submit" class="btn btn-primary" {'disabled' if not clientes_com_saldo else ''}>
                    <i class="fas fa-save"></i> Registrar Pagamento
                </button>
                <button type="button" class="btn btn-secondary" onclick="limparFormulario()">
                    <i class="fas fa-eraser"></i> Limpar
                </button>
                <a href="/" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Voltar
                </a>
            </div>
        </form>
    </div>
    
    <script>
        function validarPagamento() {{
            const cliente = document.querySelector('select[name="client"]').value;
            const valor = document.querySelector('input[name="value"]').value;
            
            if (!cliente) {{
                alert('Selecione um cliente');
                return false;
            }}
            
            if (parseFloat(valor) <= 0) {{
                alert('Valor deve ser maior que zero');
                return false;
            }}
            
            return true;
        }}
    </script>
    """
    
    return render_page(content)

@app.route('/historico')
def historico():
    # Combinar vendas e pagamentos
    transacoes = []
    
    for venda in data['sales']:
        transacoes.append({
            'tipo': 'Venda',
            'cliente': venda.get('client', 'N/A'),
            'descricao': f"{venda.get('product', 'N/A')} ({venda.get('quantity', 1)}x)" if venda.get('quantity') else venda.get('product', 'N/A'),
            'valor': venda.get('amount', 0),
            'data': venda.get('data_venda', venda.get('date', '')),
            'observacoes': venda.get('observacoes', ''),
            'classe_valor': 'text-success',
            'icone': 'fas fa-plus-circle text-success'
        })
    
    for pagamento in data['payments']:
        transacoes.append({
            'tipo': 'Pagamento',
            'cliente': pagamento.get('client', 'N/A'),
            'descricao': 'Pagamento recebido',
            'valor': pagamento.get('value', 0),
            'data': pagamento.get('data_pagamento', pagamento.get('date', '')),
            'observacoes': pagamento.get('observacoes', ''),
            'classe_valor': 'text-primary',
            'icone': 'fas fa-minus-circle text-primary'
        })
    
    # Ordenar por data (mais recentes primeiro)
    transacoes.sort(key=lambda x: x['data'], reverse=True)
    
    if not transacoes:
        rows = "<tr><td colspan='7' class='text-center py-3'>Nenhuma transação registrada.</td></tr>"
    else:
        rows = ""
        for t in transacoes:
            obs_display = (t['observacoes'][:30] + "...") if len(t['observacoes']) > 30 else t['observacoes']
            try:
                data_formatada = datetime.strptime(t['data'], '%Y-%m-%d').strftime('%d/%m/%Y') if t['data'] else 'N/A'
            except:
                data_formatada = t['data'] if t['data'] else 'N/A'
            
            rows += f"""
            <tr>
                <td><i class="{t['icone']}"></i></td>
                <td><strong>{t['tipo']}</strong></td>
                <td>{t['cliente']}</td>
                <td>{t['descricao']}</td>
                <td class="{t['classe_valor']}">
                    <strong>{formatar_moeda(t['valor'])}</strong>
                </td>
                <td>{data_formatada}</td>
                <td><small>{obs_display}</small></td>
            </tr>
            """
    
    content = f"""
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h4><i class="fas fa-history"></i> Histórico de Transações</h4>
        <div class="d-flex gap-2">
            <span class="badge badge-success"><i class="fas fa-plus"></i> Vendas</span>
            <span class="badge" style="background-color: #007bff; color: white;"><i class="fas fa-minus"></i> Pagamentos</span>
        </div>
    </div>
    
    <div class="quick-stats">
        <div class="stat-card">
            <div class="stat-number">{len(data['sales'])}</div>
            <div class="stat-label">Total de Vendas</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(data['payments'])}</div>
            <div class="stat-label">Total de Pagamentos</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(transacoes)}</div>
            <div class="stat-label">Total de Transações</div>
        </div>
    </div>
    
    <div class="table-container">
        <table class="table table-striped">
            <thead>
                <tr>
                    <th></th>
                    <th>Tipo</th>
                    <th>Cliente</th>
                    <th>Descrição</th>
                    <th>Valor</th>
                    <th>Data</th>
                    <th>Obs</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    
    <div class="mt-3">
        <a href="/" class="btn btn-secondary btn-sm">
            <i class="fas fa-home"></i> Voltar ao Dashboard
        </a>
    </div>
    """
    
    return render_page(content)

@app.route('/relatorios')
def relatorios():
    # Calcular métricas
    total_vendas = 0
    total_pagamentos = 0
    
    for venda in data['sales']:
        try:
            total_vendas += float(venda.get('amount', 0))
        except (ValueError, TypeError):
            continue
    
    for pagamento in data['payments']:
        try:
            total_pagamentos += float(pagamento.get('value', 0))
        except (ValueError, TypeError):
            continue
    
    saldo_pendente = total_vendas - total_pagamentos
    
    # Top clientes por valor de compras
    clientes_vendas = {}
    for venda in data['sales']:
        cliente = venda.get('client', 'N/A')
        try:
            valor = float(venda.get('amount', 0))
            clientes_vendas[cliente] = clientes_vendas.get(cliente, 0) + valor
        except (ValueError, TypeError):
            continue
    
    top_clientes = sorted(clientes_vendas.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Produtos mais vendidos
    produtos_vendas = {}
    for venda in data['sales']:
        produto = venda.get('product', 'N/A')
        quantidade = venda.get('quantity', 1)
        produtos_vendas[produto] = produtos_vendas.get(produto, 0) + quantidade
    
    top_produtos = sorted(produtos_vendas.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Gerar linhas das tabelas
    top_clientes_rows = ""
    if top_clientes:
        for cliente, valor in top_clientes:
            top_clientes_rows += f"<tr><td>{cliente}</td><td>{formatar_moeda(valor)}</td></tr>"
    else:
        top_clientes_rows = '<tr><td colspan="2" class="text-center">Nenhum dado disponível</td></tr>'
    
    top_produtos_rows = ""
    if top_produtos:
        for produto, quantidade in top_produtos:
            top_produtos_rows += f"<tr><td>{produto}</td><td>{quantidade}x</td></tr>"
    else:
        top_produtos_rows = '<tr><td colspan="2" class="text-center">Nenhum dado disponível</td></tr>'
    
    content = f"""
    <h4 class="mb-3"><i class="fas fa-chart-bar"></i> Relatrios e Anlises</h4>
    
    <div class="row">
        <div class="col-md-6">
            <div class="table-container">
                <h6 class="mb-3"><i class="fas fa-trophy"></i> Top 5 Clientes</h6>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Cliente</th>
                            <th>Total Compras</th>
                        </tr>
                    </thead>
                    <tbody>
                        {top_clientes_rows}
                    </tbody>
                </table>
            </div>
        </div>
        <div class="col-md-6">
            <div class="table-container">
                <h6 class="mb-3"><i class="fas fa-star"></i> Produtos Mais Vendidos</h6>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Produto</th>
                            <th>Quantidade</th>
                        </tr>
                    </thead>
                    <tbody>
                        {top_produtos_rows}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <div class="mt-3">
        <a href="/" class="btn btn-secondary btn-sm">
            <i class="fas fa-home"></i> Voltar ao Dashboard
        </a>
    </div>
    """
    
    return render_page(content)

# Rotas de edição e exclusão
@app.route('/editar_cliente/<int:client_id>', methods=['GET', 'POST'])
def editar_cliente(client_id):
    if client_id >= len(data['clients']):
        flash("Cliente no encontrado!", "danger")
        return redirect(url_for('listar_clientes'))
    
    client = data['clients'][client_id]
    
    if request.method == 'POST':
        try:
            nome = request.form.get('name', '').strip()
            telefone = request.form.get('phone', '').strip()
            email = request.form.get('email', '').strip()
            endereco = request.form.get('address', '').strip()
            cpf = request.form.get('cpf', '').strip()
            observacoes = request.form.get('observacoes', '').strip()
            
            if not nome:
                flash("Nome é obrigatório!", "danger")
                return redirect(url_for('editar_cliente', client_id=client_id))
            
            if not telefone:
                flash("Telefone é obrigatório!", "danger")
                return redirect(url_for('editar_cliente', client_id=client_id))
            
            client.update({
                'name': nome,
                'phone': telefone,
                'email': email,
                'address': endereco,
                'cpf': cpf,
                'observacoes': observacoes
            })
            
            salvar_dados(data)
            flash(f"Cliente {client['name']} atualizado com sucesso!", "success")
            return redirect(url_for('listar_clientes'))
            
        except Exception as e:
            flash(f"Erro ao atualizar cliente: {str(e)}", "danger")
            return redirect(url_for('editar_cliente', client_id=client_id))
    
    content = f"""
    <div class="form-container">
        <h2 class="form-title"><i class="fas fa-user-edit"></i> Editar Cliente</h2>
        <form method="post" onsubmit="return validarFormulario()">
            <div class="row">
                <div class="col-md-6">
                    <div class="form-group">
                        <label class="form-label">Nome Completo <span class="required">*</span></label>
                        <input type="text" class="form-control" name="name" value="{client['name']}" required>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="form-group">
                        <label class="form-label">Telefone <span class="required">*</span></label>
                        <input type="tel" class="form-control" name="phone" value="{client.get('phone', '')}" required>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <div class="form-group">
                        <label class="form-label">E-mail</label>
                        <input type="email" class="form-control" name="email" value="{client.get('email', '')}">
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="form-group">
                        <label class="form-label">CPF</label>
                        <input type="text" class="form-control" name="cpf" value="{client.get('cpf', '')}">
                    </div>
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">Endereço</label>
                <input type="text" class="form-control" name="address" value="{client.get('address', '')}">
            </div>
            <div class="form-group">
                <label class="form-label">Observações</label>
                <textarea class="form-control" name="observacoes" rows="2">{client.get('observacoes', '')}</textarea>
            </div>
            <div class="d-flex gap-2">
                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-save"></i> Salvar Alterações
                </button>
                <a href="/clientes" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Cancelar
                </a>
            </div>
        </form>
    </div>
    
    <script>
        function validarFormulario() {{
            const nome = document.querySelector('input[name="name"]').value.trim();
            const telefone = document.querySelector('input[name="phone"]').value.trim();
            
            if (nome.length < 2) {{
                alert('Nome deve ter pelo menos 2 caracteres');
                return false;
            }}
            
            if (telefone.length < 10) {{
                alert('Telefone deve ter pelo menos 10 dígitos');
                return false;
            }}
            
            return true;
        }}
    </script>
    """
    
    return render_page(content)

@app.route('/excluir_cliente/<int:client_id>')
def excluir_cliente(client_id):
    if client_id >= len(data['clients']):
        flash("Cliente não encontrado!", "danger")
    else:
        try:
            client_name = data['clients'][client_id]['name']
            
            # Verificar se cliente tem vendas ou pagamentos
            tem_vendas = any(v.get('client') == client_name for v in data['sales'])
            tem_pagamentos = any(p.get('client') == client_name for p in data['payments'])
            
            if tem_vendas or tem_pagamentos:
                flash(f"Não é possível excluir o cliente {client_name} pois possui vendas ou pagamentos registrados!", "danger")
            else:
                data['clients'].pop(client_id)
                salvar_dados(data)
                flash(f"Cliente {client_name} excluído com sucesso!", "success")
                
        except Exception as e:
            flash(f"Erro ao excluir cliente: {str(e)}", "danger")
    
    return redirect(url_for('listar_clientes'))

if __name__ == "__main__":
    print("🚀 Iniciando Sistema de Vendas Ivone...")
    print("📋 Acesse: http://localhost:5000")
    print("💖 Sistema com controle de estoque integrado!")
    print("✨ Funcionalidades:")
    print("   - Sistema de estoque completo")
    print("   - Vendas com seleção por código de produto")
    print("   - Controle automático de estoque")
    print("   - Interface visual preservada do app2.py")
    app.run(debug=True, host='0.0.0.0', port=5000)