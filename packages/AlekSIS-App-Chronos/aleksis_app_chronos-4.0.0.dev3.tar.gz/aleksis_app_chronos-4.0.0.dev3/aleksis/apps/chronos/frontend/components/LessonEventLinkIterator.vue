<script>
export default {
  name: "LessonEventLinkIterator",
  props: {
    items: {
      type: Array,
      required: true,
    },
    attr: {
      type: String,
      required: false,
      default: "name",
    },
  },
};
</script>

<template>
  <span v-bind="$attrs">
    <span v-for="(item, idx) in items" :key="idx">
      <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
      {{ item[attr] }}{{ idx + 1 < items.length ? "," : "" }}
    </span>
  </span>
</template>
