<template>
  <div class="search-container">
    <span class="search-icon">🔍</span>
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
    font-size: 14px;
    pointer-events: none;
    opacity: 0.6;
    transition: opacity 0.2s;
  }

  .search-container:focus-within .search-icon {
    opacity: 1;
  }

  .search-input {
    width: 100%;
    padding: 10px 36px 10px 38px;
    font-size: 14px;
    font-family: inherit;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    background: #fff;
    color: #1f2937;
    outline: none;
    transition: all 0.2s ease;
    box-sizing: border-box;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  }

  .search-input::placeholder {
    color: #9ca3af;
  }

  .search-input:focus {
    border-color: #7c4dff;
    box-shadow:
      0 0 0 3px rgba(124, 77, 255, 0.12),
      0 1px 2px rgba(0, 0, 0, 0.04);
  }

  .clear-button {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    width: 22px;
    height: 22px;
    border: none;
    background: #e5e7eb;
    border-radius: 50%;
    cursor: pointer;
    font-size: 14px;
    line-height: 1;
    color: #6b7280;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.15s ease;
  }

  .clear-button:hover {
    background: #d1d5db;
    transform: translateY(-50%) scale(1.1);
  }

  @media (max-width: 900px) {
    .search-input {
      padding: 8px 32px 8px 34px;
      font-size: 13px;
    }
    .search-icon {
      font-size: 12px;
      left: 10px;
    }
  }
</style>
