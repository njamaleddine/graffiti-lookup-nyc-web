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
    <span class="select-icon">▼</span>
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
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    background: #fff;
    color: #1f2937;
    outline: none;
    cursor: pointer;
    transition: all 0.2s ease;
    box-sizing: border-box;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    appearance: none;
    -webkit-appearance: none;
  }

  .select-icon {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 10px;
    color: #9ca3af;
    pointer-events: none;
    transition: transform 0.2s ease;
  }

  .select-container:focus-within .select-icon {
    color: #7c4dff;
  }

  .status-select:focus {
    border-color: #7c4dff;
    box-shadow:
      0 0 0 3px rgba(124, 77, 255, 0.12),
      0 1px 2px rgba(0, 0, 0, 0.04);
  }

  .status-select:hover {
    border-color: #d1d5db;
  }

  @media (max-width: 900px) {
    .status-select {
      padding: 8px 28px 8px 10px;
      font-size: 13px;
    }
  }
</style>
