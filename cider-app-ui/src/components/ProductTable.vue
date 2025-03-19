<template>
    <v-container>
      <v-card>
        <v-card-title>
          Product Table
          <v-spacer></v-spacer>
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
            <v-btn color="primary" @click="selectProduct(item)">
              View
            </v-btn>
          </template>
        </v-data-table>
      </v-card>
      <v-spacer></v-spacer>
      <!-- Add New Product Button -->
      <v-btn color="primary" @click="showAddProductDialog = true">
            Add New Product
        </v-btn>
  
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
        headers: [
          { text: "Brand", value: "brand", sortable: true },
          { text: "Flavor", value: "flavor", sortable: true },
          { text: "Barcode", value: "barcode", sortable: true },
          { text: "Description", value: "description", sortable: false },
          { text: "Actions", value: "actions", sortable: false },
        ],
      };
    },
    mounted() {
        console.log("Table | Product Brands:", this.productBrands);
        console.log("Table | Product Flavors:", this.productFlavors);
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
    },
  };
  </script>
  