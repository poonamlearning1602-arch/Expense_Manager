import os
from dotenv import load_dotenv
from flask import Flask, render_template
from src.models.expense import db, Expense, Income, Category, Budget, RecurringExpense
from src.controllers.expense_controller import ExpenseController

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///expense_manager.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html', title='Expense Manager')

@app.route('/api/health')
def health():
    return {'status': 'ok', 'message': 'Expense Manager API is running'}

# ECOM-165: Add Expense
@app.route('/api/expenses', methods=['POST'])
def add_expense():
    return ExpenseController.add_expense()

# ECOM-166: Edit Expense
@app.route('/api/expenses/<int:expense_id>', methods=['PUT'])
def edit_expense(expense_id):
    return ExpenseController.edit_expense(expense_id)

# ECOM-167: Delete Expense
@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    return ExpenseController.delete_expense(expense_id)

# ECOM-168: Add Income
@app.route('/api/incomes', methods=['POST'])
def add_income():
    return ExpenseController.add_income()

# ECOM-169: Get Predefined Categories
@app.route('/api/categories/predefined', methods=['GET'])
def get_predefined_categories():
    return ExpenseController.get_predefined_categories()

# ECOM-170: Create Custom Category
@app.route('/api/categories', methods=['POST'])
def create_custom_category():
    return ExpenseController.create_custom_category()

@app.route('/api/categories/<int:category_id>', methods=['PUT'])
def edit_custom_category(category_id):
    return ExpenseController.edit_custom_category(category_id)

@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_custom_category(category_id):
    return ExpenseController.delete_custom_category(category_id)

# ECOM-171: Set Budget
@app.route('/api/budgets', methods=['POST'])
def set_budget():
    return ExpenseController.set_budget()

# ECOM-172: Budget Tracking
@app.route('/api/budgets/tracking', methods=['GET'])
def get_budget_tracking():
    return ExpenseController.get_budget_tracking()

# ECOM-173: Create Recurring Expense
@app.route('/api/recurring-expenses', methods=['POST'])
def create_recurring_expense():
    return ExpenseController.create_recurring_expense()

# ECOM-175: Filter Expenses
@app.route('/api/expenses/filter', methods=['GET'])
def filter_expenses():
    return ExpenseController.filter_expenses()

# ECOM-176: Filter by Category (included in filter_expenses)
# ECOM-177: Filter by Amount (included in filter_expenses)

# ECOM-178: Full-Text Search
@app.route('/api/expenses/search', methods=['GET'])
def search_expenses():
    return ExpenseController.search_expenses()

# ECOM-179: Dashboard
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    return ExpenseController.get_dashboard()

# ECOM-180: Category Breakdown
@app.route('/api/analytics/category-breakdown', methods=['GET'])
def get_category_breakdown():
    return ExpenseController.get_category_breakdown()

# ECOM-181: Monthly Trends
@app.route('/api/analytics/trends', methods=['GET'])
def get_monthly_trends():
    return ExpenseController.get_monthly_trends()

# ECOM-182: Generate Reports
@app.route('/api/reports', methods=['GET'])
def generate_report():
    return ExpenseController.generate_report()

# ECOM-183: Export Expenses
@app.route('/api/expenses/export', methods=['GET'])
def export_expenses():
    return ExpenseController.export_expenses()

# ECOM-184: Import Expenses
@app.route('/api/expenses/import', methods=['POST'])
def import_expenses():
    return ExpenseController.import_expenses()

# Get all expenses
@app.route('/api/expenses', methods=['GET'])
def get_all_expenses():
    return ExpenseController.get_all_expenses()

# Get all incomes
@app.route('/api/incomes', methods=['GET'])
def get_all_incomes():
    return ExpenseController.get_all_incomes()

@app.errorhandler(404)
def not_found(error):
    return {'error': 'Not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True'
    app.run(host='0.0.0.0', port=port, debug=debug)
