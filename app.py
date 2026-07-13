import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import json
import os

# Set page config
st.set_page_config(
    page_title="Agentic Inventory Reorder Optimizer",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Agentic Inventory Reorder Optimizer")
st.caption("AI-powered inventory optimization with classical formulas + LLM reasoning")

# Sidebar: Generate synthetic data
with st.sidebar:
    st.header("⚙️ Data Configuration")
    num_skus = st.slider("Number of SKUs", 10, 100, 50)
    demand_volatility = st.slider("Demand Volatility", 0.1, 1.0, 0.3)
    
    if st.button("🔄 Regenerate Data"):
        st.session_state.data_generated = False
    
    st.markdown("---")
    st.subheader("📊 Optimization Logic")
    st.write("""
    **Classical Formulas**:
    • Safety Stock = Z × σ_demand × √(lead_time)  
    • Reorder Point = (avg_demand × lead_time) + safety_stock
    
    **LLM Agent**:  
    • Flags anomalies  
    • Suggests overrides  
    • Provides business reasoning
    """)

# Generate synthetic SKU data
def generate_synthetic_data(n_skus=50, volatility=0.3):
    """Generate realistic SKU inventory data"""
    np.random.seed(42)
    skus = []
    
    for i in range(n_skus):
        # Base parameters
        base_demand = np.random.uniform(50, 500)
        lead_time = np.random.randint(3, 15)
        cost = np.random.uniform(10, 200)
        current_stock = np.random.uniform(base_demand * 0.5, base_demand * 2)
        
        # Generate 90 days of demand history
        demand_history = []
        for day in range(90):
            daily_demand = base_demand + np.random.normal(0, base_demand * volatility)
            demand_history.append(max(0, daily_demand))
        
        # Calculate classical reorder point
        avg_demand = np.mean(demand_history)
        std_demand = np.std(demand_history)
        z_score = 1.65  # 95% service level
        
        safety_stock = z_score * std_demand * np.sqrt(lead_time)
        reorder_point = (avg_demand * lead_time) + safety_stock
        
        # Determine action needed
        action_needed = current_stock < reorder_point
        
        skus.append({
            "sku_id": f"SKU-{i+1:03}",
            "product_name": f"Product {i+1}",
            "category": np.random.choice(["Electronics", "Clothing", "Home", "Beauty"]),
            "current_stock": round(current_stock, 0),
            "reorder_point_classical": round(reorder_point, 0),
            "safety_stock": round(safety_stock, 0),
            "avg_daily_demand": round(avg_demand, 1),
            "lead_time_days": lead_time,
            "unit_cost": round(cost, 2),
            "demand_history": demand_history,
            "action_needed": action_needed
        })
    
    return pd.DataFrame(skus)

# Initialize session state
if 'data_generated' not in st.session_state or not st.session_state.data_generated:
    df = generate_synthetic_data(num_skus, demand_volatility)
    st.session_state.df = df
    st.session_state.data_generated = True
else:
    df = st.session_state.df

# LLM Agent Simulation (In real implementation, call OpenAI/Groq API)
def simulate_llm_agent(row):
    """Simulate LLM agent reasoning for demonstration"""
    issues = []
    recommendations = []
    
    # Handle edge case: short demand history
    demand_history = row['demand_history']
    if len(demand_history) < 8:
        recent_demand_avg = np.mean(demand_history)
        past_demand_avg = np.mean(demand_history)
    else:
        recent_demand_avg = np.mean(demand_history[-7:])
        past_demand_avg = np.mean(demand_history[:-7])
    
    # Flag potential issues
    if row['current_stock'] < row['avg_daily_demand'] * 2:
        issues.append("Critical stock level - risk of stockout within 2 days")
    
    if recent_demand_avg > past_demand_avg * 1.5:
        issues.append("Recent demand spike - consider increasing safety stock")
    
    if row['lead_time_days'] > 10:
        issues.append("Long lead time increases stockout risk")
    
    # Generate recommendations
    if issues:
        quantity_to_order = max(0, row['reorder_point_classical'] - row['current_stock'])
        recommendations.append(f"Order {int(quantity_to_order)} units immediately")
        if row['lead_time_days'] > 10:
            recommendations.append("Consider expediting shipment due to long lead time")
    
    return {
        "issues": issues,
        "recommendations": recommendations,
        "confidence": "High" if len(issues) <= 1 else "Medium"
    }

# Apply LLM agent to all SKUs
if 'llm_results' not in st.session_state:
    llm_results = []
    for _, row in df.iterrows():
        result = simulate_llm_agent(row)
        llm_results.append(result)
    st.session_state.llm_results = llm_results

# Create action items (fixed length matching)
action_df = df[df['action_needed']].copy()
if len(action_df) > 0:
    # Get LLM results only for action-needed SKUs
    action_indices = df[df['action_needed']].index
    action_llm_results = [st.session_state.llm_results[i] for i in action_indices]
    
    # Add LLM data to action_df
    action_df['llm_issues'] = [r['issues'] for r in action_llm_results]
    action_df['llm_recommendations'] = [r['recommendations'] for r in action_llm_results]

# Main dashboard
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total SKUs", len(df))
col2.metric("Action Required", len(action_df))
col3.metric("Avg Safety Stock", f"{df['safety_stock'].mean():.0f}")
col4.metric("Stockout Risk", f"{len(action_df)/len(df)*100:.1f}%")

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 Action Dashboard", "📈 Demand Analysis", "🤖 Agent Reasoning"])

with tab1:
    st.subheader("Priority Actions")
    
    if len(action_df) == 0:
        st.success("✅ All SKUs are well-stocked!")
    else:
        # Sort by urgency (lowest stock first)
        action_df_sorted = action_df.sort_values('current_stock').head(10)
        
        for idx, row in action_df_sorted.iterrows():
            with st.expander(f"🚨 {row['sku_id']} - {row['product_name']} ({row['category']})"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Current Stock", int(row['current_stock']))
                col2.metric("Reorder Point", int(row['reorder_point_classical']))
                col3.metric("Unit Cost", f"₹{row['unit_cost']:.2f}")
                
                st.subheader("🔍 LLM Agent Analysis")
                if row.get('llm_issues'):
                    st.warning("⚠️ **Issues Detected**:")
                    for issue in row['llm_issues']:
                        st.write(f"• {issue}")
                
                if row.get('llm_recommendations'):
                    st.success("💡 **Recommendations**:")
                    for rec in row['llm_recommendations']:
                        st.write(f"• {rec}")
                
                # ROI calculation
                stockout_cost = row['unit_cost'] * row['avg_daily_demand'] * 3  # 3 days stockout
                order_cost = row['unit_cost'] * max(0, row['reorder_point_classical'] - row['current_stock'])
                roi = (stockout_cost - order_cost) / order_cost * 100 if order_cost > 0 else 0
                
                st.subheader("💰 Business Impact")
                st.info(f"**Potential Stockout Cost**: ₹{stockout_cost:,.0f}\n**Order Cost**: ₹{order_cost:,.0f}\n**ROI**: {roi:.1f}%")

with tab2:
    st.subheader("Demand Patterns")
    selected_sku = st.selectbox("Select SKU", df['sku_id'].tolist())
    sku_data = df[df['sku_id'] == selected_sku].iloc[0]
    
    demand_df = pd.DataFrame({
        'Day': range(-89, 1),
        'Demand': sku_data['demand_history']
    })
    
    fig = px.line(demand_df, x='Day', y='Demand', title=f"Demand History for {selected_sku}")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Classical Calculation Details")
    st.write(f"""
    **Parameters**:
    - Average Daily Demand: {sku_data['avg_daily_demand']:.1f}
    - Demand Standard Deviation: {np.std(sku_data['demand_history']):.1f}
    - Lead Time: {sku_data['lead_time_days']} days
    - Service Level: 95% (Z = 1.65)
    
    **Calculations**:
    - Safety Stock = 1.65 × {np.std(sku_data['demand_history']):.1f} × √{sku_data['lead_time_days']} = {sku_data['safety_stock']:.0f}
    - Reorder Point = ({sku_data['avg_daily_demand']:.1f} × {sku_data['lead_time_days']}) + {sku_data['safety_stock']:.0f} = {sku_data['reorder_point_classical']:.0f}
    """)

with tab3:
    st.subheader("Agent Architecture")
    st.image("https://i.imgur.com/8ZkzFQl.png", caption="System Architecture", use_column_width=True)
    
    st.subheader("How It Works")
    st.write("""
    1. **Data Ingestion**: Synthetic SKU data with demand history, costs, lead times
    2. **Classical Engine**: Calculates safety stock and reorder points using standard formulas
    3. **LLM Agent**: Analyzes patterns, flags anomalies, provides business reasoning
    4. **Action Prioritization**: Ranks SKUs by stockout risk and ROI impact
    5. **Explainable Output**: Clear recommendations with confidence levels
    """)
    
    st.subheader("When to Trust Classical vs. LLM")
    st.info("""
    **Trust Classical When**:
    • Stable demand patterns
    • Historical data available
    • Standard inventory scenarios
    
    **Trust LLM When**:
    • Anomalous demand spikes
    • Seasonal/promotional events
    • Complex business constraints
    • Need for human-readable reasoning
    """)

# Export functionality
st.markdown("---")
st.subheader("📤 Export Results")
col1, col2 = st.columns(2)

with col1:
    csv = action_df.to_csv(index=False)
    st.download_button(
        "📥 Download Action Items (CSV)",
        csv,
        "inventory_actions.csv",
        "text/csv"
    )

with col2:
    # Create full report JSON
    report = {
        "summary": {
            "total_skus": len(df),
            "action_required": len(action_df),
            "stockout_risk_percentage": len(action_df)/len(df)*100 if len(df) > 0 else 0
        },
        "actions": action_df.to_dict('records')
    }
    st.download_button(
        "📄 Download Full Report (JSON)",
        json.dumps(report, indent=2),
        "inventory_report.json",
        "application/json"
    )

st.caption("Built with Streamlit | Classical formulas + LLM reasoning | Synthetic data for demonstration")
