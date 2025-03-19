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
        <template v-slot:[`item.average_rating`]="{ item }">
          <v-rating
            v-model="item.average_rating"
            readonly
            dense
            color="amber"
          ></v-rating>
        </template>
      </v-data-table>
    </v-card>
  </template>
  
  <script>
  export default {
    props: {
      headers: Array,
      products: Array,
    },
    methods: {
      refreshProducts() {
        this.$emit("refresh-products");
      },
    },
  };
  </script>
  