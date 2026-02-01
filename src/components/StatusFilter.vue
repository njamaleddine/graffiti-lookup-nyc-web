<template>
  <select
    :value="modelValue"
    class="status-select"
    @change="$emit('update:modelValue', $event.target.value)"
  >
    <option value="">{{ placeholder }}</option>
    <option
      v-for="option in options"
      :key="option"
      :value="option"
    >
      {{ option }}
    </option>
  </select>
</template>

<script setup>
defineProps({
  modelValue: { type: String, default: '' },
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: 'All' }
});

defineEmits(['update:modelValue']);
</script>

<style scoped>
.status-select {
  width: 100%;
  padding: 10px 12px;
  font-size: 14px;
  font-family: inherit;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fff;
  color: #202124;
  outline: none;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s;
  box-sizing: border-box;
}

.status-select:focus {
  border-color: #1a73e8;
  box-shadow: 0 0 0 2px rgba(26, 115, 232, 0.15);
}

@media (max-width: 900px) {
  .status-select {
    padding: 8px 10px;
    font-size: 13px;
  }
}
</style>
