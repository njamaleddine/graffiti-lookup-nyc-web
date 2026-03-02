<template>
  <div class="select-container">
    <select
      :value="modelValue"
      class="status-select"
      @change="$emit('update:modelValue', $event.target.value)"
    >
      <option value="">
        {{ placeholder }}
      </option>
      <option
        v-for="option in options"
        :key="option"
        :value="option"
      >
        {{ option }}
      </option>
    </select>
    <span class="select-icon"><svg
      width="10"
      height="10"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="3"
      stroke-linecap="round"
      stroke-linejoin="round"
    ><polyline points="6 9 12 15 18 9" /></svg></span>
  </div>
</template>

<script setup>
  defineProps({
    modelValue: { type: String, default: '' },
    options: { type: Array, default: () => [] },
    placeholder: { type: String, default: 'All' },
  });

  defineEmits(['update:modelValue']);
</script>

<style scoped>
  .select-container {
    position: relative;
    width: 100%;
  }

  .status-select {
    width: 100%;
    padding: 10px 32px 10px 12px;
    font-size: 14px;
    font-family: inherit;
    border: 1px solid var(--border, rgba(0, 0, 0, 0.06));
    border-radius: var(--radius-md, 12px);
    background: var(--surface, rgba(255, 255, 255, 0.7));
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    color: var(--text-primary, #0f172a);
    outline: none;
    cursor: pointer;
    transition: all var(--transition-normal, 250ms cubic-bezier(0.16, 1, 0.3, 1));
    box-sizing: border-box;
    box-shadow: var(--shadow-xs, 0 1px 2px rgba(0, 0, 0, 0.03));
    appearance: none;
    -webkit-appearance: none;
  }

  .select-icon {
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

  .select-container:focus-within .select-icon {
    color: var(--primary, #6366f1);
    transform: translateY(-50%) rotate(180deg);
  }

  .status-select:hover {
    border-color: var(--border-hover, rgba(0, 0, 0, 0.1));
    box-shadow: var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.04));
  }

  .status-select:focus {
    border-color: var(--primary, #6366f1);
    box-shadow:
      0 0 0 3px rgba(99, 102, 241, 0.1),
      var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.04));
  }

  @media (max-width: 900px) {
    .status-select {
      padding: 8px 28px 8px 10px;
      font-size: 13px;
    }
  }
</style>
