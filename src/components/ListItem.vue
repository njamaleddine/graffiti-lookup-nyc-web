<template>
  <li
    class="report-card"
    :class="{ selected: isSelected }"
  >
    <div
      class="card-content"
      @click="() => emit('select', props.item)"
    >
      <header class="card-header">
        <span class="index-badge">{{ index }}</span>
        <span class="id-badge">#{{ item.service_request }}</span>
        <span class="address">{{ item.address }}</span>
        <button
          class="predictions-toggle-btn"
          aria-label="Show predictions"
          @click.stop="togglePredictions"
        >
          <span class="ai-emoji">⋮</span>
        </button>
      </header>

      <div class="card-status">
        <StatusChip :status="item.status" />
      </div>

      <footer class="card-meta">
        <time>Created: {{ item.created }}</time>
        <time>Updated: {{ item.last_updated }}</time>
      </footer>
    </div>

    <transition name="slide-predictions">
      <div
        v-if="showPredictions"
        class="predictions-tab"
      >
        <div class="section-group" v-if="hasStats">
          <div class="section-header">
            <span class="section-title">Location Stats</span>
          </div>
          <ul class="section-list">
            <li>
              <span>Times reported:</span> <strong>{{ item.times_reported }}</strong>
            </li>
            <li>
              <span>Times cleaned:</span> <strong>{{ item.times_cleaned }}</strong>
            </li>
          </ul>
        </div>

        <div class="section-group" v-if="hasPredictions">
          <div class="section-header">
            <span class="section-title">Predictions</span>
          </div>
          <ul class="section-list">
            <li v-if="item.graffiti_likelihood !== undefined">
              <span>Retagging risk:</span> <strong>{{ item.graffiti_likelihood.toFixed(1) }}%</strong>
            </li>
            <li v-if="item.cleaning_likelihood !== undefined">
              <span>Cleaning likelihood:</span> <strong>{{ item.cleaning_likelihood.toFixed(1) }}%</strong>
            </li>
            <li v-if="estimatedRetagDate">
              <span>Est. next tag:</span> <strong>{{ estimatedRetagDate }}</strong>
            </li>
            <li v-if="estimatedCleaningDate">
              <span>Est. cleaning:</span> <strong>{{ estimatedCleaningDate }}</strong>
            </li>
          </ul>
        </div>
      </div>
    </transition>
  </li>
</template>

