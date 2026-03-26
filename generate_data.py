import json
import pandas as pd
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / 'data' / 'raw'
OUT_FILE = Path(__file__).parent / 'data' / 'ports.json'

PORT_CONFIG = {
    'Beirut, Lebanon':    ('lebanon',  'Beirut'),
    'Mombasa, Kenya':     ('kenya',    'Mombasa'),
    'Lamu, Kenya':        ('kenya',    'Lamu'),
    'Beira, Mozambique':     ('mozambique', 'Beira'),
    'Salalah, Oman':      ('oman',     'Salalah'),
    'Djibouti, Djibouti': ('djibouti', 'Djibouti'),
    'Port Sudan, Sudan':  ('sudan',    'Port Sudan'),
    'Mogadishu, Somalia': ('somalia',  'Mogadishu'),
    'Yemen (all ports)':  ('yemen',    None),
}

STRAIT_CONFIG = {
    'Strait of Hormuz': 'Strait of Hormuz',
}

CHOKEPOINT_FILE = 'daily-chokepoint-transit-calls-and-shipment-volume-estimates.csv'


def compute_seasonal(df: pd.DataFrame, value_col: str) -> dict:
    df = df.copy()
    df['doy']  = df['date'].dt.dayofyear
    df['year'] = df['date'].dt.year
    current_year = int(df['year'].max())

    df['roll7'] = (
        df.groupby('year')[value_col]
        .transform(lambda x: x.rolling(7, center=False, min_periods=3).mean())
    )

    hist = (
        df[df['year'] != current_year]
        .groupby('doy')['roll7']
        .agg(hist_avg='mean', hist_sd='std')
        .reset_index()
    )
    hist['hist_sd'] = hist['hist_sd'].fillna(0)
    hist['upper'] = (hist['hist_avg'] + hist['hist_sd']).round(2)
    hist['lower'] = (hist['hist_avg'] - hist['hist_sd']).clip(lower=0).round(2)
    hist['hist_avg'] = hist['hist_avg'].round(2)

    curr = df[df['year'] == current_year][['doy', 'roll7']].dropna()
    curr['roll7'] = curr['roll7'].round(2)

    hist_years_min = int(df[df['year'] != current_year]['year'].min())

    return {
        'current_year': current_year,
        'hist_label': f'{hist_years_min}–{current_year - 1}',
        'latest_date': df['date'].max().strftime('%d %b %Y'),
        'hist': hist[['doy', 'hist_avg', 'upper', 'lower']].to_dict(orient='records'),
        'current': curr[['doy', 'roll7']].to_dict(orient='records'),
    }


def main():
    output = {
        'ports': list(PORT_CONFIG.keys()),
        'port_data': {},
        'straits': list(STRAIT_CONFIG.keys()),
        'strait_data': {},
    }

    # Port calls
    for display_name, (country_slug, portname) in PORT_CONFIG.items():
        print(f'Processing {display_name}...')
        path = DATA_DIR / f'{country_slug}-daily-port-activity-data-and-shipment-estimates.csv'
        df = pd.read_csv(path)
        df['date'] = pd.to_datetime(df['date'], utc=True).dt.tz_localize(None)
        if portname is not None:
            df = df[df['portname'] == portname]
        df = df.groupby('date')['portcalls'].sum().reset_index()
        output['port_data'][display_name] = compute_seasonal(df, 'portcalls')
        print(f'  Latest: {output["port_data"][display_name]["latest_date"]}')

    # Strait transit calls
    chokepoints = pd.read_csv(DATA_DIR / CHOKEPOINT_FILE)
    chokepoints['date'] = pd.to_datetime(chokepoints['date'], utc=True).dt.tz_localize(None)

    for display_name, strait_name in STRAIT_CONFIG.items():
        print(f'Processing {display_name}...')
        df = chokepoints[chokepoints['portname'] == strait_name][['date', 'n_total']].copy()
        output['strait_data'][display_name] = compute_seasonal(df, 'n_total')
        print(f'  Latest: {output["strait_data"][display_name]["latest_date"]}')

    def clean(obj):
        if isinstance(obj, list): return [clean(v) for v in obj]
        if isinstance(obj, dict): return {k: clean(v) for k, v in obj.items()}
        if isinstance(obj, float) and obj != obj: return None  # NaN → null
        return obj

    OUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUT_FILE, 'w') as f:
        json.dump(clean(output), f, indent=2)

    print(f'\nWrote {OUT_FILE}')


if __name__ == '__main__':
    main()
