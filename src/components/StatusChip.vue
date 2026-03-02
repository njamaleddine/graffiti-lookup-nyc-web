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
    border-radius: 20px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 500;
    white-space: normal;
    word-break: break-word;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    transition: all 200ms cubic-bezier(0.16, 1, 0.3, 1);
    border: 1px solid transparent;
  }

  .status-chip:hover {
    transform: translateY(-1px);
    box-shadow: 0 3px 12px rgba(0, 0, 0, 0.06);
  }

  .status-emoji {
    font-size: 10px;
    flex-shrink: 0;
  }

  .status-cleaned {
    background: rgba(209, 250, 229, 0.65);
    color: #065f46;
    border-color: rgba(16, 185, 129, 0.2);
  }

  .status-no-graffiti {
    background: rgba(209, 250, 229, 0.65);
    color: #047857;
    border-color: rgba(16, 185, 129, 0.2);
  }

  .status-pending {
    background: rgba(254, 243, 199, 0.65);
    color: #92400e;
    border-color: rgba(245, 158, 11, 0.2);
  }

  .status-notice {
    background: rgba(254, 249, 195, 0.65);
    color: #854d0e;
    border-color: rgba(234, 179, 8, 0.2);
  }

  .status-notified {
    background: rgba(219, 234, 254, 0.65);
    color: #1e40af;
    border-color: rgba(59, 130, 246, 0.2);
  }

  .status-inaccessible {
    background: rgba(254, 226, 226, 0.65);
    color: #b91c1c;
    border-color: rgba(239, 68, 68, 0.2);
  }

  .status-intentional {
    background: rgba(243, 232, 255, 0.65);
    color: #7c3aed;
    border-color: rgba(139, 92, 246, 0.2);
  }

  .status-ineligible {
    background: rgba(241, 245, 249, 0.65);
    color: #475569;
    border-color: rgba(100, 116, 139, 0.15);
  }

  .status-scheduled {
    background: rgba(224, 242, 254, 0.65);
    color: #0369a1;
    border-color: rgba(14, 165, 233, 0.2);
  }

  .status-default {
    background: rgba(237, 233, 254, 0.65);
    color: #6d28d9;
    border-color: rgba(139, 92, 246, 0.2);
  }
</style>
