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
      <div class="controls-row">
        <div class="sort-container">
          <select
            v-model="sortBy"
            class="sort-select"
            aria-label="Sort by"
          >
            <option
              v-for="opt in SORT_OPTIONS"
              :key="opt.value"
              :value="opt.value"
            >
              {{ opt.label }}
            </option>
          </select>
          <span class="sort-icon">
            <svg
              width="10"
              height="10"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="3"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </span>
        </div>
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
        :address-count="addressCounts[item.address] || 1"
        :address-dates="addressDates[item.address] || []"
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
    items: { type: Array, default: () => [] },
  });

  const PAGE_SIZE = 50;
  const SCROLL_THRESHOLD = 100;
  const VIEWPORT_DEBOUNCE_MS = 50;
  const INITIAL_DELAY_MS = 100;

  const SORT_OPTIONS = [
    { value: 'last_updated', label: 'Last Updated' },
    { value: 'created', label: 'Date Created' },
    { value: 'risk_high', label: 'Risk: High → Low' },
    { value: 'risk_low', label: 'Risk: Low → High' },
    { value: 'times_reported', label: 'Most Reported' },
    { value: 'address', label: 'Address (A–Z)' },
  ];

  const listRef = ref(null);
  const displayCount = ref(PAGE_SIZE);
  const itemRefs = ref({});
  const isMounted = ref(false);
  const selectedItem = ref(null);
  const searchQuery = ref('');
  const selectedStatus = ref('');
  const sortBy = ref('last_updated');

  function initFromUrlParams() {
    if (typeof window === 'undefined') return;
    const params = new URLSearchParams(window.location.search);
    const search = params.get('search');
    const status = params.get('status');
    const id = params.get('id');
    if (search) searchQuery.value = search;
    if (status) selectedStatus.value = status;
    const sort = params.get('sort');
    if (sort) sortBy.value = sort;
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
    if (sortBy.value && sortBy.value !== 'last_updated') {
      params.set('sort', sortBy.value);
    }
    const newUrl = params.toString()
      ? `${window.location.pathname}?${params.toString()}`
      : window.location.pathname;
    window.history.replaceState({}, '', newUrl);
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

  const sortedItems = computed(() => {
    const items = [...filteredItems.value];
    switch (sortBy.value) {
      case 'last_updated':
        return items.sort((a, b) => new Date(b.last_updated) - new Date(a.last_updated));
      case 'created':
        return items.sort((a, b) => new Date(b.created) - new Date(a.created));
      case 'risk_high':
        return items.sort((a, b) => (b.graffiti_likelihood ?? 0) - (a.graffiti_likelihood ?? 0));
      case 'risk_low':
        return items.sort((a, b) => (a.graffiti_likelihood ?? 0) - (b.graffiti_likelihood ?? 0));
      case 'times_reported':
        return items.sort((a, b) => (b.times_reported ?? 0) - (a.times_reported ?? 0));
      case 'address':
        return items.sort((a, b) => (a.address ?? '').localeCompare(b.address ?? ''));
      default:
        return items;
    }
  });

  const addressCounts = computed(() => {
    const counts = {};
    (props.items ?? []).forEach((item) => {
      counts[item.address] = (counts[item.address] || 0) + 1;
    });
    return counts;
  });

  const addressDates = computed(() => {
    const dates = {};
    (props.items ?? []).forEach((item) => {
      if (!dates[item.address]) dates[item.address] = [];
      dates[item.address].push(item.created);
    });
    Object.values(dates).forEach((arr) => arr.sort());
    return dates;
  });

  const visibleItems = computed(() => sortedItems.value.slice(0, displayCount.value));

  const hasMore = computed(() => displayCount.value < sortedItems.value.length);

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
        detail: getViewportItems(),
      })
    );
  }

  function onItemSelect(item) {
    if (!isMounted.value || typeof window === 'undefined') return;

    if (selectedItem.value?.service_request === item.service_request) {
      selectedItem.value = null;
      window.dispatchEvent(new CustomEvent('item-selected', { detail: null }));
    } else {
      selectedItem.value = item;
      window.dispatchEvent(new CustomEvent('item-selected', { detail: item }));
    }
  }

  function onMarkerSelected(event) {
    const item = event.detail;
    selectedItem.value = item;
    ensureItemVisibleAndScroll(item, 'instant');
  }

  function ensureItemVisibleAndScroll(item, behavior = 'smooth') {
    const itemIndex = sortedItems.value.findIndex(
      (i) => i.service_request === item.service_request
    );

    if (itemIndex === -1) return;

    if (itemIndex >= displayCount.value) {
      displayCount.value = itemIndex + PAGE_SIZE;
      nextTick(() => scrollToItem(item, behavior));
    } else {
      scrollToItem(item, behavior);
    }
  }

  function scrollToItem(item, behavior = 'smooth') {
    const el = itemRefs.value[item.service_request];
    if (el && listRef.value) {
      el.scrollIntoView({ behavior, block: 'center' });
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
      displayCount.value = Math.min(displayCount.value + PAGE_SIZE, filteredItems.value.length);
    }
  }

  function onFilterChange() {
    displayCount.value = PAGE_SIZE;
    itemRefs.value = {};
  }

  function onFilterByAddress(event) {
    searchQuery.value = event.detail;
  }

  function emitFilteredItems() {
    if (!isMounted.value || typeof window === 'undefined') return;

    const allSorted = sortedItems.value.map((item, i) => ({ ...item, _index: i + 1 }));

    window.dispatchEvent(
      new CustomEvent('filtered-items-changed', {
        detail: allSorted,
      })
    );
  }

  watch(sortedItems, emitFilteredItems);

  watch([searchQuery, selectedStatus, selectedItem, sortBy], updateUrlParams);

  watch(sortBy, () => {
    displayCount.value = PAGE_SIZE;
    itemRefs.value = {};
    if (listRef.value) listRef.value.scrollTop = 0;
  });

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
    initFromUrlParams();
    isMounted.value = true;
    setTimeout(emitViewportItems, INITIAL_DELAY_MS);
    window.addEventListener('marker-selected', onMarkerSelected);
    window.addEventListener('filter-by-address', onFilterByAddress);
  });

  onUnmounted(() => {
    window.removeEventListener('marker-selected', onMarkerSelected);
    window.removeEventListener('filter-by-address', onFilterByAddress);
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
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 12px;
    color: var(--text-primary, #0f172a);
  }

  .list-title .count {
    font-weight: 400;
    color: var(--text-tertiary, #64748b);
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
    background: var(--border, rgba(0, 0, 0, 0.06));
    border-radius: var(--radius-lg, 16px);
    overflow-y: auto;
    overflow-x: hidden;
    flex: 1;
    min-height: 0;
    box-shadow:
      var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.04)),
      0 0 0 1px var(--border, rgba(0, 0, 0, 0.06));
  }

  .report-list::-webkit-scrollbar {
    width: 4px;
  }

  .report-list::-webkit-scrollbar-track {
    background: transparent;
  }

  .report-list::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.08);
    border-radius: 10px;
  }

  .report-list::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0.15);
  }

  .loading-indicator {
    background: var(--surface-solid, #fff);
    padding: 20px;
    text-align: center;
    font-size: 12px;
    color: var(--text-tertiary, #94a3b8);
    animation: pulse 1.5s ease-in-out infinite;
  }

  @keyframes pulse {
    0%,
    100% {
      opacity: 1;
    }
    50% {
      opacity: 0.4;
    }
  }

  .no-results {
    background: var(--surface-solid, #fff);
    padding: 40px 16px;
    text-align: center;
    font-size: 14px;
    color: var(--text-tertiary, #94a3b8);
    border-radius: var(--radius-lg, 16px);
  }

  .no-results::before {
    content: '';
    display: block;
    width: 40px;
    height: 40px;
    margin: 0 auto 12px;
    background: rgba(0, 0, 0, 0.04);
    border-radius: 50%;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: center;
    background-size: 20px;
  }

  .controls-row {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
    align-items: center;
  }

  .sort-container {
    position: relative;
    width: 100%;
  }

  .sort-select {
    width: 100%;
    padding: 10px 32px 10px 12px;
    font-size: 14px;
    font-family: inherit;
    border: 1px solid var(--border, rgba(0, 0, 0, 0.06));
    border-radius: var(--radius-md, 12px);
    background: var(--surface, rgba(255, 255, 255, 0.7));
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    color: var(--text-secondary, #475569);
    outline: none;
    cursor: pointer;
    transition: all var(--transition-normal, 250ms cubic-bezier(0.16, 1, 0.3, 1));
    box-shadow: var(--shadow-xs, 0 1px 2px rgba(0, 0, 0, 0.03));
    appearance: none;
    -webkit-appearance: none;
  }

  .sort-select:hover {
    border-color: var(--border-hover, rgba(0, 0, 0, 0.1));
    box-shadow: var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.04));
  }

  .sort-select:focus {
    border-color: var(--primary, #6366f1);
    box-shadow:
      0 0 0 3px rgba(99, 102, 241, 0.1),
      var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.04));
  }

  .sort-icon {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-tertiary, #94a3b8);
    pointer-events: none;
    transition: all var(--transition-normal, 250ms cubic-bezier(0.16, 1, 0.3, 1));
    display: flex;
    align-items: center;
  }

  .sort-container:focus-within .sort-icon {
    color: var(--primary, #6366f1);
    transform: translateY(-50%) rotate(180deg);
  }

  @media (max-width: 900px) {
    .list-container {
      height: 100%;
    }
    .list-title {
      display: none;
    }
    .filter-row {
      flex-direction: row;
      gap: 6px;
      margin-bottom: 6px;
    }
    .search-bar {
      flex: 2;
      min-width: 0;
    }
    .status-filter {
      flex: 1;
      min-width: 0;
      max-width: 120px;
    }
    .controls-row {
      margin-bottom: 6px;
    }
    .sort-select {
      padding: 8px 10px;
      font-size: 13px;
    }
  }
</style>
