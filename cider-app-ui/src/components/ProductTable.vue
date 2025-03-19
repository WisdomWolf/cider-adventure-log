<template>
    <v-card outlined>
      <v-card-title>Product List</v-card-title>
      <v-data-table
        :headers="headers"
        :items="products"
        item-value="id"
        class="elevation-1"
        dense
      >
        <template v-slot:top>
          <v-toolbar flat>
            <v-toolbar-title>Products</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-btn color="primary" @click="refreshProducts">Refresh</v-btn>
          </v-toolbar>
        </template>
        <template v-slot:item.average_rating="{ item }">
            {{ item.average_rating || "N/A" }}
        </template>
      </v-data-table>
    </v-card>
  </template>
  
  <script>
  export default {
    props: {
        headers: {
            type: Array,
            required: true,
        },
        products: {
            type: Array,
            required: true,
        },
    },
    methods: {
      refreshProducts() {
        this.$emit("refresh-products");
      },
    },
  };
  </script>
  