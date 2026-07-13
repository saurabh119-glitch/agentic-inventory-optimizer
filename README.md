# agentic-inventory-optimizer
Enterprise-grade agentic inventory optimizer combining classical inventory formulas with LLM reasoning for actionable reorder recommendations. Built for SAP S/4HANA integration.
# Agentic Inventory Reorder Optimizer

An AI-powered inventory optimization system that combines classical inventory formulas with LLM-based reasoning to provide actionable reorder recommendations.

![Dashboard](screenshots/dashboard.png)

## Features
- 📊 Classical safety stock and reorder point calculations
- 🤖 LLM agent for anomaly detection and business reasoning
- 📈 Demand pattern analysis with visualization
- 📋 Priority-ranked action items with ROI impact
- 📤 Exportable reports (CSV/JSON)

## 🔗 Key Code Snippets (Gists)

- [Classical Inventory Formulas](https://gist.github.com/saurabh119-glitch/dc2fc965ff99f1cff9b088f10ba18eba)
- [LLM Agent Logic](https://gist.github.com/saurabh119-glitch/70c0b16fe6f56e713ad7be8cd1160ff0)
- [Synthetic Data Generator](https://gist.github.com/saurabh119-glitch/7f91c0a57c46245af65ff170a86d1493)
- [Action Prioritization](https://gist.github.com/saurabh119-glitch/d6b0749e4104f154df507e64188dca6f)
## Installation
```bash
pip install -r requirements.txt
streamlit run app.py
