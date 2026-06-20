import pytest
from app import app, db
from src.models.expense import Expense, Income, Category, Budget, RecurringExpense
from datetime import datetime, timedelta

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()

        # Add predefined categories
        predefined_categories = [
            'Food & Dining', 'Transportation', 'Housing & Utilities', 'Entertainment',
            'Shopping & Retail', 'Healthcare', 'Education', 'Subscription & Memberships',
            'Insurance', 'Gifts & Donations', 'Personal Care'
        ]
        for cat_name in predefined_categories:
            cat = Category(name=cat_name, is_predefined=True)
            db.session.add(cat)
        db.session.commit()

        yield app.test_client()
        db.session.remove()
        db.drop_all()

# ==================== BASIC TESTS ====================

def test_index_route(client):
    """Test homepage loads"""
    response = client.get('/')
    assert response.status_code == 200

def test_health_route(client):
    """Test health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'ok'

def test_404_error(client):
    """Test 404 error handling"""
    response = client.get('/nonexistent')
    assert response.status_code == 404

# ==================== ECOM-165: ADD EXPENSE ====================

def test_add_expense_success(client):
    """Test adding a new expense"""
    expense_data = {
        'amount': 50.00,
        'category': 'Food & Dining',
        'description': 'Lunch',
        'payment_method': 'Cash'
    }
    response = client.post('/api/expenses', json=expense_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data['amount'] == 50.00
    assert data['category'] == 'Food & Dining'

def test_add_expense_missing_amount(client):
    """Test adding expense without amount"""
    expense_data = {
        'category': 'Food & Dining',
        'payment_method': 'Cash'
    }
    response = client.post('/api/expenses', json=expense_data)
    assert response.status_code == 400

def test_add_expense_negative_amount(client):
    """Test adding expense with negative amount"""
    expense_data = {
        'amount': -50.00,
        'category': 'Food & Dining',
        'payment_method': 'Cash'
    }
    response = client.post('/api/expenses', json=expense_data)
    assert response.status_code == 400

def test_add_expense_missing_category(client):
    """Test adding expense without category"""
    expense_data = {
        'amount': 50.00,
        'payment_method': 'Cash'
    }
    response = client.post('/api/expenses', json=expense_data)
    assert response.status_code == 400

def test_add_expense_long_description(client):
    """Test adding expense with description exceeding 500 chars"""
    long_desc = 'a' * 501
    expense_data = {
        'amount': 50.00,
        'category': 'Food & Dining',
        'description': long_desc,
        'payment_method': 'Cash'
    }
    response = client.post('/api/expenses', json=expense_data)
    assert response.status_code == 400

# ==================== ECOM-166: EDIT EXPENSE ====================

def test_edit_expense_success(client):
    """Test editing an existing expense"""
    # Add expense first
    expense_data = {
        'amount': 50.00,
        'category': 'Food & Dining',
        'payment_method': 'Cash'
    }
    add_response = client.post('/api/expenses', json=expense_data)
    expense_id = add_response.get_json()['id']

    # Edit expense
    edit_data = {'amount': 75.00}
    response = client.put(f'/api/expenses/{expense_id}', json=edit_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['amount'] == 75.00

def test_edit_nonexistent_expense(client):
    """Test editing non-existent expense"""
    response = client.put('/api/expenses/999', json={'amount': 100})
    assert response.status_code == 404

# ==================== ECOM-167: DELETE EXPENSE ====================

def test_delete_expense_success(client):
    """Test deleting an expense"""
    # Add expense first
    expense_data = {
        'amount': 50.00,
        'category': 'Food & Dining',
        'payment_method': 'Cash'
    }
    add_response = client.post('/api/expenses', json=expense_data)
    expense_id = add_response.get_json()['id']

    # Delete expense
    response = client.delete(f'/api/expenses/{expense_id}')
    assert response.status_code == 200

    # Verify deleted
    get_response = client.get(f'/api/expenses/{expense_id}')
    assert get_response.status_code == 404

def test_delete_nonexistent_expense(client):
    """Test deleting non-existent expense"""
    response = client.delete('/api/expenses/999')
    assert response.status_code == 404

# ==================== ECOM-168: ADD INCOME ====================

def test_add_income_success(client):
    """Test adding income"""
    income_data = {
        'amount': 5000.00,
        'category': 'Salary',
        'source': 'Employer'
    }
    response = client.post('/api/incomes', json=income_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data['amount'] == 5000.00
    assert data['source'] == 'Employer'

def test_add_income_missing_amount(client):
    """Test adding income without amount"""
    income_data = {
        'category': 'Salary',
        'source': 'Employer'
    }
    response = client.post('/api/incomes', json=income_data)
    assert response.status_code == 400

# ==================== ECOM-169: PREDEFINED CATEGORIES ====================

def test_get_predefined_categories(client):
    """Test getting predefined categories"""
    response = client.get('/api/categories/predefined')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0
    assert any(cat['name'] == 'Food & Dining' for cat in data)

# ==================== ECOM-170: CUSTOM CATEGORIES ====================

def test_create_custom_category(client):
    """Test creating custom category"""
    cat_data = {
        'name': 'Pet Care',
        'icon': '🐾',
        'color': '#FF6B6B'
    }
    response = client.post('/api/categories', json=cat_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'Pet Care'
    assert data['is_predefined'] == False

def test_create_duplicate_category(client):
    """Test creating duplicate category"""
    cat_data = {
        'name': 'Pet Care',
        'icon': '🐾',
        'color': '#FF6B6B'
    }
    client.post('/api/categories', json=cat_data)
    response = client.post('/api/categories', json=cat_data)
    assert response.status_code == 400

def test_edit_custom_category(client):
    """Test editing custom category"""
    # Create category first
    cat_data = {
        'name': 'Pet Care',
        'icon': '🐾',
        'color': '#FF6B6B'
    }
    add_response = client.post('/api/categories', json=cat_data)
    cat_id = add_response.get_json()['id']

    # Edit category
    edit_data = {'name': 'Pet Expenses'}
    response = client.put(f'/api/categories/{cat_id}', json=edit_data)
    assert response.status_code == 200

def test_delete_custom_category(client):
    """Test deleting custom category"""
    # Create category first
    cat_data = {
        'name': 'Pet Care',
        'icon': '🐾',
        'color': '#FF6B6B'
    }
    add_response = client.post('/api/categories', json=cat_data)
    cat_id = add_response.get_json()['id']

    # Delete category
    response = client.delete(f'/api/categories/{cat_id}')
    assert response.status_code == 200

# ==================== ECOM-171: SET BUDGET ====================

def test_set_budget(client):
    """Test setting budget"""
    budget_data = {
        'category': 'Food & Dining',
        'amount': 500.00,
        'budget_type': 'fixed'
    }
    response = client.post('/api/budgets', json=budget_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data['category'] == 'Food & Dining'
    assert data['amount'] == 500.00

def test_set_budget_negative_amount(client):
    """Test setting budget with negative amount"""
    budget_data = {
        'category': 'Food & Dining',
        'amount': -500.00
    }
    response = client.post('/api/budgets', json=budget_data)
    assert response.status_code == 400

# ==================== ECOM-172: BUDGET TRACKING ====================

def test_get_budget_tracking(client):
    """Test getting budget tracking"""
    # Set budget
    budget_data = {
        'category': 'Food & Dining',
        'amount': 500.00,
        'budget_type': 'fixed'
    }
    client.post('/api/budgets', json=budget_data)

    # Add expense
    expense_data = {
        'amount': 100.00,
        'category': 'Food & Dining',
        'payment_method': 'Cash'
    }
    client.post('/api/expenses', json=expense_data)

    # Get tracking
    response = client.get('/api/budgets/tracking')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0

# ==================== ECOM-173: RECURRING EXPENSES ====================

def test_create_recurring_expense(client):
    """Test creating recurring expense"""
    rec_data = {
        'amount': 100.00,
        'category': 'Subscription & Memberships',
        'description': 'Netflix',
        'frequency': 'monthly'
    }
    response = client.post('/api/recurring-expenses', json=rec_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data['frequency'] == 'monthly'

# ==================== ECOM-175,176,177: FILTER EXPENSES ====================

def test_filter_expenses_by_date(client):
    """Test filtering expenses by date"""
    # Add expenses
    expense_data = {
        'amount': 50.00,
        'category': 'Food & Dining',
        'payment_method': 'Cash'
    }
    client.post('/api/expenses', json=expense_data)

    # Filter by date range
    response = client.get(f'/api/expenses/filter?start_date={datetime.now().date()}&end_date={datetime.now().date()}')
    assert response.status_code == 200

def test_filter_expenses_by_category(client):
    """Test filtering expenses by category"""
    # Add expense
    expense_data = {
        'amount': 50.00,
        'category': 'Food & Dining',
        'payment_method': 'Cash'
    }
    client.post('/api/expenses', json=expense_data)

    # Filter by category
    response = client.get('/api/expenses/filter?category=Food & Dining')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1

def test_filter_expenses_by_amount(client):
    """Test filtering expenses by amount"""
    # Add expenses
    expense_data = {
        'amount': 50.00,
        'category': 'Food & Dining',
        'payment_method': 'Cash'
    }
    client.post('/api/expenses', json=expense_data)

    # Filter by amount
    response = client.get('/api/expenses/filter?min_amount=40&max_amount=60')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1

# ==================== ECOM-178: FULL-TEXT SEARCH ====================

def test_search_expenses(client):
    """Test full-text search"""
    # Add expense
    expense_data = {
        'amount': 50.00,
        'category': 'Food & Dining',
        'description': 'Lunch at Italian restaurant',
        'payment_method': 'Cash'
    }
    client.post('/api/expenses', json=expense_data)

    # Search
    response = client.get('/api/expenses/search?q=Italian')
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] == 1

# ==================== ECOM-179: DASHBOARD ====================

def test_get_dashboard(client):
    """Test getting dashboard"""
    # Add income
    income_data = {
        'amount': 5000.00,
        'category': 'Salary',
        'source': 'Employer'
    }
    client.post('/api/incomes', json=income_data)

    # Add expense
    expense_data = {
        'amount': 500.00,
        'category': 'Food & Dining',
        'payment_method': 'Cash'
    }
    client.post('/api/expenses', json=expense_data)

    # Get dashboard
    response = client.get('/api/dashboard')
    assert response.status_code == 200
    data = response.get_json()
    assert data['total_income'] == 5000.00
    assert data['total_expenses'] == 500.00
    assert data['net_balance'] == 4500.00

# ==================== ECOM-180: CATEGORY BREAKDOWN ====================

def test_get_category_breakdown(client):
    """Test getting category breakdown"""
    # Add expenses
    client.post('/api/expenses', json={
        'amount': 50.00,
        'category': 'Food & Dining',
        'payment_method': 'Cash'
    })
    client.post('/api/expenses', json={
        'amount': 100.00,
        'category': 'Transportation',
        'payment_method': 'Card'
    })

    # Get breakdown
    response = client.get('/api/analytics/category-breakdown')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2

# ==================== ECOM-181: MONTHLY TRENDS ====================

def test_get_monthly_trends(client):
    """Test getting monthly trends"""
    # Add expense
    expense_data = {
        'amount': 50.00,
        'category': 'Food & Dining',
        'payment_method': 'Cash'
    }
    client.post('/api/expenses', json=expense_data)

    # Get trends
    response = client.get('/api/analytics/trends')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 12

# ==================== ECOM-182: GENERATE REPORTS ====================

def test_generate_report(client):
    """Test generating report"""
    # Add expenses
    client.post('/api/expenses', json={
        'amount': 50.00,
        'category': 'Food & Dining',
        'payment_method': 'Cash'
    })

    # Generate report
    response = client.get('/api/reports')
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] == 1
    assert data['total'] == 50.00

# ==================== ECOM-183: EXPORT EXPENSES ====================

def test_export_expenses_csv(client):
    """Test exporting expenses as CSV"""
    # Add expense
    client.post('/api/expenses', json={
        'amount': 50.00,
        'category': 'Food & Dining',
        'description': 'Lunch',
        'payment_method': 'Cash'
    })

    # Export
    response = client.get('/api/expenses/export?format=csv')
    assert response.status_code == 200

# ==================== ECOM-184: IMPORT EXPENSES ====================

def test_import_expenses(client):
    """Test importing expenses"""
    import_data = {
        'expenses': [
            {
                'amount': 50.00,
                'category': 'Food & Dining',
                'date': datetime.now().isoformat(),
                'description': 'Lunch',
                'payment_method': 'Cash'
            }
        ]
    }
    response = client.post('/api/expenses/import', json=import_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['imported'] == 1

# ==================== GET ALL ====================

def test_get_all_expenses(client):
    """Test getting all expenses"""
    # Add expense
    client.post('/api/expenses', json={
        'amount': 50.00,
        'category': 'Food & Dining',
        'payment_method': 'Cash'
    })

    # Get all
    response = client.get('/api/expenses')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1

def test_get_all_incomes(client):
    """Test getting all incomes"""
    # Add income
    client.post('/api/incomes', json={
        'amount': 5000.00,
        'category': 'Salary',
        'source': 'Employer'
    })

    # Get all
    response = client.get('/api/incomes')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
