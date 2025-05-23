<template>
  <v-app>
    <v-container>
      <h1 class="text-center">Cider Adventure Log</h1>
      <div v-if="!selectedProduct">
        <ProductTable
          :products="products"
          :productBrands="productBrands"
          :productFlavors="productFlavors"
          @add-product="addProduct"
          @view-product="fetchProductDetails"
          @delete-product="deleteProduct"
        />
      </div>
      <!-- Product Details -->
      <ProductDetails
        v-else
        :product="selectedProduct"
        :productBrands="productBrands"
        :productFlavors="productFlavors"
        @go-back="selectedProduct = null"
        @refresh-product="fetchProductDetails(selectedProduct.id)"
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
        const response = await axios.get(`/api/products`);
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
        const response = await axios.get(`/api/products/${productId}`);
        this.selectedProduct = response.data;
      } catch (error) {
        console.error("Error fetching product details:", error);
      }
    },
    async addProduct(formData) {
      try {
        await axios.post(`/api/products`, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        this.fetchProducts(); // Refresh the product list after adding a new product
      } catch (error) {
        console.error("Error adding product:", error);
      }
    },
    async deleteProduct(product) {
      try {
        await axios.delete(`/api/products/${product.id}`);
        this.fetchProducts(); // Refresh the product list after deletion
      } catch (error) {
        console.error("Error deleting product:", error);
      }
    },
  },
  mounted() {
    console.log("Running in", import.meta.env.MODE, "mode.");
    this.fetchProducts();
    console.log("App | Product Brands:", this.productBrands);
    console.log("App | Product Flavors:", this.productFlavors);
  },
};
</script>
