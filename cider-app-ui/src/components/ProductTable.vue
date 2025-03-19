<template>
    <v-data-table
      :headers="headers"
      :items="products"
      class="elevation-1"
    >
      <template v-slot:item="{ item }">
        <tr class="clickable-row" @click="viewProductDetails(item)">
          <td>{{ item.name }}</td>
          <td>{{ item.brand }}</td>
          <td>{{ item.type }}</td>
          <td>{{ item.barcode }}</td>
          <td>
            <v-rating
              v-model="item.average_rating"
              readonly
              color="amber"
              background-color="grey lighten-1"
            ></v-rating>
          </td>
        </tr>
      </template>
    </v-data-table>
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
      viewProductDetails(item) {
        if (item && item.id) {
          this.$emit("view-product", item.id); // Emit the correct product ID
        } else {
          console.error("Invalid product item:", item); // Log the error for debugging
        }
      },
    },
  };
  </script>
  
  <style>
  .clickable-row {
    cursor: pointer;
  }
  .clickable-row:hover {
    background-color: #f5f5f5;
  }
  </style>
  