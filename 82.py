# Prompt 82

from flask import Flask, request, render_template
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)

    fig = px.line(df, x='Date', y='Amount', color='Account', title='Spending Trends')
    graphJSON = fig.to_json()

    monthly_budget = df.groupby(df['Date'].dt.to_period('M')).sum().mean()
    budget_recommendation = monthly_budget * 1.1

    return render_template('result.html', graphJSON=graphJSON, budget_recommendation=budget_recommendation)

if __name__ == '__main__':
    app.run(debug=True)