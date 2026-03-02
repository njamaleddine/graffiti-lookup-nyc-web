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
          :class="{ active: showPredictions }"
          aria-label="Show predictions"
          @click.stop="togglePredictions"
        >
          <svg class="toggle-chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
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
          <div class="stats-grid">
            <div class="stat-card">
              <span class="stat-number">{{ item.times_reported }}</span>
              <span class="stat-label">Reported</span>
            </div>
            <div class="stat-card">
              <span class="stat-number">{{ item.times_cleaned }}</span>
              <span class="stat-label">Cleaned</span>
            </div>
          </div>
        </div>

        <div class="section-group" v-if="hasPredictions">
          <div class="section-header">
            <span class="section-title">Predictions</span>
          </div>
          <ul class="section-list">
            <li v-if="item.graffiti_likelihood !== undefined" class="metric-row">
              <span class="metric-label">Retagging risk</span>
              <div class="metric-visual">
                <div class="progress-track">
                  <div
                    class="progress-fill"
                    :class="riskLevel"
                    :style="{ width: Math.min(item.graffiti_likelihood, 100).toFixed(1) + '%' }"
                  ></div>
                </div>
                <strong class="metric-number" :class="riskLevel">{{ item.graffiti_likelihood.toFixed(1) }}%</strong>
              </div>
            </li>
            <li v-if="item.cleaning_likelihood !== undefined" class="metric-row">
              <span class="metric-label">Cleaning likelihood</span>
              <div class="metric-visual">
                <div class="progress-track">
                  <div
                    class="progress-fill"
                    :class="cleaningLevel"
                    :style="{ width: Math.min(item.cleaning_likelihood, 100).toFixed(1) + '%' }"
                  ></div>
                </div>
                <strong class="metric-number" :class="cleaningLevel">{{ item.cleaning_likelihood.toFixed(1) }}%</strong>
              </div>
            </li>
            <li v-if="estimatedRetagDate" class="date-row">
              <span class="metric-label">Estimated next tag</span>
              <strong class="date-value">{{ estimatedRetagDate }}</strong>
            </li>
            <li v-if="estimatedCleaningDate" class="date-row">
              <span class="metric-label">Estimated cleaning</span>
              <strong class="date-value">{{ estimatedCleaningDate }}</strong>
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

  const riskLevel = computed(() => {
    const val = props.item.graffiti_likelihood ?? 0;
    if (val >= 70) return 'level-high';
    if (val >= 40) return 'level-medium';
    return 'level-low';
  });

  const cleaningLevel = computed(() => {
    const val = props.item.cleaning_likelihood ?? 0;
    if (val >= 70) return 'level-success';
    if (val >= 40) return 'level-moderate';
    return 'level-muted';
  });
</script>

