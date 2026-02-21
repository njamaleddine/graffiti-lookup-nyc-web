import { mount } from '@vue/test-utils';
import SearchBar from './SearchBar.vue';

describe('SearchBar.vue', () => {
  it('renders input and icon', () => {
    const wrapper = mount(SearchBar);
    expect(wrapper.find('input').exists()).toBe(true);
    expect(wrapper.find('.search-icon').exists()).toBe(true);
  });

  it('renders with placeholder', () => {
    const wrapper = mount(SearchBar, { props: { placeholder: 'Find...' } });
    expect(wrapper.find('input').attributes('placeholder')).toBe('Find...');
  });

  it('emits update:modelValue on input', async () => {
    const wrapper = mount(SearchBar, { props: { modelValue: '' } });
    const input = wrapper.find('input');
    await input.setValue('foo');
    expect(wrapper.emitted('update:modelValue')).toBeTruthy();
    expect(wrapper.emitted('update:modelValue')[0][0]).toBe('foo');
  });

  it('shows clear button when modelValue is not empty', () => {
    const wrapper = mount(SearchBar, { props: { modelValue: 'abc' } });
    expect(wrapper.find('.clear-button').exists()).toBe(true);
  });

  it('does not show clear button when modelValue is empty', () => {
    const wrapper = mount(SearchBar, { props: { modelValue: '' } });
    expect(wrapper.find('.clear-button').exists()).toBe(false);
  });

  it('clears input when clear button is clicked', async () => {
    const wrapper = mount(SearchBar, { props: { modelValue: 'abc' } });
    await wrapper.find('.clear-button').trigger('click');
    expect(wrapper.emitted('update:modelValue')).toBeTruthy();
    // Last emit should be ''
    const emits = wrapper.emitted('update:modelValue');
    expect(emits[emits.length - 1][0]).toBe('');
  });
});
