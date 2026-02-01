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

.report-card.selected {
  background: #e8f0fe;
  box-shadow: inset 3px 0 0 #1a73e8;
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
  background: #e8f0fe;
  color: #1a73e8;
  border-radius: 4px;
  min-width: 24px;
  height: 20px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
  padding: 0 4px;
}

.id-badge {
  background: #f1f3f4;
  color: #5f6368;
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 10px;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
}

.address {
  font-weight: 500;
  font-size: 13px;
  color: #202124;
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
