<template>
  <div class="search-container">
    <span class="search-icon"><svg
      width="15"
      height="15"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2.5"
      stroke-linecap="round"
      stroke-linejoin="round"
    ><circle
      cx="11"
      cy="11"
      r="8"
    /><line
      x1="21"
      y1="21"
      x2="16.65"
      y2="16.65"
    /></svg></span>
    <input
      :value="modelValue"
      type="text"
      class="search-input"
      :placeholder="placeholder"
      @input="$emit('update:modelValue', $event.target.value)"
    >
    <button
      v-if="modelValue"
      class="clear-button"
      aria-label="Clear search"
      @click="$emit('update:modelValue', '')"
    >
      ×
    </button>
  </div>
</template>

<script setup>
  defineProps({
    modelValue: { type: String, default: '' },
    placeholder: { type: String, default: 'Search...' },
  });

  defineEmits(['update:modelValue']);
</script>

<style scoped>
  .search-container {
    position: relative;
    width: 100%;
  }

  .search-icon {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    color: var(--text-tertiary, #94a3b8);
    opacity: 0.7;
    transition: all var(--transition-normal, 250ms cubic-bezier(0.16, 1, 0.3, 1));
    display: flex;
    align-items: center;
  }

  .search-container:focus-within .search-icon {
    opacity: 1;
    color: var(--primary, #6366f1);
  }

  .search-input {
    width: 100%;
    padding: 10px 36px 10px 38px;
    font-size: 14px;
    font-family: inherit;
    border: 1px solid var(--border, rgba(0, 0, 0, 0.06));
    border-radius: var(--radius-md, 12px);
    background: var(--surface, rgba(255, 255, 255, 0.7));
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    color: var(--text-primary, #0f172a);
    outline: none;
    transition: all var(--transition-normal, 250ms cubic-bezier(0.16, 1, 0.3, 1));
    box-sizing: border-box;
    box-shadow: var(--shadow-xs, 0 1px 2px rgba(0, 0, 0, 0.03));
  }

  .search-input::placeholder {
    color: var(--text-tertiary, #94a3b8);
  }

  .search-input:hover {
    border-color: var(--border-hover, rgba(0, 0, 0, 0.1));
    box-shadow: var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.04));
  }

  .search-input:focus {
    border-color: var(--primary, #6366f1);
    box-shadow:
      0 0 0 3px rgba(99, 102, 241, 0.1),
      var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.04));
  }

  .clear-button {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
    border: none;
    background: rgba(0, 0, 0, 0.06);
    border-radius: 50%;
    cursor: pointer;
    font-size: 13px;
    line-height: 1;
    color: var(--text-secondary, #475569);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast, 150ms cubic-bezier(0.16, 1, 0.3, 1));
  }

  .clear-button:hover {
    background: rgba(0, 0, 0, 0.1);
    transform: translateY(-50%) scale(1.1);
  }

  @media (max-width: 900px) {
    .search-input {
      padding: 8px 32px 8px 34px;
      font-size: 13px;
    }
  }
</style>
