<template>
  <div class="search-container">
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
  placeholder: { type: String, default: 'Search...' }
});

defineEmits(['update:modelValue']);
</script>

<style scoped>
.search-container {
  position: relative;
  width: 100%;
}

.search-input {
  width: 100%;
  padding: 10px 36px 10px 12px;
  font-size: 14px;
  font-family: inherit;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fff;
  color: #202124;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  box-sizing: border-box;
}

.search-input::placeholder {
  color: #9aa0a6;
}

.search-input:focus {
  border-color: #1a73e8;
  box-shadow: 0 0 0 2px rgba(26, 115, 232, 0.15);
}

.clear-button {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  border: none;
  background: #e0e0e0;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  color: #5f6368;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.15s;
}

.clear-button:hover {
  background: #d0d0d0;
}

@media (max-width: 900px) {
  .search-input {
    padding: 8px 32px 8px 10px;
    font-size: 13px;
  }
}
</style>
