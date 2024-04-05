<script>
import timetableTypes from "./timetableTypes";

export default {
  name: "SelectTimetable",
  props: {
    value: {
      type: Object,
      required: false,
      default: null,
    },
    availableTimetables: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      selected: null,
      selectedFull: null,
      search: "",
      selectedTypes: ["GROUP", "TEACHER", "ROOM"],
      types: timetableTypes,
    };
  },
  watch: {
    value(val) {
      this.selectedFull = val;
      this.selected = val.id;
    },
    selectedFull(val) {
      this.$emit("input", val);
    },
  },
  computed: {
    availableTimetablesFiltered() {
      // Filter timetables by selected types
      return this.availableTimetables.filter((timetable) => {
        return this.selectedTypes.indexOf(timetable.type) !== -1;
      });
    },
  },
};
</script>

<template>
  <div>
    <v-card-text class="mb-0">
      <!-- Search field for timetables -->
      <v-text-field
        search
        filled
        rounded
        clearable
        autofocus
        v-model="search"
        :placeholder="$t('chronos.timetable.search')"
        prepend-inner-icon="mdi-magnify"
        hide-details="auto"
        class="mb-2"
      />

      <!-- Filter by timetable types -->
      <v-btn-toggle v-model="selectedTypes" dense block multiple class="d-flex">
        <v-btn
          v-for="type in types"
          :key="type.id"
          class="flex-grow-1"
          :value="type.id"
        >
          {{ $t(type.name) }}
        </v-btn>
      </v-btn-toggle>
    </v-card-text>

    <!-- Select of available timetables -->
    <v-data-iterator
      :items="availableTimetablesFiltered"
      item-key="id"
      :search="search"
      single-expand
      disable-pagination
    >
      <template #default="{ items, isExpanded, expand }">
        <v-list class="scrollable-list">
          <v-list-item-group v-model="selected">
            <v-list-item
              v-for="item in items"
              @click="selectedFull = item"
              :value="item.id"
              :key="item.id"
            >
              <v-list-item-icon color="primary">
                <v-icon v-if="item.type in types" color="secondary">
                  {{ types[item.type].icon }}
                </v-icon>
                <v-icon v-else color="secondary">mdi-grid</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>{{ item.name }}</v-list-item-title>
              </v-list-item-content>
              <v-list-item-action>
                <v-icon>mdi-chevron-right</v-icon>
              </v-list-item-action>
            </v-list-item>
          </v-list-item-group>
        </v-list>
      </template>
      <template #loading>
        <v-skeleton-loader
          type="list-item-avatar,list-item-avatar,list-item-avatar"
        />
      </template>
    </v-data-iterator>
  </div>
</template>

<style scoped>
.scrollable-list {
  height: 100%;
  overflow-y: scroll;
}
</style>
