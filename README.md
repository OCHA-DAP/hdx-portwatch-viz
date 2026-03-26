# hdx-portwatch-viz

Static dashboard showing port call activity for selected ports, comparing the current year against a historical baseline. Built for GitHub Pages.

## Data update workflow

Raw CSVs come from the [PortWatch dataset on HDX](https://data.humdata.org/organization/portwatch). Each country has its own file named:

```
{country-slug}-daily-port-activity-data-and-shipment-estimates.csv
```

Data is updated automatically every Tuesday at 18:00 UTC via GitHub Actions, which downloads the latest CSVs, regenerates `data/ports.json`, and commits the result. You can also trigger a run manually from the Actions tab in the repo.

To update manually on your machine:

1. Download the latest CSVs from HDX:
   ```bash
   uv run python download_data.py
   ```
2. Regenerate the data file:
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

Then add the corresponding HDX resource ID to the `RESOURCES` dict in `download_data.py`, re-run both scripts, and commit `data/ports.json`.

## Local development

```bash
# Install dependencies
uv sync

# Download raw data and generate data/ports.json
uv run python download_data.py
uv run python generate_data.py

# Serve the dashboard locally
cd /path/to/hdx-portwatch-viz
python3 -m http.server 8000
# Open http://localhost:8000
```
