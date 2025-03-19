<template>
    <v-card class="mb-4" outlined>
      <v-card-title>Manage Products</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="3">
            <v-autocomplete
              v-model="newProduct.name"
              :items="productNames"
              label="Product Name"
              placeholder="Type to search"
              clearable
            ></v-autocomplete>
          </v-col>
          <v-col cols="12" md="3">
            <v-autocomplete
              v-model="newProduct.brand"
              :items="productBrands"
              label="Brand"
              placeholder="Type to search"
              clearable
            ></v-autocomplete>
          </v-col>
          <v-col cols="12" md="3">
            <v-autocomplete
              v-model="newProduct.type"
              :items="productTypes"
              label="Type"
              placeholder="Type to search"
              clearable
            ></v-autocomplete>
          </v-col>
          <v-col cols="12" md="3">
            <v-text-field
              v-model="newProduct.barcode"
              label="Barcode"
              placeholder="Scan or Enter Barcode"
              clearable
            ></v-text-field>
          </v-col>
        </v-row>
        <v-btn color="primary" @click="addProduct">Add Product</v-btn>
      </v-card-text>
    </v-card>
  </template>
  
  <script>
  export default {
    props: {
      productNames: Array,
      productBrands: Array,
      productTypes: Array,
      newProduct: Object,
    },
    methods: {
      addProduct() {
        this.$emit("add-product");
      },
    },
  };
  </script>
  