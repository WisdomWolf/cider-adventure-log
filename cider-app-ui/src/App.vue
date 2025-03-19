<template>
  <v-app>
    <v-container>
      <h1 class="text-center">Cider Adventure Log</h1>
      <ProductTable
        v-if="!selectedProduct"
        :headers="headers"
        :products="products"
        @view-product="fetchProductDetails"
      />
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
import axios from "axios";

export default {
  components: {
    ProductTable,
    ProductDetails,
  },
  data() {
    return {
      headers: [
        { text: "Name", value: "name" },
        { text: "Brand", value: "brand" },
        { text: "Type", value: "type" },
        { text: "Barcode", value: "barcode" },
        { text: "Average Rating", value: "average_rating" },
      ],
      products: [],
      selectedProduct: null,
    };
  },
  methods: {
    async fetchProducts() {
      try {
        const response = await axios.get(`${import.meta.env.VITE_BACKEND_URL}/products`);
        this.products = response.data;
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
        const response = await axios.get(`${import.meta.env.VITE_BACKEND_URL}/products/${productId}`);
        this.selectedProduct = response.data;
      } catch (error) {
        console.error("Error fetching product details:", error);
      }
    },
  },
  mounted() {
    this.fetchProducts();
  },
};
</script>
