<template>
  <section class="list-container">
    <header class="list-header">
      <h2 class="list-title">
        Graffiti Reports
        <span class="count">({{ filteredItems.length }} of {{ totalCount }})</span>
      </h2>
      <div class="filter-row">
        <SearchBar
          v-model="searchQuery"
          placeholder="Search by ID or address..."
          class="search-bar"
        />
        <StatusFilter
          v-model="selectedStatus"
          :options="uniqueStatuses"
          placeholder="All statuses"
          class="status-filter"
        />
      </div>
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

      <li
        v-if="filteredItems.length === 0 && (searchQuery || selectedStatus)"
        class="no-results"
      >
        No results found
      </li>
    </ul>
  </section>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue';
import SearchBar from './SearchBar.vue';
import StatusFilter from './StatusFilter.vue';
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
const searchQuery = ref('');
const selectedStatus = ref('');

function initFromUrlParams() {
  if (typeof window === 'undefined') return;
  const params = new URLSearchParams(window.location.search);
  const search = params.get('search');
  const status = params.get('status');
  const id = params.get('id');
  if (search) searchQuery.value = search;
  if (status) selectedStatus.value = status;
  if (id) {
    const item = props.items.find((i) => i.service_request === id);
    if (item) {
      selectedItem.value = item;
      setTimeout(() => scrollToItem(item), 150);
    }
  }
}

function updateUrlParams() {
  if (typeof window === 'undefined') return;
  const params = new URLSearchParams();
  if (searchQuery.value.trim()) {
    params.set('search', searchQuery.value.trim());
  }
  if (selectedStatus.value) {
    params.set('status', selectedStatus.value);
  }
  if (selectedItem.value?.service_request) {
    params.set('id', selectedItem.value.service_request);
  }
  const newUrl = params.toString()
    ? `${window.location.pathname}?${params.toString()}`
    : window.location.pathname;
  window.history.replaceState({}, '', newUrl);
}

if (typeof window !== 'undefined') {
  initFromUrlParams();
}

const totalCount = computed(() => props.items?.length ?? 0);

const uniqueStatuses = computed(() => {
  const statuses = new Set();
  (props.items ?? []).forEach((item) => {
    if (item.status) {
      statuses.add(item.status);
    }
  });
  return Array.from(statuses).sort();
});

const filteredItems = computed(() => {
  let items = props.items ?? [];

  if (selectedStatus.value) {
    items = items.filter((item) => item.status === selectedStatus.value);
  }

  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim();
    items = items.filter((item) => {
      const id = (item.service_request || '').toLowerCase();
      const address = (item.address || '').toLowerCase();
      return id.includes(query) || address.includes(query);
    });
  }
  
  return items;
});

const visibleItems = computed(() =>
  filteredItems.value.slice(0, displayCount.value)
);

const hasMore = computed(() =>
  displayCount.value < filteredItems.value.length
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

  if (selectedItem.value?.service_request === item.service_request) {
    selectedItem.value = null;
    window.dispatchEvent(
      new CustomEvent('item-selected', { detail: null })
    );
  } else {
    selectedItem.value = item;
    window.dispatchEvent(
      new CustomEvent('item-selected', { detail: item })
    );
  }
}

function onMarkerSelected(event) {
  const item = event.detail;
  selectedItem.value = item;
  ensureItemVisibleAndScroll(item);
}

function ensureItemVisibleAndScroll(item) {
  const itemIndex = filteredItems.value.findIndex(
    (i) => i.service_request === item.service_request
  );

  if (itemIndex === -1) return;

  if (itemIndex >= displayCount.value) {
    displayCount.value = itemIndex + PAGE_SIZE;
    nextTick(() => scrollToItem(item));
  } else {
    scrollToItem(item);
  }
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
      filteredItems.value.length
    );
  }
}

function onFilterChange() {
  displayCount.value = PAGE_SIZE;
  itemRefs.value = {};
}

function emitFilteredItems() {
  if (!isMounted.value || typeof window === 'undefined') return;

  const allFiltered = filteredItems.value
    .map((item, i) => ({ ...item, _index: i + 1 }));
  
  window.dispatchEvent(
    new CustomEvent('filtered-items-changed', {
      detail: allFiltered
    })
  );
}

watch(filteredItems, emitFilteredItems);

watch([searchQuery, selectedStatus, selectedItem], updateUrlParams);

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
  height: 100%;
  min-height: 0;
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

.filter-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  align-items: stretch;
}

.search-bar {
  flex: 2;
  min-width: 120px;
  display: flex;
}

.status-filter {
  flex: 1;
  max-width: 160px;
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

.no-results {
  background: #f8f9fa;
  padding: 24px 16px;
  text-align: center;
  font-size: 14px;
  color: #5f6368;
}

@media (max-width: 900px) {
  .list-container {
    height: 100%;
  }
  .list-title {
    margin-bottom: 8px;
  }
  .filter-row {
    flex-direction: row;
    gap: 8px;
    margin-bottom: 8px;
  }
  .search-bar {
    flex: 2;
    min-width: 100px;
  }
  .status-filter {
    flex: 1;
    max-width: 120px;
  }
}
</style>
