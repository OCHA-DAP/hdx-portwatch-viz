# hdx-portwatch-viz

Static dashboard showing port call activity for selected ports, comparing the current year against a historical baseline. Built for GitHub Pages.

## Data update workflow

Raw CSVs come from the [PortWatch dataset on HDX](https://data.humdata.org/organization/portwatch). Each country has its own file named:

```
{country-slug}-daily-port-activity-data-and-shipment-estimates.csv
```

**Steps to update:**

1. Download the latest CSVs from HDX into `data/raw/`
2. Run the data generation script:
   ```bash
   uv run python generate_data.py
   ```
3. Commit `data/ports.json` and push — GitHub Pages will serve the updated dashboard automatically

## Adding a new port

Edit the `PORT_CONFIG` dict at the top of `generate_data.py`:

```python
PORT_CONFIG = {
    'Beirut, Lebanon': ('lebanon', 'Beirut'),
    'My New Port, Country': ('country-slug', 'Port Name In CSV'),
}
```

Then re-run `generate_data.py` and commit `data/ports.json`.

## Local development

```bash
# Install dependencies
uv sync

# Generate data (requires CSVs in data/raw/)
uv run python generate_data.py

# Serve the dashboard locally
cd /path/to/hdx-portwatch-viz
python3 -m http.server 8000
# Open http://localhost:8000
```