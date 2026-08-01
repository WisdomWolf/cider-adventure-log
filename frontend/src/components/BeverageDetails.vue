<template>
    <v-container>
      <v-btn @click="$emit('go-back')" color="primary" class="mb-4">Back</v-btn>
      <v-card>
        <v-img
          v-if="beverage.image"
          :src="'data:image/jpeg;base64,' + beverage.image"
          height="200px"
        ></v-img>
        <v-img
          v-else
          height="200px"
          contain
        >
          <img src="@/assets/cider-can.png" alt="Beverage" style="width: 100%; height: 100%; object-fit: contain;" />
        </v-img>
        <v-card-title class="d-flex align-center flex-wrap ga-2 py-4">
          <span class="font-display text-h5 font-weight-bold" style="white-space: normal;">{{ beverage.brand }} — {{ beverage.name }}</span>
          <v-chip size="small" :color="beverage.type" variant="flat" class="font-mono text-uppercase" style="letter-spacing: 0.04em; font-size: 0.68rem;">
            {{ typeLabel(beverage.type) }}
          </v-chip>
          <v-spacer></v-spacer>
          <v-btn icon variant="text" @click="showEditDialog = true">
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <p class="text-body-1">{{ beverage.description }}</p>
          <div v-if="detailFields.length" class="mb-3">
            <div v-for="field in detailFields" :key="field.key" class="text-body-2">
              <span class="text-medium-emphasis">{{ field.label }}:</span>
              <span class="font-mono font-weight-bold">{{ beverage.details?.[field.key] }}</span>
            </div>
          </div>
          <v-rating
            v-model="beverage.average_rating"
            readonly
            color="glow"
          ></v-rating>
        </v-card-text>
      </v-card>
      <v-chip-group
        v-model="selectedBarcodes"
        multiple
        column
      >
        <v-chip closable
                v-for="(barcode, index) in beverage.barcodes"
                :key="index"
                close
                @click:close="deleteBarcode(barcode)"
        >
                {{ barcode.code }}
        </v-chip>
      </v-chip-group>

        <v-text-field
        v-model="newBarcode"
        label="Add Barcode"
        variant="outlined"
        density="compact"
        @keyup.enter="addBarcode"
        ></v-text-field>
        <v-btn color="primary" variant="tonal" @click="addBarcode">Add</v-btn>

      <p class="font-display text-h6 font-weight-bold mt-4 mb-2">Ratings</p>
      <div class="d-flex flex-column ga-3 mb-4">
        <v-card
          v-for="rating in beverage.ratings"
          :key="rating.id"
          variant="elevated"
          elevation="2"
          class="pa-3 clickable-row"
          @click="openRatingView(rating)"
        >
          <div class="d-flex align-center flex-wrap ga-2">
            <v-rating
              v-model="rating.score"
              readonly
              density="compact"
              color="glow"
            ></v-rating>
            <span class="text-caption text-medium-emphasis">
              {{ rating.taster }}<template v-if="rating.created_at"> &middot; {{ formatDate(rating.created_at) }}</template>
            </span>
          </div>
          <p v-if="rating.comment" class="text-body-2 mt-1" style="white-space: normal;">{{ rating.comment }}</p>
          <div v-if="rating.attributes" class="text-caption text-medium-emphasis font-mono">
            <span v-for="field in ratingAttributeFields" :key="field.key">
              <template v-if="rating.attributes[field.key]">
                {{ field.label }}: {{ rating.attributes[field.key] }}&nbsp;&nbsp;
              </template>
            </span>
          </div>
        </v-card>
      </div>

      <!-- Button to open the Add Rating dialog -->
      <v-btn color="primary" class="font-weight-bold" @click="openAddRating">Add Rating</v-btn>

      <!-- View/Add/Edit Rating Dialog -->
      <v-dialog v-model="showRatingDialog" max-width="500px" :persistent="isEditingRating">
        <v-card>
          <v-card-title class="d-flex align-center justify-space-between font-display text-h6 font-weight-bold">
            <span>{{ ratingDialogTitle }}</span>
            <v-btn icon size="small" variant="text" @click="closeRatingDialog">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-form v-if="isEditingRating" ref="ratingForm" v-model="valid">
              <v-rating
                v-model="newRating.score"
                color="glow"
                label="Rating Score"
                required
              ></v-rating>
              <v-textarea
                v-model="newRating.comment"
                label="Comment"
                rows="3"
                clearable
              ></v-textarea>
              <v-text-field
                v-for="field in ratingAttributeFields"
                :key="field.key"
                v-model="newRating.attributes[field.key]"
                :label="field.label"
                :type="field.type === 'number' ? 'number' : 'text'"
                clearable
              ></v-text-field>
            </v-form>
            <div v-else>
              <div class="d-flex align-center flex-wrap ga-2 mb-2">
                <v-rating
                  :model-value="newRating.score"
                  readonly
                  density="compact"
                  color="glow"
                ></v-rating>
                <span class="text-caption text-medium-emphasis">
                  {{ newRating.taster }}<template v-if="newRating.created_at"> &middot; {{ formatDate(newRating.created_at) }}</template>
                </span>
              </div>
              <p v-if="newRating.comment" class="text-body-2" style="white-space: normal;">{{ newRating.comment }}</p>
              <div class="text-caption text-medium-emphasis font-mono">
                <span v-for="field in ratingAttributeFields" :key="field.key">
                  <template v-if="newRating.attributes[field.key]">
                    {{ field.label }}: {{ newRating.attributes[field.key] }}&nbsp;&nbsp;
                  </template>
                </span>
              </div>
            </div>
          </v-card-text>
          <v-card-actions>
            <template v-if="isEditingRating">
              <v-btn v-if="editingRatingId" color="error" variant="text" @click="confirmDeleteFromEdit">Delete</v-btn>
              <v-spacer></v-spacer>
              <v-btn variant="text" @click="closeRatingDialog">Cancel</v-btn>
              <v-btn color="primary" @click="submitRating">Submit</v-btn>
            </template>
            <template v-else>
              <v-spacer></v-spacer>
              <v-btn color="primary" @click="isEditingRating = true">Edit</v-btn>
            </template>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Delete Rating Confirmation Dialog -->
      <v-dialog v-model="showDeleteRatingDialog" max-width="400px">
        <v-card>
          <v-card-title class="font-display text-h6 font-weight-bold">Delete Rating</v-card-title>
          <v-card-text>
            Are you sure you want to delete this rating? This action cannot be undone.
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="error" variant="text" @click="deleteRating">Delete</v-btn>
            <v-btn variant="text" @click="showDeleteRatingDialog = false">Cancel</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>

    <!-- Edit Beverage Dialog -->
    <v-dialog v-model="showEditDialog" max-width="600px">
      <v-card>
        <v-card-title class="font-display text-h6 font-weight-bold">
          Edit Beverage
        </v-card-title>
        <v-card-text>
          <BeverageForm
            :beverageBrands="beverageBrands"
            :beverageNames="beverageNames"
            :initialBeverage="beverage"
            @add-beverage="handleEditBeverage"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showEditDialog = false">
            Cancel
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="errorSnackbar" :timeout="3000" color="error" location="top">
      {{ errorMessage }}
    </v-snackbar>
  </template>

  <script>
  import axios from "@/axios";
  import BeverageForm from "./BeverageForm.vue";
  import { BEVERAGE_TYPES, typeLabel } from "../beverageTypes";

  export default {
    components: {
      BeverageForm
    },
    props: {
      beverage: {
        type: Object,
        required: true,
      },
      beverageBrands: {
        type: Array,
        required: true,
      },
      beverageNames: {
        type: Array,
        required: true,
      },
    },
    data() {
      return {
        showRatingDialog: false,
        isEditingRating: false,
        showEditDialog: false,
        showDeleteRatingDialog: false,
        editingRatingId: null,
        ratingToDelete: null,
        newRating: {
          score: null,
          comment: "",
          attributes: {},
          taster: null,
          created_at: null,
        },
        valid: false,
        newBarcode: "",
        errorSnackbar: false,
        errorMessage: "",
      };
    },
    computed: {
      detailFields() {
        return BEVERAGE_TYPES[this.beverage.type]?.detailFields || [];
      },
      ratingAttributeFields() {
        return BEVERAGE_TYPES[this.beverage.type]?.ratingAttributeFields || [];
      },
      ratingDialogTitle() {
        if (!this.isEditingRating) return "Rating";
        return this.editingRatingId ? "Edit Rating" : "Add a New Rating";
      },
    },
    methods: {
      typeLabel,
      formatDate(isoString) {
        return new Date(isoString).toLocaleDateString(undefined, {
          year: "numeric",
          month: "short",
          day: "numeric",
        });
      },
      openAddRating() {
        this.editingRatingId = null;
        this.newRating = { score: null, comment: "", attributes: {}, taster: null, created_at: null };
        this.isEditingRating = true;
        this.showRatingDialog = true;
      },
      openRatingView(rating) {
        this.editingRatingId = rating.id;
        this.newRating = {
          score: rating.score,
          comment: rating.comment || "",
          attributes: { ...(rating.attributes || {}) },
          taster: rating.taster,
          created_at: rating.created_at,
        };
        this.isEditingRating = false;
        this.showRatingDialog = true;
      },
      closeRatingDialog() {
        this.showRatingDialog = false;
        this.isEditingRating = false;
        this.editingRatingId = null;
      },
      async submitRating() {
        if (!this.valid) {
          return;
        }

        try {
          if (this.editingRatingId) {
            await axios.put(`/api/ratings/${this.editingRatingId}`, this.newRating);
          } else {
            await axios.post(`/api/beverages/${this.beverage.id}/ratings`, this.newRating);
          }
          this.$emit("refresh-beverage"); // Emit an event to refresh the beverage details
          this.closeRatingDialog();
        } catch (error) {
          console.error("Error saving rating:", error);
        }
      },
      confirmDeleteFromEdit() {
        this.ratingToDelete = { id: this.editingRatingId };
        this.showRatingDialog = false;
        this.showDeleteRatingDialog = true;
      },
      async deleteRating() {
        if (!this.ratingToDelete) return;

        try {
          await axios.delete(`/api/ratings/${this.ratingToDelete.id}`);
          this.$emit("refresh-beverage");
        } catch (error) {
          console.error("Error deleting rating:", error);
        } finally {
          this.showDeleteRatingDialog = false;
          this.ratingToDelete = null;
        }
      },
      async addBarcode() {
        if (!this.newBarcode.trim()) return;

        try {
          const response = await axios.post(`/api/beverages/${this.beverage.id}/barcodes`, {
            code: this.newBarcode,
          });
          this.beverage.barcodes.push(response.data);
          this.newBarcode = '';
        } catch (error) {
          if (error.response && error.response.data.error) {
            this.errorMessage = error.response.data.error;
            this.errorSnackbar = true;
          } else {
            console.error('An unexpected error occurred:', error);
          }
        }
    },
    async deleteBarcode(barcode) {
      try {
        const barcodeId = this.beverage.barcodes.find((b) => b === barcode).id;
        await axios.delete(`/api/barcodes/${barcodeId}`);
        this.beverage.barcodes = this.beverage.barcodes.filter((b) => b !== barcode);
      } catch (error) {
        console.error('Error deleting barcode:', error);
      }
    },
    async handleEditBeverage(formData) {
      try {
        await axios.put(`/api/beverages/${this.beverage.id}`, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        this.$emit("refresh-beverage");
        this.showEditDialog = false;
      } catch (error) {
        this.errorMessage = "Error updating beverage: " + (error.response?.data?.message || error.message);
        this.errorSnackbar = true;
      }
    },
    },
  };
  </script>
