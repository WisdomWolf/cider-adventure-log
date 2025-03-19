<template>
    <v-container>
      <v-card>
        <v-card-title>
          Product Table
          <v-spacer></v-spacer>
          <!-- Add New Product Button -->
          <v-btn color="primary" @click="showAddProductDialog = true">
            Add New Product
          </v-btn>
        </v-card-title>
        <v-card-text>
          <!-- Search Input -->
          <v-text-field
            v-model="search"
            label="Search"
            placeholder="Type to filter..."
            clearable
            outlined
          ></v-text-field>
        </v-card-text>
        <!-- Product Table -->
        <v-data-table
          :headers="headers"
          :items="filteredProducts"
          item-value="id"
          class="elevation-1"
          dense
        >
          <template v-slot:[`item.actions`]="{ item }">
            <!-- View Button -->
            <v-btn icon color="primary" @click="selectProduct(item)">
              <v-icon>mdi-eye</v-icon>
            </v-btn>
            <!-- Delete Button -->
            <v-btn icon color="red" @click="confirmDelete(item)">
              <v-icon>mdi-trash-can</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card>
  
      <!-- Add Product Dialog -->
      <v-dialog v-model="showAddProductDialog" max-width="600px">
        <v-card>
          <v-card-title>
            <span class="text-h6">Add New Product</span>
          </v-card-title>
          <v-card-text>
            <!-- Embed the ProductForm component -->
            <ProductForm
              :productBrands="productBrands"
              :productFlavors="productFlavors"
              @add-product="handleAddProduct"
            />
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="showAddProductDialog = false">
              Close
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
  
      <!-- Delete Confirmation Dialog -->
      <v-dialog v-model="showDeleteDialog" max-width="400px">
        <v-card>
          <v-card-title class="text-h6">Confirm Deletion</v-card-title>
          <v-card-text>
            Are you sure you want to delete this product? This action cannot be undone.
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="red" text @click="deleteProduct">Delete</v-btn>
            <v-btn color="blue darken-1" text @click="showDeleteDialog = false">
              Cancel
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </template>
  
  <script>
  import ProductForm from "./ProductForm.vue";
  
  export default {
    components: { ProductForm },
    props: {
      products: {
        type: Array,
        required: true, // Products are passed from the parent component
      },
      productBrands: {
        type: Array,
        required: true, // Product brands are passed from the parent component
      },
      productFlavors: {
        type: Array,
        required: true, // Product flavors are passed from the parent component
      },
    },
    data() {
      return {
        search: "",
        showAddProductDialog: false, // Controls the visibility of the Add Product dialog
        showDeleteDialog: false, // Controls the visibility of the Delete Confirmation dialog
        productToDelete: null, // Stores the product to be deleted
        headers: [
          { text: "Brand", value: "brand", sortable: true },
          { text: "Flavor", value: "flavor", sortable: true },
          { text: "Barcode", value: "barcode", sortable: true },
          { text: "Description", value: "description", sortable: false },
          { text: "Actions", value: "actions", sortable: false },
        ],
      };
    },
    computed: {
      filteredProducts() {
        // Filter products based on the search input
        const searchLower = this.search.toLowerCase();
        return this.products.filter((product) =>
          Object.values(product).some((value) =>
            String(value).toLowerCase().includes(searchLower)
          )
        );
      },
    },
    methods: {
      handleAddProduct(formData) {
        // Emit the new product data to the parent component
        this.$emit("add-product", formData);
        this.showAddProductDialog = false; // Close the dialog
      },
      selectProduct(product) {
        // Emit the selected product to the parent component
        this.$emit("view-product", product);
      },
      confirmDelete(product) {
        // Open the confirmation dialog and store the product to delete
        this.productToDelete = product;
        this.showDeleteDialog = true;
      },
      deleteProduct() {
        // Emit the delete event to the parent component
        this.$emit("delete-product", this.productToDelete);
        this.showDeleteDialog = false; // Close the confirmation dialog
        this.productToDelete = null; // Reset the product to delete
      },
    },
  };
  </script>
  