<template>
    <form @submit.prevent="submitProduct">
      <!-- Brand Combo Box -->
    <v-combobox
      v-model="newProduct.brand"
      :items="productBrands"
      label="Brand"
      clearable
      required
    >
      <template #clear>
        <v-icon tabindex="-1" @click="clearField('brand')">mdi-close</v-icon>
      </template>
    </v-combobox>

    <!-- Flavor Combo Box -->
    <v-combobox
      v-model="newProduct.flavor"
      :items="productFlavors"
      label="Flavor"
      clearable
      required
    >
      <template #clear>
        <v-icon tabindex="-1" @click="clearField('flavor')">mdi-close</v-icon>
      </template>
    </v-combobox>

    <!-- Barcode Text Field -->
    <v-text-field
      v-model="newProduct.barcode"
      label="Barcode (Optional)"
      clearable
    >
      <template #clear>
        <v-icon tabindex="-1" @click="clearField('barcode')">mdi-close</v-icon>
      </template>
    </v-text-field>

    <!-- Description Textarea -->
    <v-textarea
      v-model="newProduct.description"
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
        v-model="newProduct.image_url"
        label="Image URL"
        clearable
      ></v-text-field>
  
      <v-btn type="submit" color="primary">Add Product</v-btn>
    </form>
  </template>
  
  <script>
  export default {
    props: {
      productFlavors: {
        type: Array,
        required: true,
      },
      productBrands: {
        type: Array,
        required: true,
      },
    },
    data() {
      return {
        newProduct: {
          brand: "",
          flavor: "",
          barcode: "",
          description: "",
          image_url: "",
        },
        imageOption: "upload", // Default to image upload
        uploadedImage: null, // Holds the uploaded image file
        clearIcon: {
            component: {
                functional: true,
                render(h) {
                    return h("span", { attrs: { tabindex: "-1" } }); // Skip clear button in tab order
                }
            }
        }
      };
    },
    methods: {
      submitProduct() {
        const formData = new FormData();
  
        // Add product details to the form data
        formData.append("brand", this.newProduct.brand);
        formData.append("flavor", this.newProduct.flavor);
        formData.append("barcode", this.newProduct.barcode || "");
        formData.append("description", this.newProduct.description || "");
  
        // Add image data based on the selected option
        if (this.imageOption === "upload" && this.uploadedImage) {
          formData.append("image", this.uploadedImage);
        } else if (this.imageOption === "url" && this.newProduct.image_url) {
          formData.append("image_url", this.newProduct.image_url);
        }
  
        // Emit the form data to the parent component
        this.$emit("add-product", formData);
  
        // Reset the form after submission
        this.newProduct = {
          brand: "",
          flavor: "",
          type: "",
          barcode: "",
          description: "",
          image_url: "",
        };
        this.uploadedImage = null;
        this.imageOption = "upload";
      },
    },
  };
  </script>
  