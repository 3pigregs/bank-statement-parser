"""
Interactive Finance Dashboard with date filtering and category breakdown.
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path


def prepare_data(df):
    """Prepare data for visualization."""
    # Add expense/revenue flag
    df['Type'] = df['Montant'].apply(lambda x: 'Revenue' if x > 0 else 'Expense')
    
    # Monthly aggregation
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    
    monthly = df.groupby('Month').agg({
        'Montant': lambda x: {
            'revenue': x[x > 0].sum(),
            'expense': x[x < 0].sum(),
            'net': x.sum()
        }
    })
    
    monthly_summary = pd.DataFrame({
        'Month': monthly.index,
        'Revenue': [x['revenue'] for x in monthly['Montant']],
        'Expense': [abs(x['expense']) for x in monthly['Montant']],
        'Net': [x['net'] for x in monthly['Montant']]
    })
    
    # Category aggregation (exclude Uncategorized)
    df_cat = df[df['Category'] != 'Uncategorized'].copy()
    
    # Expenses by category
    expense_by_cat = df_cat[df_cat['Type'] == 'Expense'].groupby('Category')['Montant'].sum().abs()
    expense_by_cat = expense_by_cat.sort_values(ascending=False)
    
    # Revenue by category
    revenue_by_cat = df_cat[df_cat['Type'] == 'Revenue'].groupby('Category')['Montant'].sum()
    revenue_by_cat = revenue_by_cat.sort_values(ascending=False)
    
    # Monthly by category (expenses)
    monthly_cat = df_cat[df_cat['Type'] == 'Expense'].groupby(['Month', 'Category'])['Montant'].sum().abs().reset_index()
    
    return monthly_summary, expense_by_cat, revenue_by_cat, monthly_cat


def create_dashboard(df, monthly_summary, expense_by_cat, revenue_by_cat, monthly_cat):
    """Create interactive dashboard."""
    
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Monthly Revenue vs Expenses',
            'Monthly Net (Revenue - Expenses)',
            'Expenses by Category',
            'Revenue by Category',
            'Monthly Expenses by Category',
            'Account Balance'
        ),
        specs=[
            [{'type': 'bar'}, {'type': 'bar'}],
            [{'type': 'pie'}, {'type': 'pie'}],
            [{'type': 'bar'}, {'type': 'scatter'}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.12
    )
    
    # 1. Monthly Revenue vs Expenses (Waterfall)
    fig.add_trace(
        go.Bar(
            x=monthly_summary['Month'],
            y=monthly_summary['Revenue'],
            name='Revenue',
            marker_color='rgba(0,200,0,0.7)',
            text=monthly_summary['Revenue'].round(0),
            texttemplate='+%{text:.0f}€',
            textposition='outside',
            hovertemplate='Revenue: +%{y:.2f}€<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=monthly_summary['Month'],
            y=-monthly_summary['Expense'],  # Negative for waterfall effect
            name='Expenses',
            marker_color='rgba(200,0,0,0.7)',
            text=monthly_summary['Expense'].round(0),
            texttemplate='-%{text:.0f}€',
            textposition='outside',
            hovertemplate='Expenses: %{text:.2f}€<extra></extra>'
        ),
        row=1, col=1
    )
    
    # 2. Monthly Net
    colors = ['green' if x >= 0 else 'red' for x in monthly_summary['Net']]
    fig.add_trace(
        go.Bar(
            x=monthly_summary['Month'],
            y=monthly_summary['Net'],
            name='Net',
            marker_color=colors,
            text=monthly_summary['Net'].round(0),
            texttemplate='%{text:+.0f}€',
            textposition='outside',
            showlegend=False,
            hovertemplate='Net: %{y:+.2f}€<extra></extra>'
        ),
        row=1, col=2
    )
    
    # 3. Expenses by Category (Pie)
    if len(expense_by_cat) > 0:
        fig.add_trace(
            go.Pie(
                labels=expense_by_cat.index,
                values=expense_by_cat.values,
                hole=0.3,
                marker=dict(colors=['#ff6b6b', '#ee5a6f', '#c44569', '#f38181', '#e17055', '#d63031', '#fab1a0']),
                showlegend=True,
                hovertemplate='%{label}<br>%{value:.2f}€<br>%{percent}<extra></extra>'
            ),
            row=2, col=1
        )
    
    # 4. Revenue by Category (Pie)
    if len(revenue_by_cat) > 0:
        fig.add_trace(
            go.Pie(
                labels=revenue_by_cat.index,
                values=revenue_by_cat.values,
                hole=0.3,
                marker=dict(colors=['#55efc4', '#00b894', '#00cec9', '#81ecec', '#74b9ff']),
                showlegend=True,
                hovertemplate='%{label}<br>%{value:.2f}€<br>%{percent}<extra></extra>'
            ),
            row=2, col=2
        )
    
    # 5. Monthly Expenses by Category (Stacked)
    top_categories = expense_by_cat.head(8).index
    for i, category in enumerate(top_categories):
        cat_data = monthly_cat[monthly_cat['Category'] == category]
        fig.add_trace(
            go.Bar(
                x=cat_data['Month'],
                y=cat_data['Montant'],
                name=category,
                showlegend=False,
                hovertemplate=f'{category}<br>%{{y:.2f}}€<extra></extra>'
            ),
            row=3, col=1
        )
    
    # 6. Balance as Daily Histogram
    daily_balance = df.groupby('Date')['Balance'].last().reset_index()
    fig.add_trace(
        go.Bar(
            x=daily_balance['Date'],
            y=daily_balance['Balance'],
            name='Balance',
            marker_color='rgba(0,100,250,0.6)',
            marker_line_width=0,
            showlegend=False,
            hovertemplate='%{x}<br>Balance: %{y:.2f}€<extra></extra>'
        ),
        row=3, col=2
    )
    
    # Update axes
    fig.update_yaxes(title_text="Amount (€)", row=1, col=1, zeroline=True, zerolinecolor='black', zerolinewidth=2)
    fig.update_yaxes(title_text="Amount (€)", row=1, col=2, zeroline=True, zerolinecolor='black', zerolinewidth=1)
    fig.update_yaxes(title_text="Amount (€)", row=3, col=1)
    fig.update_yaxes(title_text="Balance (€)", row=3, col=2)
    
    # Update x-axes with better month visibility
    fig.update_xaxes(title_text="Month", row=1, col=1, tickangle=-45, dtick="M1")
    fig.update_xaxes(title_text="Month", row=1, col=2, tickangle=-45, dtick="M1")
    fig.update_xaxes(title_text="Month", row=3, col=1, tickangle=-45, dtick="M1")
    fig.update_xaxes(title_text="Date", row=3, col=2, tickformat="%b %Y", dtick="M1")
    
    # Layout
    fig.update_layout(
        title_text='Personal Finance Dashboard - Interactive',
        height=1400,
        showlegend=True,
        barmode='overlay',
        hovermode='closest',
        # Add date range slider on balance chart
        xaxis6=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    
    # Stack bars in monthly category chart
    fig.update_traces(marker_line_width=0, row=3, col=1)
    
    return fig


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_file = project_root / 'data' / '03_final' / 'transactions_categorized.csv'
    output_dir = project_root / 'data' / '03_final'
    
    print("📊 Loading data...")
    df = pd.read_csv(data_file, sep=';', decimal=',')
    df['Date'] = pd.to_datetime(df['Date'])
    
    print(f"✅ {len(df)} transactions loaded")
    print(f"📅 Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
    
    # Prepare data
    print("\n🔄 Preparing data...")
    monthly_summary, expense_by_cat, revenue_by_cat, monthly_cat = prepare_data(df)
    
    # Create dashboard
    print("🎨 Creating dashboard...")
    fig = create_dashboard(df, monthly_summary, expense_by_cat, revenue_by_cat, monthly_cat)
    
    # Save
    output_file = output_dir / 'finance_dashboard.html'
    fig.write_html(output_file)
    
    print(f"\n💾 Saved: {output_file}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Total Revenue: +{monthly_summary['Revenue'].sum():.2f}€")
    print(f"   Total Expenses: -{monthly_summary['Expense'].sum():.2f}€")
    print(f"   Net: {monthly_summary['Net'].sum():.2f}€")
    
    print(f"\n💳 Top Expense Categories:")
    for cat, amount in expense_by_cat.head(5).items():
        print(f"   {cat}: {amount:.2f}€")
    
    if len(revenue_by_cat) > 0:
        print(f"\n💰 Revenue Categories:")
        for cat, amount in revenue_by_cat.items():
            print(f"   {cat}: {amount:.2f}€")
    
    print("\n✨ Features:")
    print("   • Date range selector (1m, 3m, 6m, 1y, All)")
    print("   • Interactive date slider on balance chart")
    print("   • Waterfall income/expenses visualization")
    print("   • Category breakdown for expenses & revenue")
    
    print("\n🌐 Open finance_dashboard.html in your browser!")


if __name__ == "__main__":
    main()
