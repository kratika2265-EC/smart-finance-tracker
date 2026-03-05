import tkinter as tk
from tkinter import messagebox
import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt

# Folder paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

CSV_PATH = os.path.join(DATA_DIR, "transction.csv")
BUDGET_PATH = os.path.join(DATA_DIR, "budgets.csv")

os.makedirs(DATA_DIR, exist_ok=True)

# Ensure CSV exists
for path, header in [(CSV_PATH, ["date", "type", "category", "amount"]),
                     (BUDGET_PATH, ["category", "limit"])]:
    if not os.path.exists(path):
        with open(path, "w", newline="") as f:
            csv.writer(f).writerow(header)

# Add transaction
def add_transaction(t_type, category, amount, date=None):
    if date is None:
        date = datetime.today().strftime("%Y-%m-%d")

    with open(CSV_PATH, "a", newline="") as file:
        csv.writer(file).writer.writerow([date, t_type, category, amount])

# Load transactions
def load_transactions():
    transactions = []
    balance = 0
    income = 0
    expense = 0

    with open(CSV_PATH, "r") as file:
        for row in csv.DictReader(file):
            try:
                amt = float(row["amount"])
            except:
                continue
            transactions.append(row)
            if row["type"].lower()=="income":
                balance += amt
                income += amt
            else:
                balance -= abs(amt)
                expense += abs(amt)
    return transactions, balance, income, expense

# Save budget
def save_budget(category, limit):
    budgets = {}
    if os.path.exists(BUDGET_PATH):
        with open(BUDGET_PATH, "r") as f:
            for r in csv.DictReader(f):
                budgets[r["category"].lower()] = float(r["limit"])
    budgets[category.lower()] = limit
    with open(BUDGET_PATH, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["category","limit"])
        for c,l in budgets.items():
            w.writerow([c,l])

# Load budgets
def load_budgets():
    b={}
    if not os.path.exists(BUDGET_PATH): return b
    with open(BUDGET_PATH,"r") as f:
        for r in csv.DictReader(f):
            b[r["category"].lower()] = float(r["limit"])
    return b

# Check budget
def check_budget(transactions, budgets):
    spent={}
    warn=[]
    for t in transactions:
        c=t["category"].lower()
        spent[c] = spent.get(c,0) + abs(float(t["amount"]))
    for c,l in budgets.items():
        if c in spent and spent[c]>l:
            warn.append(f"⚠ {c.upper()} exceeded by ₹{spent[c]-l:.2f}")
    return warn, spent

# Screens
def open_income_screen():
    w=tk.Toplevel();w.title("Income");w.geometry("280x220");w.configure(bg="#F8F1FF",padx=15,pady=15)
    tk.Label(w,text="Amount",font=("Arial",9,"bold"),bg="#F8F1FF").pack()
    a=tk.Entry(w,width=18,bd=2,relief="flat");a.pack(pady=5,ipady=4)
    tk.Label(w,text="Category",font=("Arial",9,"bold"),bg="#F8F1FF").pack()
    c=tk.Entry(w,width=18,bd=2,relief="flat");c.pack(pady=5,ipady=4)
    def s():
        add_transaction("income",c.get(),float(a.get()));messagebox.showinfo("Saved","Income Added");w.destroy()
    tk.Button(w,text="Save",width=16,font=("Arial",10,"bold"),bg="#00b894",fg="white",bd=0,command=s).pack(pady=12,ipady=3)

def open_expense_screen():
    w=tk.Toplevel();w.title("Expense");w.geometry("280x220");w.configure(bg="#F8F1FF",padx=15,pady=15)
    tk.Label(w,text="Amount",font=("Arial",9,"bold"),bg="#F8F1FF").pack()
    a=tk.Entry(w,width=18,bd=2,relief="flat");a.pack(pady=5,ipady=4)
    tk.Label(w,text="Category",font=("Arial",9,"bold"),bg="#F8F1FF").pack()
    c=tk.Entry(w,width=18,bd=2,relief="flat");c.pack(pady=5,ipady=4)
    def s():
        add_transaction("expense",c.get(),-float(a.get()));messagebox.showinfo("Saved","Expense Added");w.destroy()
    tk.Button(w,text="Save",width=16,font=("Arial",10,"bold"),bg="#d63031",fg="white",bd=0,command=s).pack(pady=12,ipady=3)

def open_budget_screen():
    w=tk.Toplevel();w.title("Budget");w.geometry("280x230");w.configure(bg="#F8F1FF",padx=15,pady=15)
    tk.Label(w,text="Category",font=("Arial",9,"bold"),bg="#F8F1FF").pack()
    c=tk.Entry(w,width=18,bd=2,relief="flat");c.pack(pady=5,ipady=4)
    tk.Label(w,text="Limit ₹",font=("Arial",9,"bold"),bg="#F8F1FF").pack()
    l=tk.Entry(w,width=18,bd=2,relief="flat");l.pack(pady=5,ipady=4)
    def s():
        save_budget(c.get(),float(l.get()));messagebox.showinfo("Saved","Budget Set");w.destroy()
    tk.Button(w,text="Save",width=16,font=("Arial",10,"bold"),bg="#6c5ce7",fg="white",bd=0,command=s).pack(pady=14,ipady=3)

