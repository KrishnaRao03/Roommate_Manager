# RoomMate Manager

CPAN 214 Final Project – Django web application to help roommates manage shared households, expenses, and chores.

## 1. Project Overview

RoomMate Manager allows multiple users to:

- Join or create a household.
- Track shared expenses (who paid and who owes).
- Assign and track household chores.
- See a simple balance for each member.

This supports typical roommate problems such as:
- Who paid for rent, groceries, Wi-Fi, etc.  
- How to split costs fairly.  
- Who is responsible for which chores.

## 2. Main Features

### Authentication

- Django built-in authentication.
- Login and logout pages (`/accounts/login/`, `/accounts/logout/`).
- After login, user is redirected to **Dashboard**.
- If a logged-in user somehow goes to `/accounts/profile/` they are redirected to the dashboard.

### Dashboard

- Shows all households where the logged-in user is a member.
- Button **Open** to view details of a household.
- Button **Create New Household** to make a new one.

### Households

For each household:

- List of members.
- List of expenses.
- List of chores.
- Calculated balance for each member:
  - **Paid total** – how much the person paid.
  - **Share total** – how much they should pay.
  - **Balance** – positive = others owe them money.

### Expenses

- Add expense for a household:
  - Title
  - Amount
  - Category (e.g., Rent, Groceries, Utilities, Internet)
  - Date (HTML5 date picker)
- The logged-in member is recorded as `paid_by`.
- Cost is split equally between all members using an `ExpenseShare` model.
- After saving, user is redirected back to the household detail page.

### Chores

- Add chore for a household:
  - Title
  - Assigned to (a member of the same household)
  - Due date (HTML5 date picker)
  - Frequency (e.g., one-time, weekly)
  - Status (pending or completed)
- From the household detail page, a chore can be toggled between **pending** and **completed**.

## 3. Data Model (simplified)

- **User** – Django built-in auth user.
- **Household**
  - name
  - address
  - join_code
  - created_by (User)
- **Membership**
  - user (User)
  - household (Household)
  - role (e.g., admin, member)
  - share_percentage
- **ExpenseCategory**
  - name
- **Expense**
  - household (Household)
  - title
  - amount
  - category (ExpenseCategory)
  - date
  - paid_by (Membership)
- **ExpenseShare**
  - expense (Expense)
  - member (Membership)
  - share_amount
- **Chore**
  - household (Household)
  - title
  - assigned_to (Membership)
  - due_date
  - frequency
  - status

## 4. How to Run the Project

### Requirements

- Python 3.x
- pip
- virtualenv (recommended)

### Steps

```bash
# 1. Clone repository
git clone https://github.com/vrund4516/cpan214-roommate-manager.git
cd cpan214-roommate-manager

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

# 3. Install packages
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. Create superuser for admin and login
python manage.py createsuperuser

# 6. Run development server
python manage.py runserver
"# Roommate_Manager" 
