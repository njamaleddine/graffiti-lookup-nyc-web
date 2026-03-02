<template>
  <section class="map-section">
    <h2 class="map-title">
      Map View
    </h2>
    <div
      id="map"
      class="map-root"
    />
  </section>
</template>

<script setup>
  import { onMounted, onUnmounted, ref } from 'vue';

  const props = defineProps({
    items: { type: Array, default: () => [] },
  });

  const DEFAULT_CENTER = [40.7128, -74.006]; // NYC
  const DEFAULT_ZOOM = 12;
  const MAX_ZOOM = 19;
  const BOUNDS_PADDING = 0.1;
  const PAGE_SIZE = 50;
  const INIT_DELAY_MS = 100;
  const VISIBLE_ITEMS_DEBOUNCE_MS = 150;

  const ICON_CONFIG = {
    default: {
      radius: 7,
      fillColor: '#6366f1',
      color: 'rgba(255,255,255,0.9)',
      weight: 1.5,
      opacity: 1,
      fillOpacity: 0.85,
    },
    highlighted: {
      radius: 10,
      fillColor: '#4f46e5',
      color: '#fff',
      weight: 2,
      opacity: 1,
      fillOpacity: 1,
    },
  };

  let map = null;
  let leaflet = null;
  let markerMap = {};
  let currentFilteredItems = null; // Track filtered items when filtering is active
  let previousHighlightId = null;
  let visibleItemsTimer = null;

  const visibleItems = ref([]);
  const selectedItem = ref(null);

  function createMarker(item, isSelected = false) {
    const config = isSelected ? ICON_CONFIG.highlighted : ICON_CONFIG.default;

    const marker = leaflet
      .circleMarker([item.latitude, item.longitude], config)
      .addTo(map)
      .bindPopup(createPopupContent(item))
      .on('click', () => onMarkerClick(item));

    if (isSelected) {
      marker.openPopup();
    }

    return marker;
  }

  function onMarkerClick(item) {
    selectedItem.value = item;
    highlightMarker(item);

    window.dispatchEvent(new CustomEvent('marker-selected', { detail: item }));
  }

  function createPopupContent(item) {
    const indexBadge = item._index
      ? `<span style="background:linear-gradient(135deg,#6366f1,#818cf8);color:#fff;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:600;min-width:22px;text-align:center;display:inline-block;">${item._index}</span>`
      : '';

    const idBadge = `<span style="background:rgba(0,0,0,0.04);color:#64748b;border-radius:6px;padding:2px 8px;font-size:10px;font-weight:500;font-family:ui-monospace,monospace;">#${item.service_request}</span>`;

    // Ensure address includes 'NY, USA'
    let address = item.address || '';
    if (!address.match(/NY,?\s*USA$/i)) {
      // If address already ends with NY (with or without comma), append 'USA'
      if (address.match(/NY$/i)) {
        address += ', USA';
      } else {
        address += ', NY, USA';
      }
    }

    const googleMapsUrl = `https://www.google.com/maps/place/${encodeURIComponent(address)}`;

    return `
    <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
      ${indexBadge}
      ${idBadge}
      <a
        href="${googleMapsUrl}"
        target="_blank"
        rel="noopener"
        style="display:inline-flex;align-items:center;gap:3px;padding:2px 8px;background:rgba(99,102,241,0.08);color:#6366f1;border-radius:8px;font-size:10px;font-weight:500;text-decoration:none;transition:background 0.2s;"
      >
        <span>Maps</span> <span style="font-size:10px;">↗</span>
      </a>
    </div>
    <div style="font-weight:600;font-size:13px;margin-bottom:3px;color:#0f172a;">${item.address}</div>
    <div style="color:#64748b;font-size:11px;">${item.status}</div>
  `.trim();
  }

  function clearMarkers() {
    Object.values(markerMap).forEach((marker) => marker.remove());
    markerMap = {};
  }

  function updateMarkers(items, shouldFitBounds = false) {
    if (!map || !leaflet || !items) return;

    const validItems = items.filter((item) => item.latitude && item.longitude);
    const newIds = new Set(validItems.map((item) => item.service_request));

    // Remove markers no longer in the new set
    for (const id of Object.keys(markerMap)) {
      if (!newIds.has(id)) {
        markerMap[id].remove();
        delete markerMap[id];
      }
    }

    // Add only markers that don't already exist
    validItems.forEach((item) => {
      if (!markerMap[item.service_request]) {
        const isSelected = selectedItem.value?.service_request === item.service_request;
        markerMap[item.service_request] = createMarker(item, isSelected);
      }
    });

    if (shouldFitBounds) {
      fitBoundsToMarkers();
    }
  }

  function fitBoundsToMarkers() {
    const markers = Object.values(markerMap);
    if (markers.length === 0) return;

    const group = leaflet.featureGroup(markers);
    map.fitBounds(group.getBounds().pad(BOUNDS_PADDING));
  }

  function highlightMarker(item) {
    // Reset only the previously highlighted marker
    if (previousHighlightId && markerMap[previousHighlightId]) {
      const prevMarker = markerMap[previousHighlightId];
      prevMarker.setStyle(ICON_CONFIG.default);
      prevMarker.setRadius(ICON_CONFIG.default.radius);
      prevMarker.closePopup();
    }

    // Highlight only the target marker
    const marker = markerMap[item.service_request];
    if (marker) {
      marker.setStyle(ICON_CONFIG.highlighted);
      marker.setRadius(ICON_CONFIG.highlighted.radius);
      marker.bringToFront();
      marker.openPopup();
      if (item.latitude && item.longitude) {
        map.panTo([item.latitude, item.longitude]);
      }
    }

    previousHighlightId = item.service_request;
  }

  function clearHighlight() {
    if (previousHighlightId && markerMap[previousHighlightId]) {
      const marker = markerMap[previousHighlightId];
      marker.setStyle(ICON_CONFIG.default);
      marker.setRadius(ICON_CONFIG.default.radius);
      marker.closePopup();
    }
    previousHighlightId = null;
  }

  function getWindowedItems(centerItems) {
    const sourceItems = currentFilteredItems || props.items;

    if (!sourceItems || centerItems.length === 0) {
      return [];
    }

    const firstVisibleId = centerItems[0]?.service_request;
    const firstIndex = sourceItems.findIndex((item) => item.service_request === firstVisibleId);

    if (firstIndex === -1) {
      return centerItems.slice(0, PAGE_SIZE);
    }

    const halfPage = Math.floor(PAGE_SIZE / 2);
    const start = Math.max(0, firstIndex - halfPage);
    const end = Math.min(sourceItems.length, start + PAGE_SIZE);

    return sourceItems.slice(start, end).map((item, i) => ({ ...item, _index: start + i + 1 }));
  }

  function calculateInitialCenter() {
    if (!props.items?.length) return DEFAULT_CENTER;

    const itemsWithCoords = props.items.filter((item) => item.latitude && item.longitude);

    if (itemsWithCoords.length === 0) return DEFAULT_CENTER;

    const avgLat =
      itemsWithCoords.reduce((sum, item) => sum + item.latitude, 0) / itemsWithCoords.length;
    const avgLng =
      itemsWithCoords.reduce((sum, item) => sum + item.longitude, 0) / itemsWithCoords.length;

    return [avgLat, avgLng];
  }

  function initializeMap() {
    map = leaflet
      .map('map', {
        zoomControl: true,
        scrollWheelZoom: true,
        attributionControl: true,
      })
      .setView(calculateInitialCenter(), DEFAULT_ZOOM);

    leaflet
      .tileLayer('https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        maxZoom: MAX_ZOOM,
      })
      .addTo(map);
  }

  function loadInitialMarkers() {
    if (!props.items?.length) return;

    const initialItems = props.items
      .slice(0, PAGE_SIZE)
      .map((item, i) => ({ ...item, _index: i + 1 }));

    updateMarkers(initialItems, true);
  }

  function onVisibleItemsChanged(event) {
    if (visibleItemsTimer) clearTimeout(visibleItemsTimer);
    visibleItemsTimer = setTimeout(() => {
      visibleItems.value = event.detail;
      const windowed = getWindowedItems(visibleItems.value);
      updateMarkers(windowed);
    }, VISIBLE_ITEMS_DEBOUNCE_MS);
  }

  function onFilteredItemsChanged(event) {
    currentFilteredItems = event.detail;
    clearMarkers();
    updateMarkers(currentFilteredItems.slice(0, PAGE_SIZE), true);
  }

  function onItemSelected(event) {
    const item = event.detail;
    selectedItem.value = item;
    if (item) {
      highlightMarker(item);
    } else {
      clearHighlight();
    }
  }

  function onWindowResize() {
    map?.invalidateSize();
  }

  onMounted(async () => {
    leaflet = (await import('leaflet')).default;

    initializeMap();

    setTimeout(() => {
      map.invalidateSize();
      loadInitialMarkers();
    }, INIT_DELAY_MS);

    window.addEventListener('resize', onWindowResize);
    window.addEventListener('visible-items-changed', onVisibleItemsChanged);
    window.addEventListener('filtered-items-changed', onFilteredItemsChanged);
    window.addEventListener('item-selected', onItemSelected);
  });

  onUnmounted(() => {
    window.removeEventListener('resize', onWindowResize);
    window.removeEventListener('visible-items-changed', onVisibleItemsChanged);
    window.removeEventListener('filtered-items-changed', onFilteredItemsChanged);
    window.removeEventListener('item-selected', onItemSelected);
  });
