const API_BASE = '';
let expensesList = [];
let incomesList = [];
let categories = [];
let budgetList = [];

function getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
}

document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/';
        return;
    }

    await loadCategories();
    await loadDashboard();
    await loadExpenses();
    await loadBudgets();
    setupEventListeners();
    showSection('dashboard');
});

function setupEventListeners() {
    document.getElementById('expenseForm').addEventListener('submit', addExpense);
    document.getElementById('incomeForm').addEventListener('submit', addIncome);
    document.getElementById('budgetForm').addEventListener('submit', setBudget);
    document.getElementById('csvFile').addEventListener('change', importCSV);
}

async function loadCategories() {
    try {
        const res = await fetch(`${API_BASE}/api/categories/predefined`, {
            headers: getAuthHeaders()
        });
        const data = await res.json();
        categories = data;
        updateCategorySelects();
    } catch (e) {
        console.error('Load categories error:', e);
    }
}

function updateCategorySelects() {
    const selects = ['expCategory', 'budgetCategory'];
    selects.forEach(id => {
        const select = document.getElementById(id);
        if (select) {
            select.innerHTML = '<option value="">Select Category</option>';
            categories.forEach(cat => {
                const opt = document.createElement('option');
                opt.value = cat.name;
                opt.textContent = cat.name;
                select.appendChild(opt);
            });
        }
    });
}

async function loadDashboard() {
    try {
        const res = await fetch(`${API_BASE}/api/dashboard`, {
            headers: getAuthHeaders()
        });
        const data = await res.json();
        document.getElementById('totalIncome').textContent = `₹${data.total_income?.toFixed(2) || 0}`;
        document.getElementById('totalExpenses').textContent = `₹${data.total_expenses?.toFixed(2) || 0}`;
        document.getElementById('netBalance').textContent = `₹${data.net_balance?.toFixed(2) || 0}`;
        document.getElementById('savingsRate').textContent = `${data.savings_rate?.toFixed(1) || 0}%`;
    } catch (e) {
        console.error('Dashboard error:', e);
    }
}

async function loadExpenses() {
    try {
        const res = await fetch(`${API_BASE}/api/expenses`, {
            headers: getAuthHeaders()
        });
        expensesList = await res.json();
        renderExpenses();
    } catch (e) {
        console.error('Load expenses error:', e);
    }
}

function renderExpenses() {
    const list = document.getElementById('expensesList');
    list.innerHTML = '';
    expensesList.slice(-10).reverse().forEach(exp => {
        const item = document.createElement('div');
        item.className = 'list-item';
        item.innerHTML = `
            <div class="list-item-header">
                <div>
                    <div class="list-item-title">${exp.description || exp.category}</div>
                    <small>${exp.date} | ${exp.category}</small>
                </div>
                <div class="list-item-amount">₹${exp.amount}</div>
            </div>
        `;
        list.appendChild(item);
    });
}

async function addExpense(e) {
    e.preventDefault();
    const expense = {
        amount: parseFloat(document.getElementById('expAmount').value),
        category: document.getElementById('expCategory').value,
        description: document.getElementById('expDescription').value,
        date: document.getElementById('expDate').value,
        payment_method: document.getElementById('expMethod').value
    };
    try {
        await fetch(`${API_BASE}/api/expenses`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(expense)
        });
        document.getElementById('expenseForm').reset();
        await loadExpenses();
        await loadDashboard();
    } catch (e) {
        alert('Error adding expense');
    }
}

async function addIncome(e) {
    e.preventDefault();
    const income = {
        amount: parseFloat(document.getElementById('incAmount').value),
        category: document.getElementById('incCategory').value,
        source: document.getElementById('incSource').value,
        date: document.getElementById('incDate').value
    };
    try {
        await fetch(`${API_BASE}/api/incomes`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(income)
        });
        document.getElementById('incomeForm').reset();
        await loadDashboard();
    } catch (e) {
        alert('Error adding income');
    }
}

async function loadBudgets() {
    try {
        const res = await fetch(`${API_BASE}/api/budgets/tracking`, {
            headers: getAuthHeaders()
        });
        budgetList = await res.json();
        renderBudgets();
    } catch (e) {
        console.error('Load budgets error:', e);
    }
}

function renderBudgets() {
    const list = document.getElementById('budgetList');
    list.innerHTML = '';
    budgetList.forEach(budget => {
        const percent = (budget.spent / budget.budget * 100);
        let status = 'success';
        if (percent > 90) status = 'danger';
        else if (percent > 75) status = 'warning';

        const item = document.createElement('div');
        item.className = 'list-item';
        item.innerHTML = `
            <div class="list-item-header">
                <div>${budget.category}</div>
                <div class="list-item-amount">₹${budget.spent?.toFixed(2)} / ₹${budget.budget}</div>
            </div>
            <div class="budget-bar">
                <div class="budget-progress ${status}" style="width: ${Math.min(percent, 100)}%"></div>
            </div>
            <small>${percent.toFixed(0)}% used</small>
        `;
        list.appendChild(item);
    });
}

async function setBudget(e) {
    e.preventDefault();
    const budget = {
        category: document.getElementById('budgetCategory').value,
        amount: parseFloat(document.getElementById('budgetAmount').value),
        budget_type: document.getElementById('budgetType').value
    };
    try {
        await fetch(`${API_BASE}/api/budgets`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(budget)
        });
        document.getElementById('budgetForm').reset();
        await loadBudgets();
    } catch (e) {
        alert('Error setting budget');
    }
}

async function loadCharts() {
    try {
        const catRes = await fetch(`${API_BASE}/api/analytics/category-breakdown`, {
            headers: getAuthHeaders()
        });
        const catData = await catRes.json();
        drawCategoryChart(catData);

        const trendRes = await fetch(`${API_BASE}/api/analytics/trends`, {
            headers: getAuthHeaders()
        });
        const trendData = await trendRes.json();
        drawTrendsChart(trendData);
    } catch (e) {
        console.error('Charts error:', e);
    }
}

function drawCategoryChart(data) {
    const ctx = document.getElementById('categoryChart')?.getContext('2d');
    if (!ctx) return;
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.category),
            datasets: [{
                data: data.map(d => d.amount),
                backgroundColor: ['#4CAF50', '#2196F3', '#FF9800', '#f44336', '#9C27B0', '#00BCD4']
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

function drawTrendsChart(data) {
    const ctx = document.getElementById('trendsChart')?.getContext('2d');
    if (!ctx) return;
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.month),
            datasets: [{
                label: 'Expenses',
                data: data.map(d => d.total),
                borderColor: '#f44336',
                tension: 0.4
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

function showSection(name) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById(name)?.classList.add('active');
    if (name === 'analytics') loadCharts();
}

function exportCSV() {
    let csv = 'Date,Category,Amount,Description,Method\n';
    expensesList.forEach(e => {
        csv += `${e.date},${e.category},${e.amount},"${e.description}",${e.payment_method}\n`;
    });
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'expenses.csv';
    a.click();
}

function triggerImport() {
    document.getElementById('csvFile').click();
}

async function importCSV(e) {
    const file = e.target.files[0];
    const text = await file.text();
    const lines = text.split('\n').slice(1);
    const expenses = lines.filter(l => l).map(l => {
        const [date, category, amount, desc, method] = l.split(',');
        return { date, category, amount: parseFloat(amount), description: desc?.replace(/"/g, ''), payment_method: method };
    });
    try {
        await fetch(`${API_BASE}/api/expenses/import`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ expenses })
        });
        await loadExpenses();
    } catch (e) {
        alert('Import error');
    }
}
