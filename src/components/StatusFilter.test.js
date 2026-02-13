
import { mount } from '@vue/test-utils';
import StatusFilter from './StatusFilter.vue';

describe('StatusFilter.vue', () => {
  const options = ['cleaned', 'pending', 'notice'];

  it('renders select and options', () => {
    const wrapper = mount(StatusFilter, { props: { options } });
    expect(wrapper.find('select').exists()).toBe(true);
    // +1 for placeholder
    expect(wrapper.findAll('option').length).toBe(options.length + 1);
  });

  it('renders with placeholder', () => {
    const wrapper = mount(StatusFilter, { props: { placeholder: 'Choose status', options } });
    expect(wrapper.find('option').text()).toBe('Choose status');
  });

  it('emits update:modelValue on change', async () => {
    const wrapper = mount(StatusFilter, { props: { options } });
    const select = wrapper.find('select');
    await select.setValue('pending');
    expect(wrapper.emitted('update:modelValue')).toBeTruthy();
    expect(wrapper.emitted('update:modelValue')[0][0]).toBe('pending');
  });

  it('selects the correct value', () => {
    const wrapper = mount(StatusFilter, { props: { modelValue: 'notice', options } });
    expect(wrapper.find('select').element.value).toBe('notice');
  });

  it('shows placeholder as selected when modelValue is empty', () => {
    const wrapper = mount(StatusFilter, { props: { modelValue: '', options } });
    expect(wrapper.find('select').element.value).toBe('');
  });
});
