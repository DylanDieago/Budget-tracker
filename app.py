from flask import Flask, render_template, request, redirect, send_file, session
import csv
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Replace with a stronger key in production

# ----- Login credentials -----
USERNAME = "dylan"
PASSWORD = "mywife"

DATA_FILE = 'expenses.csv'
BUDGET_FILE = 'budget.txt'

# ---------- Load and Save Functions ----------
def load_expenses():
    expenses = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    row['Amount'] = float(row['Amount'])
                    expenses.append(row)
                except ValueError:
                    continue
    return expenses

def save_expense(date, description, amount):
    with open(DATA_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
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

# ---------- Authentication Routes ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect('/')
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

# ---------- Main Routes ----------
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect('/login')

    expenses = load_expenses()
    total_spent = sum(expense['Amount'] for expense in expenses)
    budget = load_budget()
    remaining = budget - total_spent
    status = "You're within budget!" if remaining >= 0 else "Over budget!"

    # Pie Chart Data
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

    return render_template('index.html',
                           expenses=expenses,
                           total_spent=total_spent,
                           budget=budget,
                           remaining=remaining,
                           status=status,
                           chart_data=chart_data)

@app.route('/add', methods=['POST'])
def add_expense():
    if not session.get('logged_in'):
        return redirect('/login')

    date = request.form['date']
    description = request.form['description']
    amount = request.form['amount']

    try:
        amount = float(amount)
        save_expense(date, description, amount)
    except ValueError:
        print("Invalid amount")

    return redirect('/')

@app.route('/set_budget', methods=['POST'])
def set_budget():
    if not session.get('logged_in'):
        return redirect('/login')

    budget = request.form['budget']
    try:
        save_budget(float(budget))
    except ValueError:
        pass
    return redirect('/')

@app.route('/download')
def download():
    if not session.get('logged_in'):
        return redirect('/login')
    return send_file(DATA_FILE, as_attachment=True)

# ---------- Run App ----------
if __name__ == '__main__':
    print("✅ App is running!")
    app.run(debug=True, host='0.0.0.0', port=5000)
