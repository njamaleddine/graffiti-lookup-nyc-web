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

const MARKER_ICON_URL = 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png';

const ICON_CONFIG = {
  default: {
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34]
  },
  highlighted: {
    iconSize: [35, 57],
    iconAnchor: [17, 57],
    popupAnchor: [1, -48],
    className: 'highlighted-marker'
  }
};

let map = null;
let leaflet = null;
let defaultIcon = null;
let highlightIcon = null;
let markerMap = {};

const visibleItems = ref([]);
const selectedItem = ref(null);

function createIcons() {
  if (!leaflet) return;

  defaultIcon = leaflet.icon({
    iconUrl: MARKER_ICON_URL,
    ...ICON_CONFIG.default
  });

  highlightIcon = leaflet.icon({
    iconUrl: MARKER_ICON_URL,
    ...ICON_CONFIG.highlighted
  });
}

function createPopupContent(item) {
  const indexBadge = item._index
    ? `<span style="background:#e8f0fe;color:#1a73e8;padding:2px 6px;border-radius:4px;font-size:11px;font-weight:600;">${item._index}</span> `
    : '';

  return `
    ${indexBadge}<b>${item.address}</b><br>
    <span style="color:#5f6368;font-size:11px;">#${item.service_request}</span><br>
    ${item.status}
  `.trim();
}

function clearMarkers() {
  Object.values(markerMap).forEach((marker) => marker.remove());
  markerMap = {};
}

function createMarker(item) {
  const isSelected = selectedItem.value?.service_request === item.service_request;

  const marker = leaflet
    .marker([item.latitude, item.longitude], {
      icon: isSelected ? highlightIcon : defaultIcon,
      zIndexOffset: isSelected ? 1000 : 0
    })
    .addTo(map)
    .bindPopup(createPopupContent(item));

  if (isSelected) {
    marker.openPopup();
  }

  return marker;
}

function addMarkers(items) {
  if (!map || !leaflet || !items) return;

  clearMarkers();

  items
    .filter((item) => item.latitude && item.longitude)
    .forEach((item) => {
      markerMap[item.service_request] = createMarker(item);
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

    marker.setIcon(isTarget ? highlightIcon : defaultIcon);
    marker.setZIndexOffset(isTarget ? 1000 : 0);

    if (isTarget) {
      marker.openPopup();
      if (item.latitude && item.longitude) {
        map.panTo([item.latitude, item.longitude]);
      }
    }
  });
}

function getWindowedItems(centerItems) {
  if (!props.items || centerItems.length === 0) {
    return [];
  }

  const firstVisibleId = centerItems[0]?.service_request;
  const firstIndex = props.items.findIndex(
    (item) => item.service_request === firstVisibleId
  );

  if (firstIndex === -1) {
    return centerItems.slice(0, PAGE_SIZE);
  }

  const halfPage = Math.floor(PAGE_SIZE / 2);
  const start = Math.max(0, firstIndex - halfPage);
  const end = Math.min(props.items.length, start + PAGE_SIZE);

  return props.items
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
    .tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
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

function onItemSelected(event) {
  const item = event.detail;
  selectedItem.value = item;
  highlightMarker(item);
}

function onWindowResize() {
  map?.invalidateSize();
}

onMounted(async () => {
  leaflet = (await import('leaflet')).default;

  createIcons();
  initializeMap();

  setTimeout(() => {
    map.invalidateSize();
    loadInitialMarkers();
  }, INIT_DELAY_MS);

  window.addEventListener('resize', onWindowResize);
  window.addEventListener('visible-items-changed', onVisibleItemsChanged);
  window.addEventListener('item-selected', onItemSelected);
});

onUnmounted(() => {
  window.removeEventListener('resize', onWindowResize);
  window.removeEventListener('visible-items-changed', onVisibleItemsChanged);
  window.removeEventListener('item-selected', onItemSelected);
});
</script>

<style scoped>
.map-section {
  width: 100%;
  min-width: 0;
  display: flex;
  flex-direction: column;
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
  height: calc(100vh - 180px);
  max-height: 600px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  overflow: hidden;
  background: #fff;
  box-sizing: border-box;
}

:deep(.highlighted-marker) {
  filter: hue-rotate(120deg) saturate(1.5) brightness(1.1);
  transition: all 0.2s ease;
}

@media (max-width: 900px) {
  .map-section {
    width: 100%;
  }

  .map-root {
    width: 100%;
    height: 350px;
    max-height: none;
    border-radius: 8px;
  }
}
</style>
