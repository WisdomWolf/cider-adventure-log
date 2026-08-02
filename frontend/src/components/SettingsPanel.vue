<template>
  <v-dialog :model-value="modelValue" max-width="480px" @update:model-value="$emit('update:modelValue', $event)">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between font-display text-h6 font-weight-bold">
        <span>Settings</span>
        <v-btn icon size="small" variant="text" @click="$emit('update:modelValue', false)">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text>
        <p class="text-overline text-medium-emphasis mb-2">Appearance</p>
        <div class="d-flex flex-column ga-2">
          <v-card
            v-for="option in THEME_FAMILIES"
            :key="option.key"
            :variant="currentFamily === option.key ? 'tonal' : 'outlined'"
            :color="currentFamily === option.key ? 'primary' : undefined"
            class="pa-3 d-flex align-center clickable-row"
            @click="selectFamily(option.key)"
          >
            <span class="theme-swatch mr-3" :style="{ background: option.swatch }"></span>
            <div class="flex-grow-1">
              <div class="font-weight-bold">{{ option.label }}</div>
              <div class="text-caption text-medium-emphasis">{{ option.tagline }}</div>
            </div>
            <v-icon v-if="currentFamily === option.key" color="primary">mdi-check-circle</v-icon>
          </v-card>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import { THEME_FAMILIES, themeNameFor, familyFromThemeName, isDarkThemeName, setStoredTheme } from "../theme";

export default {
  props: {
    modelValue: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["update:modelValue"],
  data() {
    return { THEME_FAMILIES };
  },
  computed: {
    currentFamily() {
      return familyFromThemeName(this.$vuetify.theme.global.name);
    },
    isDark() {
      return isDarkThemeName(this.$vuetify.theme.global.name);
    },
  },
  methods: {
    selectFamily(family) {
      const next = themeNameFor(family, this.isDark);
      this.$vuetify.theme.global.name = next;
      setStoredTheme(next);
    },
  },
};
</script>

<style scoped>
.theme-swatch {
  display: inline-block;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  flex-shrink: 0;
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.15);
}
</style>
