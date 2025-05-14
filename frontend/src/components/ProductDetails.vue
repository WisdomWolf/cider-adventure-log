<template>
    <v-container>
      <v-btn @click="$emit('go-back')" color="primary">Back</v-btn>
      <v-card>
        <v-img
          v-if="product.image"
          :src="'data:image/jpeg;base64,' + product.image"
          height="200px"
        ></v-img>
        <v-img
          v-else
          src="https://via.placeholder.com/200"
          height="200px"
        ></v-img>
        <v-card-title>
          {{ product.brand }} - {{ product.flavor }}
          <v-spacer></v-spacer>
          <v-btn icon @click="showEditDialog = true">
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <p>{{ product.description }}</p>
          <v-rating
            v-model="product.average_rating"
            readonly
            color="amber"
            background-color="grey lighten-1"
          ></v-rating>
        </v-card-text>
      </v-card>
      <v-chip-group
        v-model="selectedBarcodes"
        multiple
        column
      >
        <v-chip closable
                v-for="(barcode, index) in product.barcodes"
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
        @keyup.enter="addBarcode"
        ></v-text-field>
        <v-btn @click="addBarcode">Add</v-btn>
  
      <v-list>
        <v-subheader>Ratings</v-subheader>
        <v-list-item
          v-for="(rating, index) in product.ratings"
          :key="index"
        >
          <v-list-item-content>
            <v-list-item-title>
              <v-rating
                v-model="rating.score"
                readonly
                color="amber"
                background-color="grey lighten-1"
              ></v-rating>
            </v-list-item-title>
            <v-list-item-subtitle>{{ rating.comment }}</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </v-list>
  
      <!-- Button to open the Add Rating dialog -->
      <v-btn color="primary" @click="showAddRatingDialog = true">Add Rating</v-btn>
  
      <!-- Add Rating Dialog -->
      <v-dialog v-model="showAddRatingDialog" max-width="500px">
        <v-card>
          <v-card-title>Add a New Rating</v-card-title>
          <v-card-text>
            <v-form ref="ratingForm" v-model="valid">
              <v-rating
                v-model="newRating.score"
                color="amber"
                background-color="grey lighten-1"
                label="Rating Score"
                required
              ></v-rating>
              <v-textarea
                v-model="newRating.comment"
                label="Comment"
                rows="3"
                clearable
              ></v-textarea>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" @click="addRating">Submit</v-btn>
            <v-btn text @click="showAddRatingDialog = false">Cancel</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>

    <!-- Edit Product Dialog -->
    <v-dialog v-model="showEditDialog" max-width="600px">
      <v-card>
        <v-card-title>
          <span class="text-h6">Edit Product</span>
        </v-card-title>
        <v-card-text>
          <ProductForm
            :productBrands="productBrands"
            :productFlavors="productFlavors"
            :initialProduct="product"
            @add-product="handleEditProduct"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="showEditDialog = false">
            Cancel
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="errorSnackbar" :timeout="3000" color="red" top>
      {{ errorMessage }}
    </v-snackbar>
  </template>
  
  <script>
  import axios from "@/axios"; // Use your configured Axios instance
  import ProductForm from "./ProductForm.vue";

  export default {
    components: {
      ProductForm
    },
    props: {
      product: {
        type: Object,
        required: true,
      },
      productBrands: {
        type: Array,
        required: true,
      },
      productFlavors: {
        type: Array,
        required: true,
      },
    },
    data() {
      return {
        showAddRatingDialog: false,
        showEditDialog: false,
        newRating: {
          score: null,
          comment: "",
        },
        valid: false,
        newBarcode: "",
        errorSnackbar: false,
        errorMessage: "",
      };
    },
    methods: {
      async addRating() {
        if (!this.valid) {
          return;
        }
  
        try {
          await axios.post(`/api/products/${this.product.id}/ratings`, this.newRating);
          this.$emit("refresh-product"); // Emit an event to refresh the product details
          this.showAddRatingDialog = false; // Close the dialog
          this.newRating = { score: null, comment: "" }; // Reset the form
        } catch (error) {
          console.error("Error adding rating:", error);
        }
      },
      async addBarcode() {
        if (!this.newBarcode.trim()) return;

        try {
          const response = await axios.post(`/api/products/${this.product.id}/barcodes`, {
            code: this.newBarcode,
          });
          this.product.barcodes.push(response.data);
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
        const barcodeId = this.product.barcodes.find((b) => b === barcode).id;
        await axios.delete(`/api/barcodes/${barcodeId}`);
        this.product.barcodes = this.product.barcodes.filter((b) => b !== barcode);
      } catch (error) {
        console.error('Error deleting barcode:', error);
      }
    },
    async handleEditProduct(formData) {
      try {
        await axios.put(`/api/products/${this.product.id}`, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        this.$emit("refresh-product");
        this.showEditDialog = false;
      } catch (error) {
        this.errorMessage = "Error updating product: " + (error.response?.data?.message || error.message);
        this.errorSnackbar = true;
      }
    },
    },
  };
  </script>
  