def open_report_screen():
    w=tk.Toplevel();w.title("Report");w.geometry("360x420");w.configure(bg="#F8F1FF",padx=15,pady=15)
    t,b,i,e = load_transactions()
    bd = load_budgets()
    warn,sp = check_budget(t,bd)
    tk.Label(w,text="Spending Report ✦",font=("Helvetica",16,"bold"),bg="#F8F1FF").pack(pady=5)
    if warn: tk.Label(w,text="\n".join(warn),font=("Arial",8,"bold"),bg="white",fg="#d63031").pack(fill="x",pady=6,ipady=5)
    def pie():
        cd={k:v for k,v in sp.items() if k!="salary"}
        if sum(cd.values())>0:
            plt.figure();plt.pie(cd.values(),labels=cd.keys(),autopct="%1.1f%%");plt.title("Category-wise Spending");plt.show()
        else: messagebox.showinfo("Report","No spending data!")
    def bar():
        if sp: plt.figure();plt.bar(sp.keys(),sp.values());plt.title("Spending Comparison");plt.show()
    tk.Button(w,text="🥧 Pie Chart",width=18,font=("Arial",10,"bold"),bg="#a29bfe",fg="white",bd=0,command=pie).pack(pady=10,ipady=4)
    tk.Button(w,text="📊 Bar Chart",width=18,font=("Arial",10),bg="#74b9ff",fg="white",bd=0,command=bar).pack(pady=6,ipady=4)
    tk.Label(w,text=f"\nBalance: ₹{b:.2f}\nIncome: ₹{i:.2f}\nExpense: ₹{e:.2f}",font=("Arial",9),bg="white",fg="#2d3436").pack(fill="x",pady=12,ipady=8)

def open_dashboard():
    d=tk.Toplevel();d.title("Dashboard");d.geometry("380x480");d.configure(bg="#F8F1FF",padx=20,pady=20)
    t,b,i,e = load_transactions()
    tk.Label(d,text="Smart Finance ✦",font=("Helvetica",18,"bold"),bg="#F8F1FF").pack(pady=(0,15))
    c=tk.Frame(d,bg="white");c.pack(fill="x",ipady=15)
    tk.Label(c,text="Current Balance",font=("Arial",10,"bold"),bg="white",fg="#636e72").pack()
    tk.Label(c,text=f"₹ {b:.2f}",font=("Arial",26,"bold"),bg="white",fg="#6c5ce7").pack(pady=4)
    tk.Label(c,text=f"Income: ₹{i:.2f}   Expense: ₹{e:.2f}",font=("Arial",9),bg="white").pack()
    tk.Label(d,text="Transaction History",font=("Arial",11,"bold"),bg="#F8F1FF").pack(pady=6)
    lb=tk.Listbox(d,height=8,font=("Arial",9),bd=0,bg="white",fg="#2d3436");lb.pack(fill="x",pady=4)
    for x in t: lb.insert("end",f"{x['date']} | {x['category'].capitalize()} | {'+' if x['type']=='income' else '-'}₹{abs(float(x['amount'])):.2f}")
    bs={"width":18,"font":("Arial",10,"bold"),"fg":"white","bd":0,"relief":"flat","activeforeground":"white"}
    tk.Button(d,text="Add Income",bg="#00b894",**bs,command=open_income_screen).pack(pady=5)
    tk.Button(d,text="Add Expense",bg="#d63031",**bs,command=open_expense_screen).pack(pady=5)
    tk.Button(d,text="Set Budget",bg="#0984e3",**bs,command=open_budget_screen).pack(pady=5)
    tk.Button(d,text="View Report",bg="#6c5ce7",**bs,command=open_report_screen).pack(pady=5)
    tk.Label(d,text="Track • Save • Glow ✨",font=("Arial",8),bg="#F8F1FF",fg="#636e72").pack(side="bottom",pady=10)

if __name__=="__main__":
    r=tk.Tk();r.title("Smart Finance");r.geometry("330x230");r.configure(bg="#F8F1FF")
    tk.Label(r,text="Smart Finance Tracker ✦",font=("Helvetica",16,"bold"),bg="#F8F1FF").pack(pady=15)
    tk.Button(r,text="Open Dashboard",width=20,font=("Arial",11,"bold"),bg="#6c5ce7",fg="white",bd=0,command=open_dashboard).pack(pady=8,ipady=4)
    tk.Button(r,text="View Spending Report",width=20,font=("Arial",10),bg="#a29bfe",fg="white",bd=0,command=open_report_screen).pack(pady=6,ipady=4)
    r.mainloop()