<style scoped>
  .report-card {
    background: var(--surface-solid, #fff);
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    transition: all 200ms cubic-bezier(0.16, 1, 0.3, 1);
    cursor: pointer;
    animation: slideIn 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    animation-fill-mode: backwards;
    position: relative;
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(6px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .report-card:first-child {
    border-radius: var(--radius-lg, 16px) var(--radius-lg, 16px) 0 0;
  }

  .report-card:last-child {
    border-radius: 0 0 var(--radius-lg, 16px) var(--radius-lg, 16px);
  }

  .report-card:hover {
    background: #f8faff;
  }

  .report-card.selected {
    background: linear-gradient(135deg, rgba(237, 233, 254, 0.5) 0%, rgba(224, 231, 255, 0.5) 100%);
    box-shadow: inset 3px 0 0 var(--primary, #6366f1);
  }

  .card-content {
    display: contents;
  }

  .card-header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    margin-bottom: 8px;
    gap: 8px;
  }

  .index-badge {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.06) 100%);
    color: var(--primary, #6366f1);
    border-radius: var(--radius-sm, 8px);
    min-width: 26px;
    height: 22px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 600;
    flex-shrink: 0;
    padding: 0 6px;
    transition: all var(--transition-fast, 150ms cubic-bezier(0.16, 1, 0.3, 1));
  }

  .report-card:hover .index-badge {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0.1) 100%);
    transform: scale(1.05);
  }

  .id-badge {
    background: rgba(0, 0, 0, 0.04);
    color: var(--text-secondary, #475569);
    border-radius: 6px;
    padding: 3px 7px;
    font-size: 10px;
    font-weight: 500;
    white-space: nowrap;
    flex-shrink: 0;
    font-family: ui-monospace, 'SF Mono', monospace;
  }

  .address {
    font-weight: 500;
    font-size: 13px;
    color: var(--text-primary, #0f172a);
    line-height: 1.4;
    flex: 1;
  }

  .card-status {
    margin-bottom: 8px;
  }

  .card-meta {
    display: flex;
    gap: 14px;
    font-size: 11px;
    color: var(--text-tertiary, #94a3b8);
    flex-wrap: wrap;
  }

  /* --- Toggle Button --- */
  .predictions-toggle-btn {
    background: transparent;
    border: 1px solid var(--border, rgba(0, 0, 0, 0.06));
    border-radius: 50%;
    padding: 0;
    height: 28px;
    width: 28px;
    min-width: 28px;
    max-width: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-tertiary, #94a3b8);
    cursor: pointer;
    margin-left: auto;
    transition: all var(--transition-normal, 250ms cubic-bezier(0.16, 1, 0.3, 1));
    outline: none;
    overflow: hidden;
    position: relative;
  }

  .predictions-toggle-btn:hover {
    background: rgba(99, 102, 241, 0.06);
    border-color: rgba(99, 102, 241, 0.2);
    color: var(--primary, #6366f1);
  }

  .predictions-toggle-btn.active {
    background: rgba(99, 102, 241, 0.08);
    border-color: rgba(99, 102, 241, 0.25);
    color: var(--primary, #6366f1);
  }

  .toggle-chevron {
    transition: transform var(--transition-spring, 400ms cubic-bezier(0.34, 1.56, 0.64, 1));
  }

  .predictions-toggle-btn.active .toggle-chevron {
    transform: rotate(180deg);
  }

  /* --- Predictions Panel --- */
  .predictions-tab {
    background: rgba(248, 250, 252, 0.8);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid var(--border, rgba(0, 0, 0, 0.06));
    border-radius: var(--radius-md, 12px);
    margin: 12px 0 0 0;
    padding: 16px;
    animation: expandIn 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  }

  @keyframes expandIn {
    from {
      opacity: 0;
      transform: translateY(-8px) scale(0.98);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  .slide-predictions-enter-active,
  .slide-predictions-leave-active {
    transition: all 300ms cubic-bezier(0.16, 1, 0.3, 1);
  }

  .slide-predictions-enter-from,
  .slide-predictions-leave-to {
    opacity: 0;
    transform: translateY(-8px);
  }

  .slide-predictions-enter-to,
  .slide-predictions-leave-from {
    opacity: 1;
    transform: translateY(0);
  }

  /* --- Section Groups --- */
  .section-group + .section-group {
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid var(--border, rgba(0, 0, 0, 0.06));
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
  }

  .section-title {
    font-weight: 600;
    font-size: 10px;
    color: var(--text-tertiary, #94a3b8);
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }

  /* --- Stats Grid --- */
  .stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }

  .stat-card {
    background: var(--surface-solid, #fff);
    border: 1px solid var(--border, rgba(0, 0, 0, 0.06));
    border-radius: var(--radius-sm, 8px);
    padding: 10px 12px;
    display: flex;
    flex-direction: column;
    gap: 2px;
    transition: all var(--transition-fast, 150ms cubic-bezier(0.16, 1, 0.3, 1));
  }

  .stat-card:hover {
    border-color: rgba(99, 102, 241, 0.15);
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.06);
  }

  .stat-number {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary, #0f172a);
    letter-spacing: -0.03em;
    line-height: 1;
  }

  .stat-label {
    font-size: 10px;
    font-weight: 500;
    color: var(--text-tertiary, #94a3b8);
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  /* --- Predictions List --- */
  .section-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  /* --- Metric Row with Progress Bar --- */
  .metric-row {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }

  .metric-label {
    font-size: 11px;
    font-weight: 500;
    color: var(--text-secondary, #475569);
  }

  .metric-visual {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .progress-track {
    flex: 1;
    height: 6px;
    background: rgba(0, 0, 0, 0.04);
    border-radius: 3px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 600ms cubic-bezier(0.16, 1, 0.3, 1);
    min-width: 2px;
  }

  .progress-fill.level-high {
    background: linear-gradient(90deg, #f97316, #ef4444);
  }

  .progress-fill.level-medium {
    background: linear-gradient(90deg, #eab308, #f97316);
  }

  .progress-fill.level-low {
    background: linear-gradient(90deg, #22c55e, #10b981);
  }

  .progress-fill.level-success {
    background: linear-gradient(90deg, #10b981, #06b6d4);
  }

  .progress-fill.level-moderate {
    background: linear-gradient(90deg, #06b6d4, #6366f1);
  }

  .progress-fill.level-muted {
    background: rgba(0, 0, 0, 0.12);
  }

  .metric-number {
    font-size: 13px;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
    min-width: 48px;
    text-align: right;
  }

  .metric-number.level-high {
    color: #ef4444;
  }

  .metric-number.level-medium {
    color: #f59e0b;
  }

  .metric-number.level-low {
    color: #10b981;
  }

  .metric-number.level-success {
    color: #10b981;
  }

  .metric-number.level-moderate {
    color: #06b6d4;
  }

  .metric-number.level-muted {
    color: var(--text-tertiary, #94a3b8);
  }

  /* --- Date Rows --- */
  .date-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
  }

  .date-value {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary, #0f172a);
    font-variant-numeric: tabular-nums;
  }

  @media (max-width: 900px) {
    .report-card {
      padding: 10px 12px;
    }
  }
</style>
