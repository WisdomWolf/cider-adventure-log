<template>
  <v-app>
    <v-container>
      <h1 class="text-center">Product Scanner</h1>

      <!-- Product Form -->
      <ProductForm
        :productNames="productNames"
        :productBrands="productBrands"
        :productTypes="productTypes"
        :newProduct="newProduct"
        @add-product="addProduct"
      />

      <!-- Product Table -->
      <ProductTable
        :headers="headers"
        :products="products"
        @refresh-products="fetchProducts"
      />

      <!-- Add Rating Dialog -->
      <AddRatingDialog
        v-model="ratingDialog"
        :newRating="newRating"
        @add-rating="addRating"
      />
    </v-container>
  </v-app>
</template>

<script>
import { ref, onMounted } from "vue";
import ProductForm from "./components/ProductForm.vue";
import ProductTable from "./components/ProductTable.vue";
import AddRatingDialog from "./components/AddRatingDialog.vue";
import axios from "axios";

export default {
  components: {
    ProductForm,
    ProductTable,
    AddRatingDialog,
  },
  setup() {
    const products = ref([]);
    const newProduct = ref({ name: "", brand: "", type: "", barcode: "" });
    const newRating = ref({ user: "", score: 0, comment: "" });
    const productNames = ref([]);
    const productBrands = ref([]);
    const productTypes = ref([]);
    const headers = ref([
      { text: "Name", value: "name" },
      { text: "Brand", value: "brand" },
      { text: "Type", value: "type" },
      { text: "Barcode", value: "barcode" },
      { text: "Average Rating", value: "average_rating" },
    ]);
    const ratingDialog = ref(false);

    const fetchProducts = async () => {
      const response = await axios.get("/products");
      products.value = response.data.map(async (product) => {
        const avgRatingResponse = await axios.get(`/products/${product.id}/average-rating`);
        return { ...product, average_rating: avgRatingResponse.data.average_rating };
      });

      productNames.value = [...new Set(response.data.map((p) => p.name))];
      productBrands.value = [...new Set(response.data.map((p) => p.brand))];
      productTypes.value = [...new Set(response.data.map((p) => p.type))];
    };

    const addProduct = async () => {
      await axios.post("/products", newProduct.value);
      newProduct.value = { name: "", brand: "", type: "", barcode: "" };
      fetchProducts();
    };

    const addRating = async () => {
      await axios.post(`/products/${newProduct.value.id}/ratings`, newRating.value);
      newRating.value = { user: "", score: 0, comment: "" };
      ratingDialog.value = false;
      fetchProducts();
    };

    const startPolling = () => {
      setInterval(() => {
        fetchProducts();
      }, 5000);
    };

    onMounted(() => {
      fetchProducts();
      startPolling();
    });

    return {
      products,
      newProduct,
      newRating,
      productNames,
      productBrands,
      productTypes,
      headers,
      ratingDialog,
      fetchProducts,
      addProduct,
      addRating,
    };
  },
};
</script>
