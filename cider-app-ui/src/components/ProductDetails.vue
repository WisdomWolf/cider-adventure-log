<template>
    <v-container>
      <v-btn @click="$emit('go-back')" color="primary">Back</v-btn>
      <v-card>
        <!-- Updated logic to load the image -->
        <v-img
          v-if="product.image"
          :src="'data:image/jpeg;base64,' + product.image"
          height="200px"
        ></v-img>
        <v-img
          v-else
          src="https://via.placeholder.com/200" <!-- Placeholder if no image -->
          height="200px"
        ></v-img>
        <v-card-title>{{ product.name }}</v-card-title>
        <v-card-subtitle>{{ product.brand }} - {{ product.type }}</v-card-subtitle>
        <v-card-text>
          <p>{{ product.description }}</p>
          <v-rating
            v-model="product.average_rating"
            readonly
            color="amber"
            background-color="grey lighten-1"
          ></v-rating>
        </v-card-text>
      </v-card>
  
      <v-list>
        <v-subheader>Ratings</v-subheader>
        <v-list-item
          v-for="(rating, index) in product.ratings"
          :key="index"
        >
          <v-list-item-content>
            <v-list-item-title>
              <v-rating
                v-model="rating.score"
                readonly
                color="amber"
                background-color="grey lighten-1"
              ></v-rating>
            </v-list-item-title>
            <v-list-item-subtitle>{{ rating.comment }}</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-container>
  </template>
  
  <script>
  export default {
    props: {
      product: {
        type: Object,
        required: true,
      },
    },
  };
  </script>
  