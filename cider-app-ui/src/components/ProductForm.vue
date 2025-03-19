<template>
    <v-form @submit.prevent="submitProduct">
      <v-combobox
        v-model="newProduct.name"
        :items="productNames"
        label="Product Name"
        clearable
        required
      ></v-combobox>
  
      <v-combobox
        v-model="newProduct.brand"
        :items="productBrands"
        label="Brand"
        clearable
        required
      ></v-combobox>
  
      <v-combobox
        v-model="newProduct.type"
        :items="productTypes"
        label="Type"
        clearable
        required
      ></v-combobox>
  
      <v-text-field
        v-model="newProduct.barcode"
        label="Barcode"
        clearable
        required
      ></v-text-field>
  
      <v-btn type="submit" color="primary">Add Product</v-btn>
    </v-form>
  </template>
  
  <script>
  export default {
    props: {
      productNames: {
        type: Array,
        required: true,
      },
      productBrands: {
        type: Array,
        required: true,
      },
      productTypes: {
        type: Array,
        required: true,
      },
      newProduct: {
        type: Object,
        required: true,
      },
    },
    methods: {
      submitProduct() {
        this.$emit("add-product");
      },
    },
  };
  </script>
  