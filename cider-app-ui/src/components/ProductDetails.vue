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
        <v-card-title>{{ product.brand }} - {{ product.flavor }}</v-card-title>
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
        <v-chip
                v-for="(barcode, index) in product.barcodes"
                :key="index"
                close
                @click:close="deleteBarcode(barcode)"
        >
                {{ barcode }}
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
  </template>
  
  <script>
  import axios from "@/axios"; // Use your configured Axios instance

  export default {
    props: {
      product: {
        type: Object,
        required: true,
      },
    },
    data() {
      return {
        showAddRatingDialog: false,
        newRating: {
          score: null,
          comment: "",
        },
        valid: false,
        newBarcode: "",
      };
    },
    methods: {
      async addRating() {
        if (!this.valid) {
          return;
        }
  
        try {
          await axios.post(`/products/${this.product.id}/ratings`, this.newRating);
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
        await axios.post(`/products/${this.product.id}/barcodes`, {
          code: this.newBarcode,
        });
        this.product.barcodes.push(this.newBarcode);
        this.newBarcode = '';
      } catch (error) {
        console.error('Error adding barcode:', error);
      }
    },
    async deleteBarcode(barcode) {
      try {
        const barcodeId = this.product.barcodes.find((b) => b === barcode).id;
        await axios.delete(`/barcodes/${barcodeId}`);
        this.product.barcodes = this.product.barcodes.filter((b) => b !== barcode);
      } catch (error) {
        console.error('Error deleting barcode:', error);
      }
    },
    },
  };
  </script>
  