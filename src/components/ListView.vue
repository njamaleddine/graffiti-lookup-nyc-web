<template>
  <section class="list-container">
    <h2 class="list-title">Graffiti Reports</h2>
    <ul class="report-list">
      <li v-for="item in items" :key="item.service_request" class="report-card">
        <div class="card-content">
          <div class="card-header">
            <span class="address">{{ item.address }}</span>
            <span class="status-chip">{{ item.status }}</span>
          </div>
          <div class="card-meta">
            <span>Created: {{ item.created }}</span>
            <span>Updated: {{ item.last_updated }}</span>
          </div>
        </div>
      </li>
    </ul>
  </section>
</template>
<script setup>
defineProps({ items: Array });
</script>
<style scoped>
.list-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
  flex: 1;
}
.list-title {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 12px;
  color: #5f6368;
  flex-shrink: 0;
}
.report-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
  background: #e0e0e0;
  border-radius: 8px;
  overflow-y: auto;
  overflow-x: hidden;
  flex: 1;
  min-height: 0;
}
.report-card {
  background: #fff;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  transition: background-color 0.15s ease;
  cursor: pointer;
}
.report-card:first-child {
  border-radius: 8px 8px 0 0;
}
.report-card:last-child {
  border-radius: 0 0 8px 8px;
}
.report-card:hover {
  background: #e8f0fe;
}
.card-header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 6px;
  gap: 6px;
}
.address {
  font-weight: 500;
  font-size: 13px;
  color: #202124;
  line-height: 1.4;
}
.status-chip {
  background: #e8f0fe;
  color: #1a73e8;
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 10px;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
}
.card-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #5f6368;
  flex-wrap: wrap;
}
@media (max-width: 900px) {
  .list-container {
    max-height: 300px;
  }
  .report-card {
    padding: 10px 12px;
  }
}
</style>
