"""
Interactive finance dashboard built entirely from generic transaction data
(Date, Montant, Balance, Type). No personal category mapping required -
works on transactions_consolidated.csv alone.
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path


def prepare_data(df):
    """Aggregate expenses and income by generic Type."""
    expense_by_type = (
        df[df['Montant'] < 0]
        .groupby('Type')['Montant'].sum().abs()
        .sort_values(ascending=False)
    )

    income_by_type = (
        df[df['Montant'] > 0]
        .groupby('Type')['Montant'].sum()
        .sort_values(ascending=False)
    )

    return expense_by_type, income_by_type


def create_dashboard(df, expense_by_type, income_by_type):
    """Build the 3-panel dashboard figure."""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Account Balance', 'Expenses by Type', 'Income by Type'),
        specs=[
            [{'type': 'scatter', 'colspan': 2}, None],
            [{'type': 'pie'}, {'type': 'pie'}],
        ],
        vertical_spacing=0.15,
    )

    # 1. Balance over time, with date range selector/slider
    daily_balance = df.groupby('Date')['Balance'].last().reset_index()
    fig.add_trace(
        go.Scatter(
            x=daily_balance['Date'], y=daily_balance['Balance'],
            mode='lines', name='Balance',
            line=dict(color='rgba(0,100,250,0.8)'),
            hovertemplate='%{x}<br>Balance: %{y:.2f}€<extra></extra>',
        ),
        row=1, col=1,
    )
    fig.update_xaxes(
        rangeselector=dict(buttons=[
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=3, label="3m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all", label="All"),
        ]),
        rangeslider=dict(visible=True),
        type="date",
        row=1, col=1,
    )

    # 2. Expenses by generic Type (pie)
    fig.add_trace(
        go.Pie(
            labels=expense_by_type.index, values=expense_by_type.values,
            hole=0.3,
            hovertemplate='%{label}<br>%{value:.2f}€<br>%{percent}<extra></extra>',
        ),
        row=2, col=1,
    )

    # 3. Income by generic Type (pie)
    fig.add_trace(
        go.Pie(
            labels=income_by_type.index, values=income_by_type.values,
            hole=0.3,
            hovertemplate='%{label}<br>%{value:.2f}€<br>%{percent}<extra></extra>',
        ),
        row=2, col=2,
    )

    fig.update_layout(
        title_text='Finance Dashboard',
        height=900,
        showlegend=True,
    )

    return fig


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_file = project_root / 'data' / '03_final' / 'transactions_consolidated.csv'
    output_file = project_root / 'data' / '03_final' / 'finance_dashboard.html'

    print("📊 Loading data...")
    df = pd.read_csv(data_file, sep=';', decimal=',')
    df['Date'] = pd.to_datetime(df['Date'])
    print(f"✅ {len(df)} transactions loaded")
    print(f"📅 Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")

    print("\n🔄 Preparing data...")
    expense_by_type, income_by_type = prepare_data(df)

    print("🎨 Creating dashboard...")
    fig = create_dashboard(df, expense_by_type, income_by_type)

    fig.write_html(output_file)
    print(f"\n💾 Saved: {output_file}")

    total_revenue = df.loc[df['Montant'] > 0, 'Montant'].sum()
    total_expense = -df.loc[df['Montant'] < 0, 'Montant'].sum()
    print(f"\n📊 Summary:")
    print(f"   Total Revenue: +{total_revenue:.2f}€")
    print(f"   Total Expenses: -{total_expense:.2f}€")
    print(f"   Net: {total_revenue - total_expense:.2f}€")

    print(f"\n💳 Expense Types:")
    for t, amount in expense_by_type.items():
        print(f"   {t}: {amount:.2f}€")

    print(f"\n💰 Income Types:")
    for t, amount in income_by_type.items():
        print(f"   {t}: {amount:.2f}€")

    print("\n🌐 Open finance_dashboard.html in your browser!")


if __name__ == "__main__":
    main()
