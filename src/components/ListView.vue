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
import { ref, computed, watch, onMounted } from 'vue';
import ListItem from './ListItem.vue';

// ─────────────────────────────────────────────────────────────────────────────
// Props
// ─────────────────────────────────────────────────────────────────────────────

const props = defineProps({
  items: { type: Array, default: () => [] }
});

// ─────────────────────────────────────────────────────────────────────────────
// Constants
// ─────────────────────────────────────────────────────────────────────────────

const PAGE_SIZE = 50;
const SCROLL_THRESHOLD = 100;
const VIEWPORT_DEBOUNCE_MS = 50;
const INITIAL_DELAY_MS = 100;

// ─────────────────────────────────────────────────────────────────────────────
// State
// ─────────────────────────────────────────────────────────────────────────────

const listRef = ref(null);
const displayCount = ref(PAGE_SIZE);
const itemRefs = ref({});
const isMounted = ref(false);

// ─────────────────────────────────────────────────────────────────────────────
// Computed
// ─────────────────────────────────────────────────────────────────────────────

const totalCount = computed(() => props.items?.length ?? 0);

const visibleItems = computed(() =>
  props.items?.slice(0, displayCount.value) ?? []
);

const hasMore = computed(() =>
  displayCount.value < totalCount.value
);

// ─────────────────────────────────────────────────────────────────────────────
// Ref Registration (for viewport tracking)
// ─────────────────────────────────────────────────────────────────────────────

function registerItemRef(id, el) {
  if (el?.$el) {
    itemRefs.value[id] = el.$el;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Viewport Calculation
// ─────────────────────────────────────────────────────────────────────────────

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

// ─────────────────────────────────────────────────────────────────────────────
// Event Handlers
// ─────────────────────────────────────────────────────────────────────────────

function onItemSelect(item) {
  if (!isMounted.value || typeof window === 'undefined') return;

  window.dispatchEvent(
    new CustomEvent('item-selected', { detail: item })
  );
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

// ─────────────────────────────────────────────────────────────────────────────
// Watchers
// ─────────────────────────────────────────────────────────────────────────────

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

// ─────────────────────────────────────────────────────────────────────────────
// Lifecycle
// ─────────────────────────────────────────────────────────────────────────────

onMounted(() => {
  isMounted.value = true;
  setTimeout(emitViewportItems, INITIAL_DELAY_MS);
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
