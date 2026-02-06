GRAFFITI_RECENT_REQUEST_DAYS = 365
GEOCODE_CACHE_FILE = "public/geocode-cache.json"
GRAFFITI_LOOKUPS_FILE = "public/graffiti-lookups.json"

GRAFFITI_COMPLETE_STATUSES = [
    "CityOwnedIneligible",
    "Cleaning crew dispatched.  Property cleaned.",
    "Cleaning crew dispatched. No graffiti on property.",
    "The property owner\u2019s name cannot be determined.",
    "Graffiti is intentional.",
    "Graffiti on property is inaccessible to graffiti cleaning staff.",
]

REQUEST_USER_AGENT = "graffiti-lookup-nyc-web"
REQUEST_TIMEOUT = 10
REQUEST_MIN_DELAY_SECONDS = 1.5
REQUEST_MAX_RETRIES = 3
REQUEST_ERROR_WAIT_SECONDS = 5.0
