<template>
    <form @submit.prevent="submitBeverage">
    <!-- Type Select (fixed once editing an existing beverage) -->
    <v-select
      v-model="newBeverage.type"
      :items="typeOptions"
      label="Type"
      :disabled="!!initialBeverage"
      required
    ></v-select>

      <!-- Brand Combo Box -->
    <v-combobox
      v-model="newBeverage.brand"
      :items="beverageBrands"
      label="Brand"
      clearable
      required
    >
      <template #clear>
        <v-icon tabindex="-1" @click="clearField('brand')">mdi-close</v-icon>
      </template>
    </v-combobox>

    <!-- Name Combo Box -->
    <v-combobox
      v-model="newBeverage.name"
      :items="beverageNames"
      label="Name"
      clearable
      required
    >
      <template #clear>
        <v-icon tabindex="-1" @click="clearField('name')">mdi-close</v-icon>
      </template>
    </v-combobox>

    <!-- Type-specific detail fields -->
    <v-text-field
      v-for="field in detailFields"
      :key="field.key"
      v-model="newBeverage.details[field.key]"
      :label="field.label"
      :type="field.type === 'number' ? 'number' : 'text'"
      clearable
    ></v-text-field>

    <!-- Barcode Text Field -->
    <v-text-field
      v-model="newBeverage.barcode"
      label="Barcode (Optional)"
      clearable
    >
      <template #clear>
        <v-icon tabindex="-1" @click="clearField('barcode')">mdi-close</v-icon>
      </template>
    </v-text-field>

    <!-- Description Textarea -->
    <v-textarea
      v-model="newBeverage.description"
      label="Description"
      rows="3"
      clearable
    >
      <template #clear>
        <v-icon tabindex="-1" @click="clearField('description')">mdi-close</v-icon>
      </template>
    </v-textarea>

      <v-radio-group v-model="imageOption" label="Image Source" row>
        <v-radio label="Upload Image" value="upload"></v-radio>
        <v-radio label="Provide Image URL" value="url"></v-radio>
      </v-radio-group>

      <v-file-input
        v-if="imageOption === 'upload'"
        v-model="uploadedImage"
        label="Upload Image"
        accept="image/*"
        clearable
      ></v-file-input>

      <v-text-field
        v-if="imageOption === 'url'"
        v-model="newBeverage.image_url"
        label="Image URL"
        clearable
      ></v-text-field>

      <v-btn type="submit" color="primary" class="font-weight-bold mt-2">{{ initialBeverage ? 'Update Beverage' : 'Add Beverage' }}</v-btn>
    </form>
  </template>

  <script>
  import { BEVERAGE_TYPE_OPTIONS, BEVERAGE_TYPES } from "../beverageTypes";

  export default {
    props: {
      beverageNames: {
        type: Array,
        required: true,
      },
      beverageBrands: {
        type: Array,
        required: true,
      },
      initialBeverage: {
        type: Object,
        default: null,
      },
    },
    data() {
      const details = {};
      if (this.initialBeverage?.details) {
        Object.assign(details, this.initialBeverage.details);
      }
      return {
        typeOptions: BEVERAGE_TYPE_OPTIONS,
        newBeverage: {
          type: this.initialBeverage?.type || "cider",
          brand: this.initialBeverage?.brand || "",
          name: this.initialBeverage?.name || "",
          barcode: this.initialBeverage?.barcode || "",
          description: this.initialBeverage?.description || "",
          image_url: "",
          details,
        },
        imageOption: "upload", // Default to image upload
        uploadedImage: null, // Holds the uploaded image file
      };
    },
    computed: {
      detailFields() {
        return BEVERAGE_TYPES[this.newBeverage.type]?.detailFields || [];
      },
    },
    methods: {
      submitBeverage() {
        const formData = new FormData();

        // Add beverage details to the form data
        formData.append("type", this.newBeverage.type);
        formData.append("brand", this.newBeverage.brand);
        formData.append("name", this.newBeverage.name);
        formData.append("barcode", this.newBeverage.barcode || "");
        formData.append("description", this.newBeverage.description || "");

        for (const field of this.detailFields) {
          const value = this.newBeverage.details[field.key];
          if (value !== undefined && value !== null) {
            formData.append(field.key, value);
          }
        }

        // Add image data based on the selected option
        if (this.imageOption === "upload" && this.uploadedImage) {
          formData.append("image", this.uploadedImage);
        } else if (this.imageOption === "url" && this.newBeverage.image_url) {
          formData.append("image_url", this.newBeverage.image_url);
        }

        // Emit the form data to the parent component
        this.$emit("add-beverage", formData);

        // Reset the form after submission
        this.newBeverage = {
          type: "cider",
          brand: "",
          name: "",
          barcode: "",
          description: "",
          image_url: "",
          details: {},
        };
        this.uploadedImage = null;
        this.imageOption = "upload";
      },
      clearField(field) {
        this.newBeverage[field] = "";
      },
    },
  };
  </script>
