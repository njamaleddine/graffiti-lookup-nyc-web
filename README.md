# Graffiti Lookup NYC Web

An interactive web application to explore graffiti removal requests across New York City. Built with Astro and Vue, featuring a side-by-side list and map view.

## Features

- **Interactive Map** - View graffiti reports on a Leaflet map with CARTO Voyager basemaps
- **Search & Filter** - Search by ID or address, filter by status with dropdown
- **Click to Highlight** - Click markers or list items to sync selection between views
- **Live Map Updates** - Map markers update in real-time as you filter or scroll
- **Daily Updates** - Data refreshed automatically via GitHub Actions using [graffiti-lookup-nyc](https://pypi.org/project/graffiti-lookup-nyc/)
- **Geocoded Addresses** - Addresses automatically converted to map coordinates with caching
- **Mobile Responsive** - Optimized for mobile viewports with side-by-side filters

## Tech Stack

- [Astro](https://astro.build/) - Static site generator
- [Vue 3](https://vuejs.org/) - Interactive components with Composition API
- [Leaflet](https://leafletjs.com/) - Map library with [CARTO Voyager](https://carto.com/) tiles
- [geopy](https://geopy.readthedocs.io/) - Address geocoding via Nominatim
- [graffiti-lookup-nyc](https://pypi.org/project/graffiti-lookup-nyc/) - NYC 311 graffiti data CLI

## Local Development

### Prerequisites

- Node.js 20+ (see `.nvmrc`)
- Python 3.12+ (for geocoding script)

### Setup

```bash
# Install Node dependencies
npm install

# Start development server
npm run dev
```

The site will be available at `http://localhost:4321/graffiti-lookup-nyc-web/`

### Generating Data Locally

To generate graffiti data and geocode addresses locally:

```bash
# Install Python dependencies
pip install -r geocode/requirements.txt

# Generate graffiti data (replace with your IDs)
graffiti-lookup-nyc --ids "G258700,G258801,G258900" --file-path public/graffiti-lookups.json --file-type json

# Geocode addresses
python -m geocode
```

## Deployment

This project is configured for GitHub Pages deployment.

### Automatic Deployment

The GitHub Actions workflow (`.github/workflows/build-and-deploy.yml`) runs daily at 12am EST and:

1. Fetches latest graffiti data using the `graffiti-lookup-nyc` CLI
2. Geocodes new addresses
3. Builds the Astro site
4. Deploys to GitHub Pages

### Required Setup

1. **Enable GitHub Pages** in your repository settings:
   - Go to Settings → Pages
   - Set Source to "Deploy from a branch"
   - Select the `gh-pages` branch

2. **Add Repository Variable**:
   - Go to Settings → Secrets and variables → Actions → Variables
   - Add a variable named `GRAFFITI_IDS` with comma-separated graffiti lookup IDs (e.g., `G258700,G258801,G258900`)

### Manual Deployment

You can trigger a manual deployment from the Actions tab by running the "Build and Deploy" workflow.

## Project Structure

```
├── .github/
│   └── workflows/
│       ├── build-and-deploy.yml  # Daily data fetch & deploy
│       ├── codeql.yml            # Security analysis
│       ├── lint-js.yml           # ESLint for Vue/Astro
│       ├── lint-python.yml       # Black & flake8 for Python
│       └── test.yml              # Python tests with coverage
├── geocode/                      # Python geocoding package
│   ├── __init__.py
│   ├── __main__.py               # Entry point (python -m geocode)
│   ├── geocoder.py               # Geocoding logic with caching
│   ├── logger.py                 # Logging setup
│   ├── sanitize.py               # Address normalization
│   ├── requirements.txt          # Python dependencies
│   ├── requirements-dev.txt      # Dev dependencies (pytest)
│   └── tests/                    # Test suite
├── public/
│   ├── geocode-cache.json        # Cached geocoding results
│   └── graffiti-lookups.json     # Generated graffiti data
├── src/
│   ├── components/
│   │   ├── ListItem.vue          # Individual report card
│   │   ├── ListView.vue          # Scrollable list with search & filter
│   │   ├── MapView.vue           # Leaflet map with dynamic markers
│   │   ├── SearchBar.vue         # Reusable search input component
│   │   ├── StatusChip.vue        # Status badge with color coding
│   │   └── StatusFilter.vue      # Reusable status dropdown filter
│   ├── layouts/
│   │   └── Layout.astro          # Base HTML layout (100dvh viewport)
│   └── pages/
│       └── index.astro           # Main page with flex layout
├── astro.config.mjs              # Astro configuration
├── eslint.config.js              # ESLint configuration
├── setup.cfg                     # Python tool config (flake8, pytest)
└── package.json
```

## Architecture Diagram

Below is a high level architecture diagram showing the main data flow and core components:


```mermaid
flowchart TD

   %% Data Acquisition & Processing
   CLI["graffiti-lookup-nyc CLI"]
   FILTER["filter_service_requests.py\n(if GRAFFITI_FILTER_ACTIVE_SERVICE_REQUESTS=True)"]
   IDS["GRAFFITI_IDS (env var)"]
   GEOCODE["geocode/geocoder.py"]
   LOOKUPS["graffiti-lookups.json"]
   CACHE["geocode-cache.json"]
   DATA_CACHE["data-cache branch (Git)"]
   GH_ACTIONS["GitHub Actions"]
   PUBLIC["public/ (artifacts)"]
   ASTRO["Astro Build"]
   DIST["dist/ (static site)"]
   GH_PAGES["GitHub Pages"]
   USER["User (browser)"]

   %% Rigid, grid-like layout
   CLI --> FILTER
   FILTER --> LOOKUPS
   IDS -.-> LOOKUPS
   CLI -.-> LOOKUPS
   LOOKUPS --> GEOCODE
   GEOCODE --> CACHE
   GEOCODE -- update --> LOOKUPS
   LOOKUPS -.-> DATA_CACHE
   CACHE -.-> DATA_CACHE

   GH_ACTIONS --> CLI
   GH_ACTIONS --> GEOCODE
   GH_ACTIONS --> PUBLIC
   LOOKUPS -.-> ASTRO
   PUBLIC --> ASTRO
   ASTRO --> DIST
   DIST --> GH_PAGES
   GH_PAGES --> USER
   DIST -.-> USER

   %% Node styles
   style CLI fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#0d47a1
   style FILTER fill:#fffde7,stroke:#fbc02d,stroke-width:2px,color:#f57c00
   style IDS fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px,color:#4a148c
   style GEOCODE fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#1b5e20
   style LOOKUPS fill:#fff3e0,stroke:#ef6c00,stroke-width:2px,color:#e65100
   style CACHE fill:#ede7f6,stroke:#5e35b1,stroke-width:2px,color:#311b92
   style DATA_CACHE fill:#eceff1,stroke:#607d8b,stroke-width:2px,color:#263238
   style GH_ACTIONS fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#01579b
   style PUBLIC fill:#f9fbe7,stroke:#afb42b,stroke-width:2px,color:#827717
   style ASTRO fill:#fce4ec,stroke:#d81b60,stroke-width:2px,color:#880e4f
   style DIST fill:#f1f8e9,stroke:#689f38,stroke-width:2px,color:#33691e
   style GH_PAGES fill:#e0f2f1,stroke:#00897b,stroke-width:2px,color:#004d40
   style USER fill:#fffde7,stroke:#fbc02d,stroke-width:2px,color:#f57c00

   %% Edge styles
   linkStyle 0 stroke:#1976d2,stroke-width:2px
   linkStyle 1 stroke:#fbc02d,stroke-width:2px
   linkStyle 2 stroke:#8e24aa,stroke-width:2px,stroke-dasharray: 5 5
   linkStyle 3 stroke:#1976d2,stroke-width:2px,stroke-dasharray: 5 5
   linkStyle 4 stroke:#ef6c00,stroke-width:2px
   linkStyle 5 stroke:#388e3c,stroke-width:2px
   linkStyle 6 stroke:#388e3c,stroke-width:2px,stroke-dasharray: 2 2
   linkStyle 7 stroke:#607d8b,stroke-width:2px,stroke-dasharray: 2 2
   linkStyle 8 stroke:#5e35b1,stroke-width:2px,stroke-dasharray: 2 2
   linkStyle 9 stroke:#0288d1,stroke-width:2px
   linkStyle 10 stroke:#388e3c,stroke-width:2px
   linkStyle 11 stroke:#afb42b,stroke-width:2px
   linkStyle 12 stroke:#d81b60,stroke-width:2px,stroke-dasharray: 2 2
   linkStyle 13 stroke:#d81b60,stroke-width:2px
   linkStyle 14 stroke:#689f38,stroke-width:2px
   linkStyle 15 stroke:#00897b,stroke-width:2px
   linkStyle 16 stroke:#fbc02d,stroke-width:2px,stroke-dasharray: 2 2
```

**Legend:**
- **Data Acquisition & Processing (Python):** CLI and scripts for fetching, filtering, and geocoding graffiti data. If the environment variable `GRAFFITI_FILTER_ACTIVE_SERVICE_REQUESTS` is `True`, `filter_service_requests.py` filters the graffiti-lookups.json; otherwise, IDs are taken from the `GRAFFITI_IDS` env var.
- **Data Caching & Reuse:** All data artifacts are cached in a dedicated branch (`data-cache`) to store geocoding results and graffiti lookup data. `geocode-cache.json` is only used by the GitHub Action for geocoding, not by the Astro build.
- **Build & Deployment (CI/CD):** GitHub Actions orchestrates the pipeline, builds the static site, and deploys to GitHub Pages.
- **Frontend (Astro + Vue):** Static site served to users, with all data precomputed and embedded.


> **Note:**
> The `data-cache` branch is a persistent cache for both geocode results and graffiti lookup data. `geocode-cache.json` is only used by the GitHub Action to avoid redundant geocoding, and is not consumed by the Astro build. The same data is available for the Astro build and for filtering operations (e.g., in `filter_service_requests`).
>
> The workflow uses `filter_service_requests.py` to filter graffiti-lookups.json only if the environment variable `GRAFFITI_FILTER_ACTIVE_SERVICE_REQUESTS` is set to `True`. Otherwise, the IDs are taken from the `GRAFFITI_IDS` environment variable.

## License

MIT
