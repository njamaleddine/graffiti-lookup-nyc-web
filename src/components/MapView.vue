<template>
  <section class="map-section">
    <h2 class="map-title">Map View</h2>
    <div id="map" class="map-root"></div>
  </section>
</template>
<script setup>

import { onMounted, watch } from 'vue';

const props = defineProps({ items: Array });
let leafletMap;
let leafletMarkers = [];

function addMarkersToMap(leaflet) {
  if (!leafletMap) return;
  leafletMarkers.forEach(marker => marker.remove());
  leafletMarkers = [];
  props.items.forEach(item => {
    if (item.latitude && item.longitude) {
      const marker = leaflet.marker([item.latitude, item.longitude], {
        icon: leaflet.icon({
          iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
          iconSize: [25, 41],
          iconAnchor: [12, 41],
          popupAnchor: [1, -34],
        })
      }).addTo(leafletMap)
        .bindPopup(`<b>${item.address}</b><br>${item.status}`);
      leafletMarkers.push(marker);
    }
  });
}

onMounted(async () => {
  const leaflet = (await import('leaflet')).default;
  leafletMap = leaflet.map('map', {
    zoomControl: true,
    scrollWheelZoom: true,
    attributionControl: true,
  }).setView([40.7128, -74.0060], 11);
  leaflet.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19,
  }).addTo(leafletMap);
  addMarkersToMap(leaflet);
  window.addEventListener('resize', () => leafletMap.invalidateSize());

  watch(
    () => props.items,
    () => addMarkersToMap(leaflet),
    { deep: true }
  );
});
</script>
<style scoped>
.map-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  flex: 1;
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
  flex: 1;
  min-height: 500px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  overflow: hidden;
  background: #fff;
}
@media (max-width: 900px) {
  .map-root {
    min-height: 400px;
  }
}
</style>
