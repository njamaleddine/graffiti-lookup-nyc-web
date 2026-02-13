
import { mount } from '@vue/test-utils';
import StatusChip from './StatusChip.vue';

describe('StatusChip.vue', () => {
  it('renders with default status', () => {
    const wrapper = mount(StatusChip);
    expect(wrapper.text()).toContain('Unknown');
    expect(wrapper.find('.status-chip').classes()).toContain('status-default');
    expect(wrapper.find('.status-emoji').text()).toBe('📍');
  });

  it('renders with known status and correct class/emoji', () => {
    const wrapper = mount(StatusChip, { props: { status: 'cleaned' } });
    expect(wrapper.text()).toContain('cleaned');
    expect(wrapper.find('.status-chip').classes()).toContain('status-cleaned');
    expect(wrapper.find('.status-emoji').text()).toBe('✨');
  });

  it('renders with status: to be cleaned', () => {
    const wrapper = mount(StatusChip, { props: { status: 'to be cleaned' } });
    expect(wrapper.find('.status-chip').classes()).toContain('status-scheduled');
    expect(wrapper.find('.status-emoji').text()).toBe('📅');
  });

  it('renders with status: dispatched no graffiti', () => {
    const wrapper = mount(StatusChip, { props: { status: 'dispatched - no graffiti' } });
    expect(wrapper.find('.status-chip').classes()).toContain('status-no-graffiti');
    expect(wrapper.find('.status-emoji').text()).toBe('✅');
  });

  it('renders with status: waiver', () => {
    const wrapper = mount(StatusChip, { props: { status: 'waiver' } });
    expect(wrapper.find('.status-chip').classes()).toContain('status-pending');
    expect(wrapper.find('.status-emoji').text()).toBe('⏳');
  });

  it('renders with status: notice', () => {
    const wrapper = mount(StatusChip, { props: { status: 'notice' } });
    expect(wrapper.find('.status-chip').classes()).toContain('status-notice');
    expect(wrapper.find('.status-emoji').text()).toBe('📋');
  });

  it('renders with status: notified', () => {
    const wrapper = mount(StatusChip, { props: { status: 'notified' } });
    expect(wrapper.find('.status-chip').classes()).toContain('status-notified');
    expect(wrapper.find('.status-emoji').text()).toBe('📬');
  });

  it('renders with status: inaccessible', () => {
    const wrapper = mount(StatusChip, { props: { status: 'inaccessible' } });
    expect(wrapper.find('.status-chip').classes()).toContain('status-inaccessible');
    expect(wrapper.find('.status-emoji').text()).toBe('🚫');
  });

  it('renders with status: intentional', () => {
    const wrapper = mount(StatusChip, { props: { status: 'intentional' } });
    expect(wrapper.find('.status-chip').classes()).toContain('status-intentional');
    expect(wrapper.find('.status-emoji').text()).toBe('🏷️');
  });

  it('renders with status: ineligible', () => {
    const wrapper = mount(StatusChip, { props: { status: 'ineligible' } });
    expect(wrapper.find('.status-chip').classes()).toContain('status-ineligible');
    expect(wrapper.find('.status-emoji').text()).toBe('❌');
  });

  it('renders with unknown status', () => {
    const wrapper = mount(StatusChip, { props: { status: 'something-unknown' } });
    expect(wrapper.find('.status-chip').classes()).toContain('status-default');
    expect(wrapper.find('.status-emoji').text()).toBe('📍');
  });
});
