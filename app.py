import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from budget import Budget

# 1. Page Configuration
st.set_page_config(page_title="Personal Budget Tracker", page_icon="💰", layout="wide")

if not os.path.exists("data"):
    os.makedirs("data")

# 2. Currency Formatting Helper
def fmt(value, currency):
    if currency == "USD":
        return f"${value:,.2f}"
    else:  # JPY
        return f"¥{int(value):,}"

# 3. Session State
if "budget" not in st.session_state:
    st.session_state.budget = None

# 4. Sidebar Setup
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Currency Selection
    currency_choice = st.radio("Select Currency", ["USD", "JPY"], horizontal=True)
    
    month_list = ["January", "February", "March", "April", "May", "June", 
                  "July", "August", "September", "October", "November", "December"]
    selected_month = st.selectbox("Select Month", month_list)
    
    # Dynamic step: $1.00 for USD, ¥100 for JPY
    step_val = 1.0 if currency_choice == "USD" else 100.0
    monthly_income = st.number_input(f"Monthly Income ({currency_choice})", min_value=0.0, step=step_val, value=1000.0 if currency_choice == "USD" else 150000.0)
    
    if st.button("Initialize/Reset Budget", use_container_width=True, type="primary"):
        st.session_state.budget = Budget(selected_month, monthly_income, currency_choice)
        st.success(f"Budget started in {currency_choice}")

# 5. Main UI
st.title("💰 Personal Budget Tracker")
st.markdown("---")

if st.session_state.budget:
    b = st.session_state.budget
    curr = b.currency

    # --- Metrics Section ---
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Income", fmt(b.income, curr))
    m2.metric("Total Spent", fmt(b.total_expenses(), curr), delta=f"-{fmt(b.total_expenses(), curr)}", delta_color="inverse")
    m3.metric("Remaining Balance", fmt(b.remaining_income(), curr))

    # --- Overspending Alerts ---
    overspent = b.overspent_categories()
    for item in overspent:
        st.error(f"⚠️ **Budget Alert:** Overspent in **{item['category']}**! ({fmt(item['spent'], curr)} / {fmt(item['limit'], curr)})")

    st.markdown("### 📝 Entry & Management")
    col1, col2 = st.columns(2)

    with col1:
        with st.form("expense_form", clear_on_submit=True):
            st.subheader("Add Expense")
            exp_cat = st.text_input("Category Name")
            exp_amt = st.number_input(f"Amount ({curr})", min_value=0.0, step=step_val)
            if st.form_submit_button("Add Expense", use_container_width=True):
                if exp_cat and exp_amt > 0:
                    b.add_expense(exp_cat.strip(), exp_amt)
                    st.rerun()

    with col2:
        with st.form("limit_form", clear_on_submit=True):
            st.subheader("Set Limit")
            existing_cats = list(b.expenses.keys())
            if existing_cats:
                lim_cat = st.selectbox("Select Category", options=existing_cats)
                lim_amt = st.number_input(f"Limit ({curr})", min_value=0.0, step=step_val)
                if st.form_submit_button("Set Limit", use_container_width=True):
                    b.set_limit(lim_cat, lim_amt)
                    st.rerun()
            else:
                st.info("Add an expense first to define categories.")
                st.form_submit_button("Set Limit", disabled=True, use_container_width=True)

    st.divider()

    # --- Visuals ---
    if b.expenses:
        st.markdown("### 📊 Data Visualization")
        v1, v2 = st.columns(2)
        with v1:
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            ax1.pie(b.expenses.values(), labels=b.expenses.keys(), autopct='%1.1f%%', startangle=140)
            ax1.set_title("Spending Breakdown")
            st.pyplot(fig1)
        with v2:
            chart_data = pd.DataFrame({
                "Spent": [b.expenses.get(c, 0) for c in existing_cats],
                "Limit": [b.limits.get(c, 0) for c in existing_cats]
            }, index=existing_cats)
            st.bar_chart(chart_data)

    # --- Table ---
    st.markdown("### 📋 Budget Summary")
    df = b.to_dataframe()
    
    # Table formatting based on currency
    tbl_fmt = "$%.2f" if curr == "USD" else "¥%d"
    
    st.dataframe(
        df, 
        use_container_width=True,
        column_config={
            "Amount Spent": st.column_config.NumberColumn(format=tbl_fmt),
            "Limit": st.column_config.NumberColumn(format=tbl_fmt),
        }
    )

    # Save/Download
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Save to Server", use_container_width=True):
            b.to_csv(f"data/budget_{b.month.lower()}.csv")
            st.success("File Saved!")
    with c2:
        st.download_button("📥 Download CSV", df.to_csv(index=False), f"budget_{b.month}.csv", "text/csv", use_container_width=True)
else:
    st.info("👈 Select currency and income in the sidebar to begin.")