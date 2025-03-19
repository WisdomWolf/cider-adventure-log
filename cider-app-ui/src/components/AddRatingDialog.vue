<template>
    <v-dialog v-model="internalDialog" max-width="500px">
      <v-card>
        <v-card-title>Add Rating</v-card-title>
        <v-card-text>
          <v-text-field v-model="newRating.user" label="User" required></v-text-field>
          <v-rating v-model="newRating.score" color="amber"></v-rating>
          <v-textarea v-model="newRating.comment" label="Comment"></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" @click="addRating">Submit</v-btn>
          <v-btn text @click="closeDialog">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script>
  export default {
    props: {
      modelValue: {
        type: Boolean,
        required: true,
      },
      newRating: {
        type: Object,
        required: true,
      },
    },
    emits: ["update:modelValue", "add-rating"],
    computed: {
      internalDialog: {
        get() {
          return this.modelValue; // Bind to the parent component's value
        },
        set(value) {
          this.$emit("update:modelValue", value); // Emit the updated value
        },
      },
    },
    methods: {
      addRating() {
        this.$emit("add-rating");
      },
      closeDialog() {
        this.internalDialog = false; // Close the dialog
      },
    },
  };
  </script>
  