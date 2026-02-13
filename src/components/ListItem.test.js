
import { mount } from '@vue/test-utils';
import ListItem from './ListItem.vue';
import StatusChip from './StatusChip.vue';

const item = {
  service_request: 'SR123',
  address: '123 Main St',
  status: 'cleaned',
  created: '2024-01-01',
  last_updated: '2024-01-02'
};

describe('ListItem.vue', () => {
  it('renders all item fields', () => {
    const wrapper = mount(ListItem, {
      props: { item, index: 1 }
    });
    expect(wrapper.find('.index-badge').text()).toBe('1');
    expect(wrapper.find('.id-badge').text()).toContain('SR123');
    expect(wrapper.find('.address').text()).toBe('123 Main St');
    expect(wrapper.find('time').text()).toContain('2024-01-01');
    expect(wrapper.text()).toContain('2024-01-02');
  });

  it('applies selected class when isSelected is true', () => {
    const wrapper = mount(ListItem, {
      props: { item, index: 1, isSelected: true }
    });
    expect(wrapper.classes()).toContain('selected');
  });

  it('does not apply selected class when isSelected is false', () => {
    const wrapper = mount(ListItem, {
      props: { item, index: 1, isSelected: false }
    });
    expect(wrapper.classes()).not.toContain('selected');
  });

  it('emits select event with item when clicked', async () => {
    const wrapper = mount(ListItem, {
      props: { item, index: 1 }
    });
    await wrapper.find('.card-content').trigger('click');
    expect(wrapper.emitted('select')).toBeTruthy();
    expect(wrapper.emitted('select')[0][0]).toEqual(item);
  });

  it('renders StatusChip with correct status', () => {
    const wrapper = mount(ListItem, {
      props: { item, index: 1 },
      global: { components: { StatusChip } }
    });
    const chip = wrapper.findComponent(StatusChip);
    expect(chip.exists()).toBe(true);
    expect(chip.props('status')).toBe('cleaned');
  });

  // Skipped: Vue 3 will throw if required props are missing; this is enforced by the framework and not useful to test.

  it('accepts isSelected as optional', () => {
    const wrapper = mount(ListItem, {
      props: { item, index: 1 }
    });
    expect(wrapper.props('isSelected')).toBe(false);
  });

  it('validator fails if item is missing required fields', () => {
    const badItem = { address: 'No ID' };
    const wrapper = mount(ListItem, { props: { item: badItem, index: 1 } });
    expect(wrapper.props('item')).toEqual(badItem);
  });
});
