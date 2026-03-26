import requests
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / 'data' / 'raw'
HDX_API  = 'https://data.humdata.org/api/3/action'

RESOURCES = {
    'djibouti-daily-port-activity-data-and-shipment-estimates.csv':     '96a7bdea-8297-49b7-ad6c-adb1d1f48e6d',
    'kenya-daily-port-activity-data-and-shipment-estimates.csv':        'e0bde7c9-2cb7-4eab-ae71-3e2c2e225207',
    'lebanon-daily-port-activity-data-and-shipment-estimates.csv':      '8d1d8984-fd6d-4f8e-af84-32b0ab8bacd3',
    'oman-daily-port-activity-data-and-shipment-estimates.csv':         '381b41b9-12c8-4bb3-b056-65ef6ddf1c6b',
    'somalia-daily-port-activity-data-and-shipment-estimates.csv':      '8bf8a420-56b3-492a-96b0-e8acb7f14c04',
    'sudan-daily-port-activity-data-and-shipment-estimates.csv':        '6ce7a041-ce33-4e83-bc66-7fd1d1fa4af8',
    'yemen-daily-port-activity-data-and-shipment-estimates.csv':        '5b130c44-8c57-485c-b1bf-6ab07aa12ce9',
    'daily-chokepoint-transit-calls-and-shipment-volume-estimates.csv': 'cbd17f06-8ab2-4ba4-a666-f7a4bcc9ea3f',
}


def get_download_url(resource_id: str) -> str:
    resp = requests.get(f'{HDX_API}/resource_show', params={'id': resource_id}, timeout=30)
    resp.raise_for_status()
    return resp.json()['result']['url']


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for filename, resource_id in RESOURCES.items():
        print(f'Downloading {filename}...')
        url = get_download_url(resource_id)
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        (DATA_DIR / filename).write_bytes(resp.content)
        print(f'  {len(resp.content) / 1024:.0f} KB')

    print('\nAll files downloaded.')


if __name__ == '__main__':
    main()
