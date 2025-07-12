from flask import Flask, render_template, request, redirect, session, url_for
import csv, os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with something secure

# Hardcoded credentials
USERNAME = "you"
PASSWORD = "love"

DATA_FILE = 'expenses.csv'
BUDGET_FILE = 'budget.txt'

def load_expenses():
    expenses = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    row['Amount'] = float(row['Amount'])
                    expenses.append(row)
                except ValueError:
                    continue
    return expenses

def save_expense(date, description, amount):
    with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([date, description, amount])

def load_budget():
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, 'r', encoding='utf-8') as f:
            try:
                return float(f.read())
            except ValueError:
                return 0.0
    return 0.0

def save_budget(budget):
    with open(BUDGET_FILE, 'w', encoding='utf-8') as f:
        f.write(str(budget))

@app.route('/', methods=['GET'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    expenses = load_expenses()
    total_spent = sum(exp['Amount'] for exp in expenses)
    budget = load_budget()
    remaining = budget - total_spent
    status = "You're within budget!" if remaining >= 0 else "Over budget!"

    chart_labels = []
    chart_values = []
    category_totals = {}

    for e in expenses:
        category = e['Description']
        category_totals[category] = category_totals.get(category, 0) + e['Amount']

    for category, total in category_totals.items():
        chart_labels.append(category)
        chart_values.append(round(total, 2))

    chart_data = {
        'labels': chart_labels,
        'data': chart_values
    }

    return render_template("index.html",
                           expenses=expenses,
                           total_spent=total_spent,
                           budget=budget,
                           remaining=remaining,
                           status=status,
                           chart_data=chart_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = 'Incorrect username or password.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
def add_expense():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        date = request.form['date']
        desc = request.form['description']
        amount = float(request.form['amount'])
        save_expense(date, desc, amount)
    except:
        pass
    return redirect('/')

@app.route('/set_budget', methods=['POST'])
def set_budget():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        budget = float(request.form['budget'])
        save_budget(budget)
    except:
        pass
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)