</script>

<style scoped>
  .map-section {
    width: 100%;
    min-width: 0;
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 0;
  }

  .map-title {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 12px;
    color: var(--text-tertiary, #94a3b8);
    flex-shrink: 0;
  }

  .map-root {
    width: 100%;
    min-width: 0;
    flex: 1;
    min-height: 0;
    border-radius: var(--radius-lg, 16px);
    border: 1px solid var(--border, rgba(0, 0, 0, 0.06));
    overflow: hidden;
    background: var(--bg, #f8fafc);
    box-sizing: border-box;
    box-shadow:
      var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.04)),
      0 0 0 1px var(--border, rgba(0, 0, 0, 0.06));
    animation: fadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1);
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: scale(0.99);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }

  :deep(.leaflet-popup-content-wrapper) {
    border-radius: var(--radius-md, 12px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    border: 1px solid rgba(0, 0, 0, 0.04);
  }

  :deep(.leaflet-popup-content) {
    margin: 12px 14px;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  }

  :deep(.leaflet-popup-tip) {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }

  @media (max-width: 900px) {
    .map-section {
      width: 100%;
      height: 100%;
    }

    .map-root {
      width: 100%;
      flex: 1;
      min-height: 0;
      border-radius: var(--radius-md, 12px);
    }

    .map-title {
      margin-bottom: 8px;
    }
  }
</style>
