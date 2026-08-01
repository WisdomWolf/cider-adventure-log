<template>
  <v-card>
    <v-card-title class="font-display text-h5 font-weight-bold">
      Import Ratings
    </v-card-title>

    <!-- Step 1: upload -->
    <v-card-text v-if="step === 'upload'">
      <p class="text-body-2 text-medium-emphasis mb-4">
        Upload the Cider Adventure Log spreadsheet export (.xlsx). You'll get a chance to
        review and edit everything before anything is created.
      </p>
      <v-file-input
        v-model="file"
        label="Spreadsheet (.xlsx)"
        accept=".xlsx"
        clearable
      ></v-file-input>
      <v-alert v-if="error" type="error" density="compact" class="mt-2">{{ error }}</v-alert>
    </v-card-text>
    <v-card-actions v-if="step === 'upload'">
      <v-spacer></v-spacer>
      <v-btn variant="text" @click="$emit('close')">Cancel</v-btn>
      <v-btn color="primary" :loading="loading" :disabled="!file" @click="doPreview">
        Preview Import
      </v-btn>
    </v-card-actions>

    <!-- Step 2: preview / edit / map -->
    <v-card-text v-else-if="step === 'preview'" style="max-height: 70vh; overflow-y: auto;">
      <v-alert type="info" density="compact" variant="tonal" class="mb-4">
        {{ summary.total_rows }} rows found &mdash; {{ beverages.length }} beverages,
        {{ summary.rating_count }} ratings<template v-if="summary.rows_without_rating">
          ({{ summary.rows_without_rating }} row{{ summary.rows_without_rating === 1 ? '' : 's' }} had no rating and
          will just create the beverage)</template>.
      </v-alert>

      <p class="font-display text-h6 font-weight-bold mb-2">Map tasters to accounts</p>
      <p class="text-caption text-medium-emphasis mb-3">
        Names left unmapped will have their ratings skipped &mdash; the beverage is still imported either way.
      </p>
      <v-row dense class="mb-4">
        <v-col v-for="name in names" :key="name" cols="12" sm="6">
          <v-select
            v-model="nameMap[name]"
            :items="userOptions"
            :label="name"
            clearable
            density="comfortable"
          ></v-select>
        </v-col>
      </v-row>

      <p class="font-display text-h6 font-weight-bold mb-2">Beverages</p>
      <p class="text-caption text-medium-emphasis mb-3">
        Edit Brand/Name to fix typos or merge near-duplicates &mdash; any two rows you retype to the
        same Brand + Name become one beverage on import.
      </p>
      <v-table density="compact" fixed-header height="360">
        <thead>
          <tr>
            <th style="width: 32%">Brand</th>
            <th style="width: 32%">Name</th>
            <th>Ratings</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(bev, i) in beverages" :key="i">
            <td>
              <v-text-field v-model="bev.brand" density="compact" variant="underlined" hide-details></v-text-field>
            </td>
            <td>
              <v-text-field v-model="bev.name" density="compact" variant="underlined" hide-details></v-text-field>
            </td>
            <td class="font-mono">{{ bev.ratings.length }}</td>
          </tr>
        </tbody>
      </v-table>

      <v-alert v-if="error" type="error" density="compact" class="mt-4">{{ error }}</v-alert>
    </v-card-text>
    <v-card-actions v-if="step === 'preview'">
      <v-btn variant="text" @click="step = 'upload'">Back</v-btn>
      <v-spacer></v-spacer>
      <v-btn variant="text" @click="$emit('close')">Cancel</v-btn>
      <v-btn color="primary" class="font-weight-bold" :loading="loading" @click="doCommit">
        Import {{ beverages.length }} Beverages
      </v-btn>
    </v-card-actions>

    <!-- Step 3: result -->
    <v-card-text v-else-if="step === 'result'">
      <v-alert type="success" variant="tonal">
        Created {{ result.beverages_created }} beverage{{ result.beverages_created === 1 ? '' : 's' }}
        and {{ result.ratings_created }} rating{{ result.ratings_created === 1 ? '' : 's' }}.
        <template v-if="result.ratings_skipped">
          {{ result.ratings_skipped }} rating{{ result.ratings_skipped === 1 ? '' : 's' }} skipped (unmapped taster).
        </template>
      </v-alert>
    </v-card-text>
    <v-card-actions v-if="step === 'result'">
      <v-spacer></v-spacer>
      <v-btn color="primary" @click="$emit('imported')">Done</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { previewImport, commitImport } from "../services/imports";
import { fetchUsers } from "../services/auth";

export default {
  emits: ["close", "imported"],
  data() {
    return {
      step: "upload",
      file: null,
      loading: false,
      error: "",
      beverages: [],
      names: [],
      summary: {},
      nameMap: {},
      users: [],
      result: null,
    };
  },
  computed: {
    userOptions() {
      return this.users.map((u) => ({ title: u.display_name || u.email, value: u.id }));
    },
  },
  async mounted() {
    try {
      this.users = await fetchUsers();
    } catch (error) {
      console.error("Error fetching users:", error);
    }
  },
  methods: {
    async doPreview() {
      if (!this.file) return;
      this.error = "";
      this.loading = true;
      try {
        const data = await previewImport(this.file);
        this.beverages = data.beverages;
        this.names = data.names;
        this.summary = data.summary;
        this.nameMap = {};
        this.step = "preview";
      } catch (error) {
        this.error = error.response?.data?.message || "Failed to preview the spreadsheet.";
      } finally {
        this.loading = false;
      }
    },
    async doCommit() {
      this.error = "";
      this.loading = true;
      try {
        this.result = await commitImport(this.beverages, this.nameMap);
        this.step = "result";
      } catch (error) {
        this.error = error.response?.data?.message || "Import failed.";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
