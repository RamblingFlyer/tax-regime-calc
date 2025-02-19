import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from groq import Groq
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = "mongodb+srv://Payrolluser:payrolluser@cluster0.ccvba.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["your_database"]
collection = db["your_collection"]
questions_collection = db["questions"]

# Set page config
st.set_page_config(
    page_title="Indian Tax Regime Calculator",
    page_icon="💰",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main {
    padding: 2rem;
}
.stApp {
    background: linear-gradient(to bottom, #1a1a1a, #2d2d2d);
    color: #ffffff;
}
.css-1d391kg {
    padding: 2rem;
}
.stButton>button {
    background: linear-gradient(to right, #4a4a4a, #2d2d2d);
    color: white;
    border: none;
}
.stTextInput>div>div>input, .stNumberInput>div>div>input {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
    border: 1px solid #4a4a4a;
}
.stSelectbox>div>div>div {
    background-color: #2d2d2d;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("💰 Indian Tax Regime Calculator")
st.markdown("""Compare the old and new tax regimes to find out which one is best suited for you.""")

# Input section
st.subheader("Enter Your Income Details")
col1, col2 = st.columns(2)

with col1:
    salary = st.number_input("Annual Salary", min_value=0, value=0)
    investment_80c = st.number_input("Section 80C Investments (Old Regime)", min_value=0, value=0, max_value=150000)
    hra = st.number_input("HRA Exemption (Old Regime)", min_value=0, value=0)

with col2:
    standard_deduction = st.number_input("Standard Deduction (Old Regime)", min_value=0, value=0)
    other_deductions = st.number_input("Other Deductions (Old Regime)", min_value=0, value=0)

# Calculate taxable income for both regimes
def calculate_old_regime(salary, investment_80c, hra, standard_deduction, other_deductions):
    taxable_income = salary - min(investment_80c, 150000) - hra - standard_deduction - other_deductions
    tax = 0
    
    if taxable_income <= 250000:
        tax = 0
    elif taxable_income <= 500000:
        tax = (taxable_income - 250000) * 0.05
    elif taxable_income <= 1000000:
        tax = 12500 + (taxable_income - 500000) * 0.2
    else:
        tax = 112500 + (taxable_income - 1000000) * 0.3
    
    # Add cess
    tax = tax + (tax * 0.04)
    return tax, taxable_income

def calculate_new_regime(salary):
    taxable_income = salary
    tax = 0
    
    if taxable_income <= 300000:
        tax = 0
    elif taxable_income <= 600000:
        tax = (taxable_income - 300000) * 0.05
    elif taxable_income <= 900000:
        tax = 15000 + (taxable_income - 600000) * 0.1
    elif taxable_income <= 1200000:
        tax = 45000 + (taxable_income - 900000) * 0.15
    elif taxable_income <= 1500000:
        tax = 90000 + (taxable_income - 1200000) * 0.2
    else:
        tax = 150000 + (taxable_income - 1500000) * 0.3
    
    # Add cess
    tax = tax + (tax * 0.04)
    return tax, taxable_income

# Calculate taxes
old_tax, old_taxable = calculate_old_regime(salary, investment_80c, hra, standard_deduction, other_deductions)
new_tax, new_taxable = calculate_new_regime(salary)

# Display results
st.subheader("Tax Comparison")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Old Regime Tax", f"₹{old_tax:,.2f}")
    
with col2:
    st.metric("New Regime Tax", f"₹{new_tax:,.2f}")
    
with col3:
    savings = abs(old_tax - new_tax)
    better_regime = "Old" if old_tax < new_tax else "New"
    st.metric("Tax Savings", f"₹{savings:,.2f}", f"{better_regime} Regime is Better")

# Visualizations
st.subheader("Visual Comparison")

# Bar chart comparing taxes
fig1 = go.Figure(data=[
    go.Bar(
        name='Tax Amount',
        x=['Old Regime', 'New Regime'],
        y=[old_tax, new_tax],
        text=[f'₹{old_tax:,.0f}', f'₹{new_tax:,.0f}'],
        textposition='auto',
    )
])

fig1.update_layout(
    title='Tax Amount Comparison',
    yaxis_title='Tax Amount (₹)',
    plot_bgcolor='rgba(0,0,0,0)',
    showlegend=False
)

st.plotly_chart(fig1, use_container_width=True)

# Pie charts for income breakdown
col1, col2 = st.columns(2)

with col1:
    old_regime_data = pd.DataFrame({
        'Category': ['Tax', 'Take Home'],
        'Amount': [old_tax, salary - old_tax]
    })
    
    fig2 = px.pie(
        old_regime_data,
        values='Amount',
        names='Category',
        title='Old Regime Income Distribution'
    )
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    new_regime_data = pd.DataFrame({
        'Category': ['Tax', 'Take Home'],
        'Amount': [new_tax, salary - new_tax]
    })
    
    fig3 = px.pie(
        new_regime_data,
        values='Amount',
        names='Category',
        title='New Regime Income Distribution'
    )
    st.plotly_chart(fig3, use_container_width=True)

# Effective tax rate comparison
old_effective_rate = (old_tax / salary * 100) if salary > 0 else 0
new_effective_rate = (new_tax / salary * 100) if salary > 0 else 0

fig4 = go.Figure(data=[
    go.Bar(
        name='Effective Tax Rate',
        x=['Old Regime', 'New Regime'],
        y=[old_effective_rate, new_effective_rate],
        text=[f'{old_effective_rate:.1f}%', f'{new_effective_rate:.1f}%'],
        textposition='auto',
    )
])

fig4.update_layout(
    title='Effective Tax Rate Comparison',
    yaxis_title='Effective Tax Rate (%)',
    plot_bgcolor='rgba(0,0,0,0)',
    showlegend=False
)

st.plotly_chart(fig4, use_container_width=True)

# Recommendations
st.subheader("Recommendation")

# Prepare the context for the LLM
context = f"""
Financial Information:
- Annual Salary: ₹{salary:,.2f}
- Section 80C Investments: ₹{investment_80c:,.2f}
- HRA Exemption: ₹{hra:,.2f}
- Standard Deduction: ₹{standard_deduction:,.2f}
- Other Deductions: ₹{other_deductions:,.2f}

Tax Calculations:
- Old Regime Tax: ₹{old_tax:,.2f}
- New Regime Tax: ₹{new_tax:,.2f}
- Tax Savings: ₹{savings:,.2f}
- Old Regime Effective Rate: {old_effective_rate:.1f}%
- New Regime Effective Rate: {new_effective_rate:.1f}%

Better Regime: {better_regime} Regime
"""

# Generate personalized recommendation using Groq
prompt = f"""Based on the following financial information for an Indian taxpayer, provide a detailed, personalized tax regime recommendation. Focus on explaining why the recommended regime is better and what specific advantages it offers. Keep the tone professional but conversational.

{context}

Provide a comprehensive analysis in this format:
1. Clear recommendation statement
2. 3-4 specific reasons why this regime is advantageous
3. Additional financial planning tips based on their current tax situation
"""


# Initialize Groq client
client_groq = Groq(
    api_key="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"
)

with st.spinner('Generating personalized recommendation...'):
    try:
        completion = client_groq.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are a knowledgeable Indian tax advisor providing personalized recommendations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        recommendation = completion.choices[0].message.content
        
        # Display the recommendation
        if old_tax < new_tax:
            st.success(f"The Old Tax Regime is better for you. You save ₹{savings:,.2f} annually compared to the New Regime.")
        else:
            st.success(f"The New Tax Regime is better for you. You save ₹{savings:,.2f} annually compared to the Old Regime.")
            
        st.markdown(recommendation)
        
    except Exception as e:
        st.error("Unable to generate personalized recommendation. Please try again later.")
        st.markdown("""
        ### General Recommendation
        - Compare your tax liability under both regimes
        - Consider your deductions and exemptions
        - Choose the regime that results in lower tax liability
        """)

# Q&A Section
st.subheader("💬 Tax Regime Q&A")
st.markdown("Ask any questions you have about the tax regimes and get personalized answers.")

# Enhanced query box styling
st.markdown("""
<style>
.stTextInput>div>div>input {
    font-size: 1.1rem !important;
    background: linear-gradient(to right, rgba(74, 74, 74, 0.2), rgba(45, 45, 45, 0.3)) !important;
    border: 2px solid rgba(74, 74, 74, 0.5) !important;
    border-radius: 15px !important;
    padding: 1rem 1.5rem !important;
    margin: 1rem 0 !important;
    color: #ffffff !important;
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.3s ease !important;
}

.stTextInput>div>div>input:focus {
    border-color: #6c63ff !important;
    box-shadow: 0 0 20px rgba(108, 99, 255, 0.2) !important;
    transform: translateY(-2px) !important;
}

.stTextInput>div>div>input::placeholder {
    color: rgba(255, 255, 255, 0.6) !important;
    font-style: italic;
}
.chat-message {
    background: linear-gradient(to right, rgba(74, 74, 74, 0.2), rgba(45, 45, 45, 0.2));
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    animation: fadeIn 0.5s ease;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)
user_question = st.text_input("User Question", placeholder="Example: What are the main differences between old and new tax regimes?", key="query_box", label_visibility="collapsed")


if user_question:
    with st.spinner('Analyzing your question...'):
        try:
            # Prepare context with user's financial information
            qa_context = f"""
            Based on the user's financial information:
            - Annual Salary: ₹{salary:,.2f}
            - Current Tax Regime: {better_regime}
            - Tax Savings: ₹{savings:,.2f}
            
            Question: {user_question}
            
            Provide a clear, detailed answer focusing on Indian tax regulations. If the question is related to the user's 
            specific financial situation, incorporate the above context into your response. Keep the tone professional 
            but conversational.
            """
            
            completion = client_groq.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable Indian tax advisor. Provide accurate, helpful answers about Indian tax regimes and regulations."},
                    {"role": "user", "content": qa_context}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Display the response in an enhanced chat-like format
            st.markdown(f"""
            <div class='chat-message'>
            {completion.choices[0].message.content}
            </div>
            """, unsafe_allow_html=True)

            # Store user question in MongoDB
            questions_collection.insert_one({
                "question": user_question,
                "asked_at": datetime.now(),
                "answer": completion.choices[0].message.content
            })
            
        except Exception as e:
            st.error("Unable to process your question. Please try again later.")
    

