"""Generate blinded perturbed-series diagnostics for LLM memory-leakage inspection.

The output preserves local OHLCV-style structure while reducing cues that a
pretrained LLM could associate with famous crisis windows. It does not create a
new performance leaderboard; it supports robustness/audit checks.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import random

INPUT_DIR = Path('dataset')
OUTPUT_DIR = Path('dataset_blinded')
BLOCK_SIZE = 10
NOISE_LEVEL = 0.001
RANDOM_SEED = 42

WINDOW_CODES = {
    '2008_2009': 'W1',
    '2020_2021': 'W2',
    '2022_2023': 'W3',
    '2004_2023': 'FULL',
}
ASSET_CODES = {
    'AAPL': 'SYNTH_A',
    'GOLD': 'SYNTH_B',
    'gold': 'SYNTH_B',
}

def clean_numeric(v):
    if pd.isna(v):
        return np.nan
    if isinstance(v, str):
        v = v.replace(',', '').replace('"', '').replace('%', '')
    try:
        return float(v)
    except Exception:
        return np.nan

def detect_codes(path: Path):
    name = path.stem
    asset = next((code for key, code in ASSET_CODES.items() if key in name), 'SYNTH_X')
    window = next((code for key, code in WINDOW_CODES.items() if key in name), 'W0')
    return asset, window

def process_file(path: Path):
    df = pd.read_csv(path)
    date_col = next((c for c in df.columns if c.lower() == 'date'), None)
    price_cols = [c for c in df.columns if c.lower() in ['price','open','high','low','close']]
    for c in price_cols:
        df[c] = df[c].map(clean_numeric)

    chunks = [df.iloc[i:i+BLOCK_SIZE].copy() for i in range(0, len(df), BLOCK_SIZE)]
    random.shuffle(chunks)
    out = pd.concat(chunks, ignore_index=True)

    for c in price_cols:
        out[c] = out[c] * (1 + np.random.normal(0, NOISE_LEVEL, len(out)))
    if 'High' in out.columns and 'Low' in out.columns and price_cols:
        out['High'] = out[price_cols].max(axis=1)
        out['Low'] = out[price_cols].min(axis=1)

    if date_col:
        start = pd.Timestamp('2000-01-03')
        out[date_col] = pd.bdate_range(start, periods=len(out)).strftime('%Y-%m-%d')
    price_col = next((c for c in out.columns if c.lower() in ['price','close']), None)
    change_col = next((c for c in out.columns if c.lower() == 'change %'), None)
    if price_col and change_col:
        out[change_col] = out[price_col].pct_change().fillna(0).map(lambda x: f'{x:.2%}')

    asset, window = detect_codes(path)
    outname = f'{asset}_{window}_BLINDED.csv'
    OUTPUT_DIR.mkdir(exist_ok=True)
    out.to_csv(OUTPUT_DIR / outname, index=False)
    return outname, len(out)

def main():
    np.random.seed(RANDOM_SEED)
    random.seed(RANDOM_SEED)
    rows = []
    for path in sorted(INPUT_DIR.glob('*.csv')):
        outname, n = process_file(path)
        rows.append({'source_file': path.name, 'blinded_file': outname, 'rows': n})
    pd.DataFrame(rows).to_csv(OUTPUT_DIR / 'BLINDED_DIAGNOSTIC_MANIFEST.csv', index=False)
    print(f'Generated {len(rows)} blinded diagnostic files in {OUTPUT_DIR}')

if __name__ == '__main__':
    main()
