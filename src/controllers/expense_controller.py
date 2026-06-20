from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from src.models.expense import db, Expense, Income, Category, Budget, RecurringExpense
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json

class ExpenseController:

    @staticmethod
    def add_expense():
        """ECOM-165: Add a new expense"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()

            # Validation
            if not data.get('amount') or data['amount'] <= 0:
                return jsonify({'error': 'Amount must be positive'}), 400
            if not data.get('category'):
                return jsonify({'error': 'Category is required'}), 400
            if not data.get('payment_method'):
                return jsonify({'error': 'Payment method is required'}), 400

            if data.get('description') and len(data['description']) > 500:
                return jsonify({'error': 'Description cannot exceed 500 characters'}), 400

            expense_date = datetime.fromisoformat(data.get('date', datetime.now().isoformat()))

            expense = Expense(
                user_id=user_id,
                amount=float(data['amount']),
                category=data['category'],
                date=expense_date,
                description=data.get('description', ''),
                payment_method=data['payment_method']
            )

            db.session.add(expense)
            db.session.commit()

            return jsonify(expense.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def edit_expense(expense_id):
        """ECOM-166: Edit an existing expense"""
        try:
            user_id = get_jwt_identity()
            expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first_or_404()
            data = request.get_json()

            if 'amount' in data:
                if data['amount'] <= 0:
                    return jsonify({'error': 'Amount must be positive'}), 400
                expense.amount = float(data['amount'])

            if 'category' in data:
                expense.category = data['category']

            if 'date' in data:
                expense.date = datetime.fromisoformat(data['date'])

            if 'description' in data:
                if len(data['description']) > 500:
                    return jsonify({'error': 'Description cannot exceed 500 characters'}), 400
                expense.description = data['description']

            if 'payment_method' in data:
                expense.payment_method = data['payment_method']

            expense.updated_at = datetime.utcnow()
            db.session.commit()

            return jsonify(expense.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def delete_expense(expense_id):
        """ECOM-167: Delete an expense"""
        try:
            user_id = get_jwt_identity()
            expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first_or_404()
            db.session.delete(expense)
            db.session.commit()
            return jsonify({'message': 'Expense deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def add_income():
        """ECOM-168: Add income transaction"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()

            if not data.get('amount') or data['amount'] <= 0:
                return jsonify({'error': 'Amount must be positive'}), 400
            if not data.get('category'):
                return jsonify({'error': 'Category is required'}), 400
            if not data.get('source'):
                return jsonify({'error': 'Source is required'}), 400

            income_date = datetime.fromisoformat(data.get('date', datetime.now().isoformat()))

            income = Income(
                user_id=user_id,
                amount=float(data['amount']),
                category=data['category'],
                source=data['source'],
                date=income_date
            )

            db.session.add(income)
            db.session.commit()

            return jsonify(income.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def get_predefined_categories():
        """ECOM-169: Get predefined categories"""
        try:
            categories = Category.query.filter_by(is_predefined=True).all()
            return jsonify([cat.to_dict() for cat in categories]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def create_custom_category():
        """ECOM-170: Create custom category"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()

            if not data.get('name'):
                return jsonify({'error': 'Category name is required'}), 400

            if Category.query.filter_by(user_id=user_id, name=data['name']).first():
                return jsonify({'error': 'Category already exists'}), 400

            category = Category(
                user_id=user_id,
                name=data['name'],
                icon=data.get('icon'),
                color=data.get('color'),
                is_predefined=False
            )

            db.session.add(category)
            db.session.commit()

            return jsonify(category.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def edit_custom_category(category_id):
        """Edit custom category"""
        try:
            user_id = get_jwt_identity()
            category = Category.query.filter_by(id=category_id, user_id=user_id).first_or_404()
            data = request.get_json()

            if category.is_predefined:
                return jsonify({'error': 'Cannot edit predefined categories'}), 400

            if 'name' in data:
                if Category.query.filter_by(user_id=user_id, name=data['name']).filter(Category.id != category_id).first():
                    return jsonify({'error': 'Category name already exists'}), 400
                category.name = data['name']

            if 'icon' in data:
                category.icon = data['icon']

            if 'color' in data:
                category.color = data['color']

            db.session.commit()
            return jsonify(category.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def delete_custom_category(category_id):
        """Delete custom category"""
        try:
            user_id = get_jwt_identity()
            category = Category.query.filter_by(id=category_id, user_id=user_id).first_or_404()

            if category.is_predefined:
                return jsonify({'error': 'Cannot delete predefined categories'}), 400

            expenses_count = Expense.query.filter_by(user_id=user_id, category=category.name).count()
            if expenses_count > 0:
                return jsonify({'error': 'Cannot delete category with existing expenses'}), 400

            db.session.delete(category)
            db.session.commit()

            return jsonify({'message': 'Category deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def set_budget():
        """ECOM-171: Set budget for categories"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()

            if not data.get('category'):
                return jsonify({'error': 'Category is required'}), 400
            if not data.get('amount') or data['amount'] <= 0:
                return jsonify({'error': 'Amount must be positive'}), 400

            now = datetime.now()

            budget = Budget.query.filter_by(
                user_id=user_id,
                category=data['category'],
                month=now.month,
                year=now.year
            ).first()

            if budget:
                budget.amount = float(data['amount'])
                budget.budget_type = data.get('budget_type', 'fixed')
                budget.updated_at = datetime.utcnow()
            else:
                budget = Budget(
                    user_id=user_id,
                    category=data['category'],
                    amount=float(data['amount']),
                    budget_type=data.get('budget_type', 'fixed'),
                    month=now.month,
                    year=now.year
                )
                db.session.add(budget)

            db.session.commit()
            return jsonify(budget.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def get_budget_tracking():
        """ECOM-172: Monitor budget utilization"""
        try:
            user_id = get_jwt_identity()
            now = datetime.now()
            budgets = Budget.query.filter_by(user_id=user_id, month=now.month, year=now.year).all()

            tracking = []
            for budget in budgets:
                expenses = Expense.query.filter_by(user_id=user_id, category=budget.category).filter(
                    Expense.date >= datetime(now.year, now.month, 1),
                    Expense.date < datetime(now.year, now.month, 28)
                ).all()

                total_spent = sum(exp.amount for exp in expenses)
                percentage = (total_spent / budget.amount * 100) if budget.amount > 0 else 0

                status = 'green' if percentage < 75 else 'yellow' if percentage < 90 else 'red'

                tracking.append({
                    'category': budget.category,
                    'budget': budget.amount,
                    'spent': total_spent,
                    'percentage': round(percentage, 2),
                    'status': status
                })

            return jsonify(tracking), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def filter_expenses():
        """Filter expenses by date, category, amount"""
        try:
            user_id = get_jwt_identity()
            filters = request.args.to_dict()
            query = Expense.query.filter_by(user_id=user_id)

            # Filter by date range
            if filters.get('start_date'):
                start_date = datetime.fromisoformat(filters['start_date'])
                query = query.filter(Expense.date >= start_date)

            if filters.get('end_date'):
                end_date = datetime.fromisoformat(filters['end_date'])
                query = query.filter(Expense.date <= end_date)

            # Filter by category
            if filters.get('category'):
                query = query.filter_by(category=filters['category'])

            # Filter by amount range
            if filters.get('min_amount'):
                query = query.filter(Expense.amount >= float(filters['min_amount']))

            if filters.get('max_amount'):
                query = query.filter(Expense.amount <= float(filters['max_amount']))

            expenses = query.all()
            return jsonify([exp.to_dict() for exp in expenses]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def search_expenses():
        """ECOM-178: Full-text search"""
        try:
            user_id = get_jwt_identity()
            search_term = request.args.get('q', '').lower()

            expenses = Expense.query.filter_by(user_id=user_id).all()
            results = [
                exp.to_dict() for exp in expenses
                if search_term in exp.description.lower() or search_term in exp.category.lower()
            ]

            return jsonify({'count': len(results), 'results': results}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def get_dashboard():
        """ECOM-179: Dashboard summary"""
        try:
            user_id = get_jwt_identity()
            now = datetime.now()
            month_start = datetime(now.year, now.month, 1)

            expenses = Expense.query.filter_by(user_id=user_id).filter(Expense.date >= month_start).all()
            incomes = Income.query.filter_by(user_id=user_id).filter(Income.date >= month_start).all()

            total_expenses = sum(exp.amount for exp in expenses)
            total_income = sum(inc.amount for inc in incomes)
            net_balance = total_income - total_expenses
            savings_rate = (net_balance / total_income * 100) if total_income > 0 else 0

            return jsonify({
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_balance': net_balance,
                'savings_rate': round(savings_rate, 2),
                'month': now.strftime('%B %Y')
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def get_category_breakdown():
        """ECOM-180: Category breakdown visualization"""
        try:
            user_id = get_jwt_identity()
            now = datetime.now()
            month_start = datetime(now.year, now.month, 1)

            expenses = Expense.query.filter_by(user_id=user_id).filter(Expense.date >= month_start).all()

            breakdown = {}
            for exp in expenses:
                if exp.category not in breakdown:
                    breakdown[exp.category] = 0
                breakdown[exp.category] += exp.amount

            total = sum(breakdown.values())

            result = [
                {
                    'category': cat,
                    'amount': amount,
                    'percentage': round(amount / total * 100, 2) if total > 0 else 0
                }
                for cat, amount in sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
            ]

            return jsonify(result), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def get_monthly_trends():
        """ECOM-181: Monthly trends analysis"""
        try:
            user_id = get_jwt_identity()
            now = datetime.now()
            months = 12
            trends = []

            for i in range(months):
                month_date = now - relativedelta(months=i)
                month_start = datetime(month_date.year, month_date.month, 1)
                month_end = month_start + relativedelta(months=1)

                expenses = Expense.query.filter_by(user_id=user_id).filter(
                    Expense.date >= month_start,
                    Expense.date < month_end
                ).all()
                incomes = Income.query.filter_by(user_id=user_id).filter(
                    Income.date >= month_start,
                    Income.date < month_end
                ).all()

                total_expenses = sum(exp.amount for exp in expenses)
                total_income = sum(inc.amount for inc in incomes)

                trends.insert(0, {
                    'month': month_start.strftime('%B %Y'),
                    'expenses': total_expenses,
                    'income': total_income
                })

            return jsonify(trends), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def generate_report():
        """ECOM-182: Generate expense reports"""
        try:
            user_id = get_jwt_identity()
            filters = request.args.to_dict()
            query = Expense.query.filter_by(user_id=user_id)

            if filters.get('start_date'):
                start_date = datetime.fromisoformat(filters['start_date'])
                query = query.filter(Expense.date >= start_date)

            if filters.get('end_date'):
                end_date = datetime.fromisoformat(filters['end_date'])
                query = query.filter(Expense.date <= end_date)

            if filters.get('category'):
                query = query.filter_by(category=filters['category'])

            expenses = query.all()

            total = sum(exp.amount for exp in expenses)
            average = total / len(expenses) if expenses else 0

            breakdown = {}
            for exp in expenses:
                if exp.category not in breakdown:
                    breakdown[exp.category] = 0
                breakdown[exp.category] += exp.amount

            return jsonify({
                'total': total,
                'average': round(average, 2),
                'count': len(expenses),
                'breakdown': breakdown,
                'expenses': [exp.to_dict() for exp in expenses]
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def export_expenses():
        """ECOM-183: Export expenses"""
        try:
            user_id = get_jwt_identity()
            format_type = request.args.get('format', 'csv')
            expenses = Expense.query.filter_by(user_id=user_id).all()

            if format_type == 'csv':
                csv_data = 'Date,Amount,Category,Description,Payment Method\n'
                for exp in expenses:
                    csv_data += f'{exp.date.date()},{exp.amount},{exp.category},{exp.description},{exp.payment_method}\n'
                return csv_data, 200, {'Content-Type': 'text/csv'}

            return jsonify([exp.to_dict() for exp in expenses]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def import_expenses():
        """ECOM-184: Import expenses"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            expenses_data = data.get('expenses', [])

            imported = 0
            duplicates = 0
            errors = []

            for exp_data in expenses_data:
                try:
                    duplicate = Expense.query.filter_by(user_id=user_id).filter(
                        Expense.amount == float(exp_data.get('amount')),
                        Expense.category == exp_data.get('category'),
                        Expense.date == datetime.fromisoformat(exp_data.get('date'))
                    ).first()

                    if duplicate:
                        duplicates += 1
                        continue

                    expense = Expense(
                        user_id=user_id,
                        amount=float(exp_data.get('amount')),
                        category=exp_data.get('category'),
                        date=datetime.fromisoformat(exp_data.get('date')),
                        description=exp_data.get('description', ''),
                        payment_method=exp_data.get('payment_method', 'Other')
                    )
                    db.session.add(expense)
                    imported += 1
                except Exception as e:
                    errors.append(str(e))

            db.session.commit()

            return jsonify({
                'imported': imported,
                'duplicates': duplicates,
                'errors': errors
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def create_recurring_expense():
        """ECOM-173: Create recurring expenses"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()

            if not data.get('amount') or data['amount'] <= 0:
                return jsonify({'error': 'Amount must be positive'}), 400
            if not data.get('category'):
                return jsonify({'error': 'Category is required'}), 400
            if not data.get('frequency'):
                return jsonify({'error': 'Frequency is required'}), 400

            recurring = RecurringExpense(
                user_id=user_id,
                amount=float(data['amount']),
                category=data['category'],
                description=data.get('description', ''),
                frequency=data['frequency'],
                start_date=datetime.fromisoformat(data.get('start_date', datetime.now().isoformat())),
                end_date=datetime.fromisoformat(data['end_date']) if data.get('end_date') else None
            )

            db.session.add(recurring)
            db.session.commit()

            return jsonify(recurring.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def get_all_expenses():
        """Get all expenses"""
        try:
            user_id = get_jwt_identity()
            expenses = Expense.query.filter_by(user_id=user_id).all()
            return jsonify([exp.to_dict() for exp in expenses]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def get_all_incomes():
        """Get all incomes"""
        try:
            user_id = get_jwt_identity()
            incomes = Income.query.filter_by(user_id=user_id).all()
            return jsonify([inc.to_dict() for inc in incomes]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
