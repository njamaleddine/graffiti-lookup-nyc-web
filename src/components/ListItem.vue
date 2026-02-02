<template>
  <li
    class="report-card"
    :class="{ selected: isSelected }"
  >
    <div
      class="card-content"
      @click="$emit('select', item)"
    >
      <header class="card-header">
        <span class="index-badge">{{ index }}</span>
        <span class="id-badge">#{{ item.service_request }}</span>
        <span class="address">{{ item.address }}</span>
      </header>

      <div class="card-status">
        <StatusChip :status="item.status" />
      </div>

      <footer class="card-meta">
        <time>Created: {{ item.created }}</time>
        <time>Updated: {{ item.last_updated }}</time>
      </footer>
    </div>
  </li>
</template>

<script setup>
import StatusChip from './StatusChip.vue';

defineProps({
  item: {
    type: Object,
    required: true,
    validator: (value) => 'service_request' in value && 'address' in value
  },
  index: {
    type: Number,
    required: true
  },
  isSelected: {
    type: Boolean,
    default: false
  }
});

defineEmits(['select']);
</script>

<style scoped>
.report-card {
  background: #fff;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  transition: all 0.2s ease;
  cursor: pointer;
  animation: slideIn 0.3s ease-out;
  animation-fill-mode: backwards;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-8px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.report-card:first-child {
  border-radius: 10px 10px 0 0;
}

.report-card:last-child {
  border-radius: 0 0 10px 10px;
}

.report-card:hover {
  background: linear-gradient(135deg, #f0f7ff 0%, #e8f4fd 100%);
}

.report-card.selected {
  background: linear-gradient(135deg, #ede9fe 0%, #e0e7ff 100%);
  box-shadow: inset 3px 0 0 #7c4dff;
}

.card-content {
  display: contents;
}

.card-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 6px;
  gap: 8px;
}

.index-badge {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1d4ed8;
  border-radius: 6px;
  min-width: 26px;
  height: 22px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
  padding: 0 6px;
  transition: transform 0.15s ease;
}

.report-card:hover .index-badge {
  transform: scale(1.05);
}

.id-badge {
  background: #f3f4f6;
  color: #6b7280;
  border-radius: 5px;
  padding: 3px 7px;
  font-size: 10px;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
  font-family: ui-monospace, monospace;
}

.address {
  font-weight: 500;
  font-size: 13px;
  color: #1f2937;
  line-height: 1.4;
  flex: 1;
}

.card-status {
  margin-bottom: 6px;
}

.card-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #5f6368;
  flex-wrap: wrap;
}

@media (max-width: 900px) {
  .report-card {
    padding: 10px 12px;
  }
}
</style>
