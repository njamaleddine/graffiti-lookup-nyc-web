<template>
  <span
    class="status-chip"
    :class="statusClass"
  >
    {{ displayText }}
  </span>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  status: { type: String, default: '' }
});

const STATUS_MAP = {
  'to be cleaned': 'scheduled',
  'dispatched.*no graffiti': 'no-graffiti',
  'property cleaned': 'cleaned',
  'cleaned': 'cleaned',
  'waiver': 'pending',
  'no response': 'pending',
  'notice': 'notice',
  'sent': 'notice',
  'notified': 'notified',
  '90 days': 'notified',
  'inaccessible': 'inaccessible',
  'intentional': 'intentional',
  'ineligible': 'ineligible',
  'cannot be determined': 'ineligible'
};

const statusClass = computed(() => {
  if (!props.status) return 'status-default';

  const normalized = props.status.toLowerCase();

  // Check "to be cleaned" before "cleaned" to avoid false match
  if (normalized.includes('to be cleaned')) return 'status-scheduled';

  for (const [pattern, className] of Object.entries(STATUS_MAP)) {
    if (pattern.includes('.*')) {
      const regex = new RegExp(pattern);
      if (regex.test(normalized)) return `status-${className}`;
    } else if (normalized.includes(pattern)) {
      return `status-${className}`;
    }
  }

  return 'status-default';
});

const displayText = computed(() => props.status || 'Unknown');
</script>

<style scoped>
.status-chip {
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 10px;
  font-weight: 500;
  white-space: nowrap;
}

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
</style>
