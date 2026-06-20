import os
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from src.models.expense import db, User, Expense, Income, Category, Budget, RecurringExpense
from src.controllers.expense_controller import ExpenseController

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///expense_manager.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')

jwt = JWTManager(app)

db.init_app(app)

with app.app_context():
    db.create_all()

    # Ensure predefined categories exist (no user_id means shared)
    predefined_cats = [
        'Food & Dining', 'Transportation', 'Housing & Utilities', 'Entertainment',
        'Shopping & Retail', 'Healthcare', 'Education', 'Subscription & Memberships',
        'Insurance', 'Gifts & Donations', 'Personal Care'
    ]

    for cat_name in predefined_cats:
        existing = Category.query.filter_by(name=cat_name, is_predefined=True).first()
        if not existing:
            cat = Category(name=cat_name, is_predefined=True, user_id=None)
            db.session.add(cat)
    db.session.commit()

@app.route('/')
def index():
    return render_template('login.html', title='Expense Manager - Login')

@app.route('/app')
def app_dashboard():
    return render_template('app.html', title='Expense Manager')

@app.route('/api/health')
def health():
    return {'status': 'ok', 'message': 'Expense Manager API is running'}

# Authentication routes
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return {'error': 'Missing username, password, or email'}, 400

    if User.query.filter_by(username=data['username']).first():
        return {'error': 'Username already exists'}, 400

    if User.query.filter_by(email=data['email']).first():
        return {'error': 'Email already exists'}, 400

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.id)
    return {'access_token': access_token, 'user': user.to_dict()}, 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return {'error': 'Missing username or password'}, 400

    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return {'error': 'Invalid username or password'}, 401

    access_token = create_access_token(identity=user.id)
    return {'access_token': access_token, 'user': user.to_dict()}, 200

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return {'error': 'User not found'}, 404
    return user.to_dict(), 200

# ECOM-165: Add Expense
@app.route('/api/expenses', methods=['POST'])
@jwt_required()
def add_expense():
    return ExpenseController.add_expense()

# ECOM-166: Edit Expense
@app.route('/api/expenses/<int:expense_id>', methods=['PUT'])
@jwt_required()
def edit_expense(expense_id):
    return ExpenseController.edit_expense(expense_id)

# ECOM-167: Delete Expense
@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    return ExpenseController.delete_expense(expense_id)

# ECOM-168: Add Income
@app.route('/api/incomes', methods=['POST'])
@jwt_required()
def add_income():
    return ExpenseController.add_income()

# ECOM-169: Get Predefined Categories
@app.route('/api/categories/predefined', methods=['GET'])
@jwt_required()
def get_predefined_categories():
    return ExpenseController.get_predefined_categories()

# ECOM-170: Create Custom Category
@app.route('/api/categories', methods=['POST'])
@jwt_required()
def create_custom_category():
    return ExpenseController.create_custom_category()

@app.route('/api/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
def edit_custom_category(category_id):
    return ExpenseController.edit_custom_category(category_id)

@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_custom_category(category_id):
    return ExpenseController.delete_custom_category(category_id)

# ECOM-171: Set Budget
@app.route('/api/budgets', methods=['POST'])
@jwt_required()
def set_budget():
    return ExpenseController.set_budget()

# ECOM-172: Budget Tracking
@app.route('/api/budgets/tracking', methods=['GET'])
@jwt_required()
def get_budget_tracking():
    return ExpenseController.get_budget_tracking()

# ECOM-173: Create Recurring Expense
@app.route('/api/recurring-expenses', methods=['POST'])
@jwt_required()
def create_recurring_expense():
    return ExpenseController.create_recurring_expense()

# ECOM-175: Filter Expenses
@app.route('/api/expenses/filter', methods=['GET'])
@jwt_required()
def filter_expenses():
    return ExpenseController.filter_expenses()

# ECOM-176: Filter by Category (included in filter_expenses)
# ECOM-177: Filter by Amount (included in filter_expenses)

# ECOM-178: Full-Text Search
@app.route('/api/expenses/search', methods=['GET'])
@jwt_required()
def search_expenses():
    return ExpenseController.search_expenses()

# ECOM-179: Dashboard
@app.route('/api/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    return ExpenseController.get_dashboard()

# ECOM-180: Category Breakdown
@app.route('/api/analytics/category-breakdown', methods=['GET'])
@jwt_required()
def get_category_breakdown():
    return ExpenseController.get_category_breakdown()

# ECOM-181: Monthly Trends
@app.route('/api/analytics/trends', methods=['GET'])
@jwt_required()
def get_monthly_trends():
    return ExpenseController.get_monthly_trends()

# ECOM-182: Generate Reports
@app.route('/api/reports', methods=['GET'])
@jwt_required()
def generate_report():
    return ExpenseController.generate_report()

# ECOM-183: Export Expenses
@app.route('/api/expenses/export', methods=['GET'])
@jwt_required()
def export_expenses():
    return ExpenseController.export_expenses()

# ECOM-184: Import Expenses
@app.route('/api/expenses/import', methods=['POST'])
@jwt_required()
def import_expenses():
    return ExpenseController.import_expenses()

# Get all expenses
@app.route('/api/expenses', methods=['GET'])
@jwt_required()
def get_all_expenses():
    return ExpenseController.get_all_expenses()

# Get all incomes
@app.route('/api/incomes', methods=['GET'])
@jwt_required()
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
