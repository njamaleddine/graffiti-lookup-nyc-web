<template>
  <span
    class="status-chip"
    :class="statusClass"
  >
    <span class="status-emoji">{{ statusEmoji }}</span>
    {{ displayText }}
  </span>
</template>

<script setup>
  import { computed } from 'vue';

  const props = defineProps({
    status: { type: String, default: '' },
  });

  const STATUS_MAP = {
    'to be cleaned': 'scheduled',
    'dispatched.*no graffiti': 'no-graffiti',
    'property cleaned': 'cleaned',
    cleaned: 'cleaned',
    waiver: 'pending',
    'no response': 'pending',
    notice: 'notice',
    sent: 'notice',
    notified: 'notified',
    '90 days': 'notified',
    inaccessible: 'inaccessible',
    intentional: 'intentional',
    ineligible: 'ineligible',
    'cannot be determined': 'ineligible',
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

  const EMOJI_MAP = {
    'status-cleaned': '✨',
    'status-no-graffiti': '✅',
    'status-pending': '⏳',
    'status-notice': '📋',
    'status-notified': '📬',
    'status-inaccessible': '🚫',
    'status-intentional': '🏷️',
    'status-ineligible': '❌',
    'status-scheduled': '📅',
    'status-default': '📍',
  };

  const statusEmoji = computed(() => EMOJI_MAP[statusClass.value] || '📍');
</script>

<style scoped>
  .status-chip {
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 500;
    white-space: normal;
    word-break: break-word;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    transition: transform 0.15s ease;
  }

  .status-chip:hover {
    transform: scale(1.02);
  }

  .status-emoji {
    font-size: 10px;
  }

  .status-cleaned {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    color: #065f46;
  }

  .status-no-graffiti {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    color: #047857;
  }

  .status-pending {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    color: #92400e;
  }

  .status-notice {
    background: linear-gradient(135deg, #fef9c3 0%, #fde047 100%);
    color: #854d0e;
  }

  .status-notified {
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
    color: #1e40af;
  }

  .status-inaccessible {
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
    color: #b91c1c;
  }

  .status-intentional {
    background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%);
    color: #7c3aed;
  }

  .status-ineligible {
    background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
    color: #475569;
  }

  .status-scheduled {
    background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
    color: #0369a1;
  }

  .status-default {
    background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
    color: #6d28d9;
  }
</style>
