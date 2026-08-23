"""
Classify transactions into a generic, bank-terminology-based Type.
Rule-based on French bank statement vocabulary - no personal data involved,
unlike the per-merchant Category mapping (data/03_final/category_mapping.csv).
"""
import re
import pandas as pd
from pathlib import Path

# Ordered (pattern, label) rules - first match wins. Patterns are matched
# case-insensitively against the start of the transaction description.
TYPE_RULES = [
    (r'^ACHAT CB', 'Card Purchase'),
    (r'RETRAIT', 'ATM Withdrawal'),
    (r'^CREDIT CARTE BANCAIRE', 'Card Refund'),
    (r'^(COMMISSION|COTISATION|FRAIS DE|AVANTAGE TARIFAIRE|DROITS DE GARDE)', 'Bank Fee'),
    (r'^REMISE DE CHEQUE', 'Check Deposit'),
    (r'^CHEQUE N', 'Check Payment'),
    (r'^PAIEMENT COUPON', 'Investment Income'),
    (r'^PRELEVEMENT', 'Direct Debit'),
    (r'^VIREMENT INSTANTANE DE\b', 'Incoming Transfer'),
    (r'^VIREMENT INSTANTANE (A|DEBIT)', 'Outgoing Transfer'),
    (r'^VIREMENT DE', 'Incoming Transfer'),
    (r'^VIREMENT POUR', 'Outgoing Transfer'),
]


def classify_type(libelle: str, montant: float) -> str:
    """Classify a transaction using generic bank terminology, falling back
    to Debit/Credit based on amount sign if no rule matches."""
    for pattern, label in TYPE_RULES:
        if re.search(pattern, libelle, flags=re.IGNORECASE):
            return label
    return 'Other Credit' if montant > 0 else 'Other Debit'


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_file = project_root / 'data' / '03_final' / 'transactions_consolidated.csv'

    print("📊 Loading transactions...")
    df = pd.read_csv(data_file, sep=';', decimal=',')
    print(f"✅ {len(df)} transactions")

    print("\n🔄 Classifying transaction types...")
    df['Type'] = df.apply(lambda row: classify_type(row['Libellé'], row['Montant']), axis=1)

    df.to_csv(data_file, index=False, encoding='utf-8-sig', sep=';', decimal=',')
    print(f"💾 Saved: {data_file}")

    print("\n📊 Type breakdown:")
    for t, count in df['Type'].value_counts().items():
        print(f"   {t}: {count}")


if __name__ == "__main__":
    main()
