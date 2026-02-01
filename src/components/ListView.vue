<template>
  <section class="list-container">
    <header class="list-header">
      <h2 class="list-title">
        Graffiti Reports
        <span class="count">({{ visibleItems.length }} of {{ totalCount }})</span>
      </h2>
    </header>

    <ul
      ref="listRef"
      class="report-list"
      @scroll="onScroll"
    >
      <ListItem
        v-for="(item, index) in visibleItems"
        :key="item.service_request"
        :ref="(el) => registerItemRef(item.service_request, el)"
        :item="item"
        :index="index + 1"
        :is-selected="selectedItem?.service_request === item.service_request"
        @select="onItemSelect"
      />

      <li
        v-if="hasMore"
        class="loading-indicator"
      >
        Loading more...
      </li>
    </ul>
  </section>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import ListItem from './ListItem.vue';

const props = defineProps({
  items: { type: Array, default: () => [] }
});

const PAGE_SIZE = 50;
const SCROLL_THRESHOLD = 100;
const VIEWPORT_DEBOUNCE_MS = 50;
const INITIAL_DELAY_MS = 100;

const listRef = ref(null);
const displayCount = ref(PAGE_SIZE);
const itemRefs = ref({});
const isMounted = ref(false);
const selectedItem = ref(null);

const totalCount = computed(() => props.items?.length ?? 0);

const visibleItems = computed(() =>
  props.items?.slice(0, displayCount.value) ?? []
);

const hasMore = computed(() =>
  displayCount.value < totalCount.value
);

function registerItemRef(id, el) {
  if (el?.$el) {
    itemRefs.value[id] = el.$el;
  }
}

function getViewportItems() {
  if (!listRef.value || !isMounted.value) return [];

  const listRect = listRef.value.getBoundingClientRect();

  return visibleItems.value.filter((item) => {
    const el = itemRefs.value[item.service_request];
    if (!el) return false;

    const rect = el.getBoundingClientRect();
    return rect.bottom > listRect.top && rect.top < listRect.bottom;
  });
}

function emitViewportItems() {
  if (!isMounted.value || typeof window === 'undefined') return;

  window.dispatchEvent(
    new CustomEvent('visible-items-changed', {
      detail: getViewportItems()
    })
  );
}

function onItemSelect(item) {
  if (!isMounted.value || typeof window === 'undefined') return;

  selectedItem.value = item;
  window.dispatchEvent(
    new CustomEvent('item-selected', { detail: item })
  );
}

function onMarkerSelected(event) {
  const item = event.detail;
  selectedItem.value = item;
  scrollToItem(item);
}

function scrollToItem(item) {
  const el = itemRefs.value[item.service_request];
  if (el && listRef.value) {
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

function onScroll() {
  loadMoreIfNeeded();
  emitViewportItems();
}

function loadMoreIfNeeded() {
  const list = listRef.value;
  if (!list || !hasMore.value) return;

  const distanceFromBottom = list.scrollHeight - list.scrollTop - list.clientHeight;

  if (distanceFromBottom < SCROLL_THRESHOLD) {
    displayCount.value = Math.min(
      displayCount.value + PAGE_SIZE,
      totalCount.value
    );
  }
}

watch(
  () => props.items,
  () => {
    displayCount.value = PAGE_SIZE;
    itemRefs.value = {};
  }
);

watch(visibleItems, () => {
  setTimeout(emitViewportItems, VIEWPORT_DEBOUNCE_MS);
});

onMounted(() => {
  isMounted.value = true;
  setTimeout(emitViewportItems, INITIAL_DELAY_MS);
  window.addEventListener('marker-selected', onMarkerSelected);
});

onUnmounted(() => {
  window.removeEventListener('marker-selected', onMarkerSelected);
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

.list-header {
  flex-shrink: 0;
}

.list-title {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 12px;
  color: #5f6368;
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
}
</style>
