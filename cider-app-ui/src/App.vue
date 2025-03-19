<template>
  <v-app>
    <v-container>
      <h1 class="text-center">Cider Adventure Log</h1>
      <div v-if="!selectedProduct">
        <!-- Product Table -->
        <ProductTable
          :headers="headers"
          :products="products"
          @view-product="fetchProductDetails"
        />

        <!-- Add Product Form -->
        <ProductForm
          :productBrands="productBrands"
          :productFlavors="productFlavors"
          @add-product="addProduct"
        />
      </div>
      <!-- Product Details -->
      <ProductDetails
        v-else
        :product="selectedProduct"
        @go-back="selectedProduct = null"
      />
    </v-container>
  </v-app>
</template>

<script>
import ProductTable from "./components/ProductTable.vue";
import ProductDetails from "./components/ProductDetails.vue";
import ProductForm from "./components/ProductForm.vue";
import axios from "axios";

export default {
  components: {
    ProductTable,
    ProductDetails,
    ProductForm,
  },
  data() {
    return {
      headers: [
        { text: "Brand", value: "brand" },
        { text: "Flavor", value: "flavor" },
        { text: "Barcode", value: "barcode" },
        { text: "Average Rating", value: "average_rating" },
      ],
      products: [],
      productBrands: [],
      productFlavors: [],
      selectedProduct: null,
    };
  },
  methods: {
    async fetchProducts() {
      try {
        const response = await axios.get(`/products`);
        const productsData = response.data;

        // Populate dropdown options with unique values
        this.productBrands = [...new Set(productsData.map((p) => p.brand))];
        this.productFlavors = [...new Set(productsData.map((p) => p.flavor))];

        // Update the products array
        this.products = productsData;
      } catch (error) {
        console.error("Error fetching products:", error);
      }
    },
    async fetchProductDetails(productId) {
      if (!productId) {
        console.error("Invalid product ID:", productId);
        return;
      }

      try {
        const response = await axios.get(`/products/${productId}`);
        this.selectedProduct = response.data;
      } catch (error) {
        console.error("Error fetching product details:", error);
      }
    },
    async addProduct(formData) {
      try {
        await axios.post(`/products`, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        this.fetchProducts(); // Refresh the product list after adding a new product
      } catch (error) {
        console.error("Error adding product:", error);
      }
    },
  },
  mounted() {
    this.fetchProducts();
  },
};
</script>
