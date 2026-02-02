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
  items: { type: Array, default: () => [] }
});

const DEFAULT_CENTER = [40.7128, -74.0060]; // NYC
const DEFAULT_ZOOM = 12;
const MAX_ZOOM = 19;
const BOUNDS_PADDING = 0.1;
const PAGE_SIZE = 50;
const INIT_DELAY_MS = 100;

const ICON_CONFIG = {
  default: {
    radius: 8,
    fillColor: '#1a73e8',
    color: '#fff',
    weight: 1,
    opacity: 1,
    fillOpacity: 0.9
  },
  highlighted: {
    radius: 10,
    fillColor: '#7c4dff',
    color: '#fff',
    weight: 2,
    opacity: 1,
    fillOpacity: 1
  }
};

let map = null;
let leaflet = null;
let markerMap = {};
let currentFilteredItems = null; // Track filtered items when filtering is active

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

  window.dispatchEvent(
    new CustomEvent('marker-selected', { detail: item })
  );
}

function createPopupContent(item) {
  const indexBadge = item._index
    ? `<span style="background:#e8f0fe;color:#1a73e8;padding:2px 6px;border-radius:4px;font-size:11px;font-weight:600;min-width:24px;text-align:center;display:inline-block;">${item._index}</span>`
    : '';

  const idBadge = `<span style="background:#f1f3f4;color:#5f6368;border-radius:4px;padding:2px 6px;font-size:10px;font-weight:500;">#${item.service_request}</span>`;

  return `
    <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
      ${indexBadge}${idBadge}
    </div>
    <div style="font-weight:600;margin-bottom:4px;">${item.address}</div>
    <div style="color:#5f6368;font-size:12px;">${item.status}</div>
  `.trim();
}

function clearMarkers() {
  Object.values(markerMap).forEach((marker) => marker.remove());
  markerMap = {};
}

function addMarkers(items) {
  if (!map || !leaflet || !items) return;

  clearMarkers();

  items
    .filter((item) => item.latitude && item.longitude)
    .forEach((item) => {
      const isSelected = selectedItem.value?.service_request === item.service_request;
      markerMap[item.service_request] = createMarker(item, isSelected);
    });

  fitBoundsToMarkers();
}

function fitBoundsToMarkers() {
  const markers = Object.values(markerMap);
  if (markers.length === 0) return;

  const group = leaflet.featureGroup(markers);
  map.fitBounds(group.getBounds().pad(BOUNDS_PADDING));
}

function highlightMarker(item) {
  Object.entries(markerMap).forEach(([id, marker]) => {
    const isTarget = id === item.service_request;
    const config = isTarget ? ICON_CONFIG.highlighted : ICON_CONFIG.default;

    marker.setStyle(config);
    marker.setRadius(config.radius);

    if (isTarget) {
      marker.bringToFront();
      marker.openPopup();
      if (item.latitude && item.longitude) {
        map.panTo([item.latitude, item.longitude]);
      }
    }
  });
}

function clearHighlight() {
  Object.values(markerMap).forEach((marker) => {
    marker.setStyle(ICON_CONFIG.default);
    marker.setRadius(ICON_CONFIG.default.radius);
    marker.closePopup();
  });
}

function getWindowedItems(centerItems) {
  const sourceItems = currentFilteredItems || props.items;

  if (!sourceItems || centerItems.length === 0) {
    return [];
  }

  const firstVisibleId = centerItems[0]?.service_request;
  const firstIndex = sourceItems.findIndex(
    (item) => item.service_request === firstVisibleId
  );

  if (firstIndex === -1) {
    return centerItems.slice(0, PAGE_SIZE);
  }

  const halfPage = Math.floor(PAGE_SIZE / 2);
  const start = Math.max(0, firstIndex - halfPage);
  const end = Math.min(sourceItems.length, start + PAGE_SIZE);

  return sourceItems
    .slice(start, end)
    .map((item, i) => ({ ...item, _index: start + i + 1 }));
}

function calculateInitialCenter() {
  if (!props.items?.length) return DEFAULT_CENTER;

  const itemsWithCoords = props.items.filter(
    (item) => item.latitude && item.longitude
  );

  if (itemsWithCoords.length === 0) return DEFAULT_CENTER;

  const avgLat =
    itemsWithCoords.reduce((sum, item) => sum + item.latitude, 0) /
    itemsWithCoords.length;
  const avgLng =
    itemsWithCoords.reduce((sum, item) => sum + item.longitude, 0) /
    itemsWithCoords.length;

  return [avgLat, avgLng];
}

function initializeMap() {
  map = leaflet
    .map('map', {
      zoomControl: true,
      scrollWheelZoom: true,
      attributionControl: true
    })
    .setView(calculateInitialCenter(), DEFAULT_ZOOM);

  leaflet
    .tileLayer('https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
      maxZoom: MAX_ZOOM
    })
    .addTo(map);
}

function loadInitialMarkers() {
  if (!props.items?.length) return;

  const initialItems = props.items
    .slice(0, PAGE_SIZE)
    .map((item, i) => ({ ...item, _index: i + 1 }));

  addMarkers(initialItems);
}

function onVisibleItemsChanged(event) {
  visibleItems.value = event.detail;
  const windowed = getWindowedItems(visibleItems.value);
  addMarkers(windowed);
}

function onFilteredItemsChanged(event) {
  currentFilteredItems = event.detail;
  addMarkers(currentFilteredItems.slice(0, PAGE_SIZE));
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
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 12px;
  color: #5f6368;
  flex-shrink: 0;
}

.map-root {
  width: 100%;
  min-width: 0;
  flex: 1;
  min-height: 0;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  overflow: hidden;
  background: #fff;
  box-sizing: border-box;
}

:deep(.highlighted-marker) {
  transition: all 0.2s ease;
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
    border-radius: 8px;
  }

  .map-title {
    margin-bottom: 8px;
  }
}
</style>
