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
let leafletMap;
let markerMap = {}; // service_request -> marker
let leafletInstance = null;
let defaultIcon = null;
let highlightIcon = null;
const visibleItems = ref([]);
const selectedItem = ref(null);

function createIcons() {
  if (!leafletInstance) return;
  defaultIcon = leafletInstance.icon({
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
  });
  highlightIcon = leafletInstance.icon({
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    iconSize: [35, 57],
    iconAnchor: [17, 57],
    popupAnchor: [1, -48],
    className: 'highlighted-marker'
  });
}

function addMarkersToMap(items) {
  if (!leafletMap || !leafletInstance || !items) return;
  
  // Remove old markers
  Object.values(markerMap).forEach(marker => marker.remove());
  markerMap = {};
  
  items.forEach(item => {
    if (item.latitude && item.longitude) {
      const isSelected = selectedItem.value?.service_request === item.service_request;
      const indexLabel = item._index ? `<span style="background:#e8f0fe;color:#1a73e8;padding:2px 6px;border-radius:4px;font-size:11px;font-weight:600;">${item._index}</span> ` : '';
      const marker = leafletInstance.marker([item.latitude, item.longitude], {
        icon: isSelected ? highlightIcon : defaultIcon,
        zIndexOffset: isSelected ? 1000 : 0
      }).addTo(leafletMap)
        .bindPopup(`${indexLabel}<b>${item.address}</b><br><span style="color:#5f6368;font-size:11px;">#${item.service_request}</span><br>${item.status}`);
      
      markerMap[item.service_request] = marker;
      
      if (isSelected) {
        marker.openPopup();
      }
    }
  });
  
  // Fit map bounds to show all markers
  const allMarkers = Object.values(markerMap);
  if (allMarkers.length > 0) {
    const group = leafletInstance.featureGroup(allMarkers);
    leafletMap.fitBounds(group.getBounds().pad(0.1));
  }
}

function handleItemSelected(event) {
  const item = event.detail;
  selectedItem.value = item;
  
  // Update marker icons
  Object.entries(markerMap).forEach(([id, marker]) => {
    if (id === item.service_request) {
      marker.setIcon(highlightIcon);
      marker.setZIndexOffset(1000);
      marker.openPopup();
      // Pan to selected marker
      if (item.latitude && item.longitude) {
        leafletMap.panTo([item.latitude, item.longitude]);
      }
    } else {
      marker.setIcon(defaultIcon);
      marker.setZIndexOffset(0);
    }
  });
}


// Helper to get windowed items for marker display
function getWindowedItems(centerItems) {
  if (!props.items || centerItems.length === 0) return [];
  const PAGE_SIZE = 50;
  // Find the index of the first visible item in the full list
  const firstIdx = props.items.findIndex(item => item.service_request === centerItems[0]?.service_request);
  if (firstIdx === -1) return centerItems.slice(0, PAGE_SIZE);
  const start = Math.max(0, firstIdx - Math.floor(PAGE_SIZE / 2));
  const end = Math.min(props.items.length, start + PAGE_SIZE);
  // Include original index for each item
  return props.items.slice(start, end).map((item, i) => ({ ...item, _index: start + i + 1 }));
}

function handleVisibleItemsChanged(event) {
  visibleItems.value = event.detail;
  const windowed = getWindowedItems(visibleItems.value);
  addMarkersToMap(windowed);
}

onMounted(async () => {
  const leaflet = (await import('leaflet')).default;
  leafletInstance = leaflet;
  createIcons();
  
  // Calculate center from items with coordinates, fallback to NYC
  let initialCenter = [40.7128, -74.0060];
  if (props.items && props.items.length > 0) {
    const itemsWithCoords = props.items.filter(item => item.latitude && item.longitude);
    if (itemsWithCoords.length > 0) {
      const avgLat = itemsWithCoords.reduce((sum, item) => sum + item.latitude, 0) / itemsWithCoords.length;
      const avgLng = itemsWithCoords.reduce((sum, item) => sum + item.longitude, 0) / itemsWithCoords.length;
      initialCenter = [avgLat, avgLng];
    }
  }
  
  leafletMap = leaflet.map('map', {
    zoomControl: true,
    scrollWheelZoom: true,
    attributionControl: true,
  }).setView(initialCenter, 12);
  leaflet.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
  }).addTo(leafletMap);
  
  // Wait for map container to be properly sized before adding markers
  setTimeout(() => {
    leafletMap.invalidateSize();
    // Always add first 50 markers with their index
    if (props.items && props.items.length > 0) {
      const initialItems = props.items.slice(0, 50).map((item, i) => ({ ...item, _index: i + 1 }));
      addMarkersToMap(initialItems);
    }
  }, 100);
  
  window.addEventListener('resize', () => leafletMap.invalidateSize());
  window.addEventListener('visible-items-changed', handleVisibleItemsChanged);
  window.addEventListener('item-selected', handleItemSelected);
});

onUnmounted(() => {
  window.removeEventListener('visible-items-changed', handleVisibleItemsChanged);
  window.removeEventListener('item-selected', handleItemSelected);
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