<script setup>
  import StatusChip from './StatusChip.vue';
  import { ref, computed, watch, toRefs, defineProps, defineEmits } from 'vue';

  function addDays(dateStr, days) {
    const date = new Date(dateStr + 'T00:00:00');
    date.setDate(date.getDate() + days);
    return date.toISOString().slice(0, 10);
  }

  function isValidDate(value) {
    return value && value !== 'Unknown';
  }

  const props = defineProps({
    item: {
      type: Object,
      required: true,
      validator: (value) => 'service_request' in value && 'address' in value,
    },
    index: {
      type: Number,
      required: true,
    },
    isSelected: {
      type: Boolean,
      default: false,
    },
  });

  const { isSelected } = toRefs(props);

  const emit = defineEmits(['select']);

  const showPredictions = ref(false);

  function togglePredictions() {
    showPredictions.value = !showPredictions.value;
  }

  watch(isSelected, (val) => {
    if (!val) showPredictions.value = false;
  });

  const estimatedRetagDate = computed(() => {
    const { predicted_recurrence_days, last_updated, estimated_next_tag } = props.item;
    if (predicted_recurrence_days > 0 && last_updated) {
      return addDays(last_updated, predicted_recurrence_days);
    }
    return isValidDate(estimated_next_tag) ? estimated_next_tag : null;
  });

  const estimatedCleaningDate = computed(() => {
    const { predicted_resolution_days, created, predicted_cleaning_date } = props.item;
    if (predicted_resolution_days > 0 && created) {
      return addDays(created, predicted_resolution_days);
    }
    return isValidDate(predicted_cleaning_date) ? predicted_cleaning_date : null;
  });

  const hasStats = computed(() => {
    return (props.item.times_reported ?? 0) > 0 || (props.item.times_cleaned ?? 0) > 0;
  });

  const hasPredictions = computed(() => {
    return props.item.graffiti_likelihood !== undefined
      || props.item.cleaning_likelihood !== undefined
      || estimatedRetagDate.value
      || estimatedCleaningDate.value;
  });
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

  .predictions-tab {
    background: linear-gradient(135deg, #f3f4f6 0%, #e0e7ff 100%);
    border-radius: 10px;
    margin: 12px 0 0 0;
    padding: 16px 18px;
    box-shadow: 0 2px 8px rgba(124,77,255,0.08);
    animation: slideInPredictions 0.4s cubic-bezier(.68,-.55,.27,1.55);
  }

  .predictions-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
  }

  .ai-emoji {
    font-size: 1.6em;
    vertical-align: middle;
  }

  .predictions-title {
    font-weight: 600;
    font-size: 0.9em;
    color: #7c4dff;
  }

  .predictions-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .predictions-list li {
    margin-bottom: 8px;
    font-size: 13px;
    color: #333;
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .section-group + .section-group {
    margin-top: 14px;
    padding-top: 12px;
    border-top: 1px solid rgba(124, 77, 255, 0.12);
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
  }

  .section-title {
    font-weight: 600;
    font-size: 0.85em;
    color: #7c4dff;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  .section-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .section-list li {
    margin-bottom: 6px;
    font-size: 13px;
    color: #333;
    display: flex;
    gap: 8px;
    align-items: center;
  }

  @keyframes slideInPredictions {
    from {
      opacity: 0;
      transform: translateX(40px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  .slide-predictions-enter-active, .slide-predictions-leave-active {
    transition: all 0.4s cubic-bezier(.68,-.55,.27,1.55);
  }

  .slide-predictions-enter-from, .slide-predictions-leave-to {
    opacity: 0;
    transform: translateX(40px);
  }

  .slide-predictions-enter-to, .slide-predictions-leave-from {
    opacity: 1;
    transform: translateX(0);
  }

  .predictions-toggle-btn {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 50%;
    padding: 0;
    height: 28px;
    width: 28px;
    min-width: 28px;
    max-width: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1em;
    color: #6366f1;
    font-weight: 500;
    box-shadow: 0 1px 4px rgba(60,60,100,0.07);
    cursor: pointer;
    margin-left: auto;
    transition: box-shadow 0.15s, border 0.15s, background 0.15s;
    outline: none;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    position: relative;
  }
  .predictions-toggle-btn:hover, .predictions-toggle-btn:focus {
    background: #ede9fe;
    border-color: #a5b4fc;
    box-shadow: 0 2px 8px rgba(124,77,255,0.10);
  }
  .predictions-toggle-btn:active {
    background: #e0e7ff;
    border-color: #6366f1;
    box-shadow: 0 1px 3px rgba(60,60,100,0.04);
  }
  .predictions-toggle-btn .ai-emoji {
    font-size: 1em;
    margin: -2px 0 0 0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #6366f1;
    opacity: 0.85;
    pointer-events: none;
  }
  .predictions-toggle-btn .predictions-label {
    font-size: 0.97em;
    color: #4f46e5;
    font-weight: 600;
    letter-spacing: 0.01em;
    display: inline;
    white-space: nowrap;
    overflow: hidden;
    max-width: 70px;
  }
  @media (max-width: 700px) {
    .predictions-toggle-btn {
      padding: 0;
      height: 32px;
      width: 32px;
      min-width: 32px;
      border-radius: 50%;
      gap: 0;
      justify-content: center;
      max-width: 32px;
    }
    .predictions-toggle-btn .ai-emoji {
      font-size: 1.2em;
      margin: 0;
    }
    .predictions-toggle-btn .predictions-label {
      display: none;
    }
  }
</style>
