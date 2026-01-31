<template>
  <section class="list-container">
    <h2 class="list-title">Graffiti Reports <span class="count">({{ visibleItems.length }} of {{ items?.length || 0 }})</span></h2>
    <ul class="report-list" ref="listRef" @scroll="handleScroll">
      <li 
        v-for="item in visibleItems" 
        :key="item.service_request" 
        :ref="el => setItemRef(item.service_request, el)"
        class="report-card"
      >
        <div class="card-content" @click="selectItem(item)">
          <div class="card-header">
            <span class="address">{{ item.address }}</span>
            <span class="status-chip" :class="getStatusClass(item.status)">{{ item.status || 'Unknown' }}</span>
          </div>
          <div class="card-meta">
            <span>Created: {{ item.created }}</span>
            <span>Updated: {{ item.last_updated }}</span>
          </div>
        </div>
      </li>
      <li v-if="hasMore" class="loading-indicator">
        Loading more...
      </li>
    </ul>
  </section>
</template>
<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';

const props = defineProps({ items: Array });

const PAGE_SIZE = 50;
const displayCount = ref(PAGE_SIZE);
const listRef = ref(null);
const isMounted = ref(false);
const itemRefs = ref({});
const viewportItems = ref([]);

const visibleItems = computed(() => {
  if (!props.items) return [];
  return props.items.slice(0, displayCount.value);
});

const hasMore = computed(() => {
  if (!props.items) return false;
  return displayCount.value < props.items.length;
});

function setItemRef(id, el) {
  if (el) {
    itemRefs.value[id] = el;
  }
}

function getStatusClass(status) {
  if (!status) return 'status-default';
  const s = status.toLowerCase();
  // Check more specific patterns first
  if (s.includes('to be cleaned')) return 'status-scheduled';
  if (s.includes('dispatched') && s.includes('no graffiti')) return 'status-no-graffiti';
  if (s.includes('property cleaned') || (s.includes('cleaned') && !s.includes('to be'))) return 'status-cleaned';
  if (s.includes('waiver') || s.includes('no response')) return 'status-pending';
  if (s.includes('notice') || s.includes('sent')) return 'status-notice';
  if (s.includes('notified') || s.includes('90 days')) return 'status-notified';
  if (s.includes('inaccessible')) return 'status-inaccessible';
  if (s.includes('intentional')) return 'status-intentional';
  if (s.includes('ineligible') || s.includes('cannot be determined')) return 'status-ineligible';
  return 'status-default';
}

function selectItem(item) {
  if (!isMounted.value || typeof window === 'undefined') return;
  window.dispatchEvent(new CustomEvent('item-selected', {
    detail: item
  }));
}

function calculateViewportItems() {
  if (!listRef.value || !isMounted.value) return;
  
  const list = listRef.value;
  const listRect = list.getBoundingClientRect();
  const inViewport = [];
  
  visibleItems.value.forEach(item => {
    const el = itemRefs.value[item.service_request];
    if (el) {
      const rect = el.getBoundingClientRect();
      // Check if element is within the list's visible area
      if (rect.bottom > listRect.top && rect.top < listRect.bottom) {
        inViewport.push(item);
      }
    }
  });
  
  viewportItems.value = inViewport;
  emitViewportItems();
}

function emitViewportItems() {
  if (!isMounted.value || typeof window === 'undefined') return;
  window.dispatchEvent(new CustomEvent('visible-items-changed', {
    detail: viewportItems.value
  }));
}

function handleScroll() {
  const list = listRef.value;
  if (!list) return;
  
  // Load more when scrolled near bottom (within 100px)
  if (hasMore.value) {
    const scrollBottom = list.scrollHeight - list.scrollTop - list.clientHeight;
    if (scrollBottom < 100) {
      displayCount.value = Math.min(displayCount.value + PAGE_SIZE, props.items.length);
    }
  }
  
  // Update viewport items
  calculateViewportItems();
}

// Reset when items change
watch(() => props.items, () => {
  displayCount.value = PAGE_SIZE;
  itemRefs.value = {};
});

// Recalculate viewport items when visible items change
watch(visibleItems, () => {
  setTimeout(calculateViewportItems, 50);
});

onMounted(() => {
  isMounted.value = true;
  setTimeout(calculateViewportItems, 100);
});
</script>
<style scoped>
.list-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 180px);
  max-height: 600px;
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
.list-title .count {
  font-weight: 400;
  color: #9aa0a6;
  text-transform: none;
  letter-spacing: normal;
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
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 10px;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
}

/* Status color variations */
.status-cleaned {
  background: #e6f4ea;
  color: #137333;
}
.status-no-graffiti {
  background: #e6f4ea;
  color: #0d652d;
}
.status-pending {
  background: #fef7e0;
  color: #b45309;
}
.status-notice {
  background: #fff3cd;
  color: #856404;
}
.status-notified {
  background: #e0f2fe;
  color: #0369a1;
}
.status-inaccessible {
  background: #fce4ec;
  color: #c62828;
}
.status-intentional {
  background: #f3e5f5;
  color: #7b1fa2;
}
.status-ineligible {
  background: #eceff1;
  color: #546e7a;
}
.status-scheduled {
  background: #e1f5fe;
  color: #0277bd;
}
.status-default {
  background: #e8f0fe;
  color: #1a73e8;
}
.card-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #5f6368;
  flex-wrap: wrap;
}
.loading-indicator {
  background: #f8f9fa;
  padding: 16px;
  text-align: center;
  font-size: 12px;
  color: #5f6368;
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
