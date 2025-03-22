<template>
  <v-container>
    <v-card>
      <v-card-title>
        Product Table
        <v-spacer></v-spacer>
      </v-card-title>
      <v-card-text>
        <!-- Search Input with Barcode Scanner Button -->
        <div class="d-flex align-center">
          <v-text-field
            v-model="search"
            label="Search"
            prepend-inner-icon="mdi-magnify"
            placeholder="Type to filter..."
            single-line
            clearable
            variant="outlined"
            class="flex-grow-1"
          ></v-text-field>
          <v-btn 
            @click="openBarcodeScanner" 
            class="ml-2" 
            color="primary"
            :disabled="isScanning"
          >
            <v-icon left>mdi-barcode-scan</v-icon>
            Scan
          </v-btn>
        </div>
      </v-card-text>

      <!-- Product Table -->
      <v-data-table
        :headers="headers"
        :items="products"
        :search="search"
        item-value="id"
        class="elevation-1"
        dense
        :custom-filter="customFilter"
      >
        <template v-slot:item="{ item }">
          <tr class="clickable-row" @click="selectProduct(item)">
            <td>{{ item.brand }}</td>
            <td>{{ item.flavor }}</td>
            <td>
              <v-rating
                v-if="item.average_rating"
                v-model="item.average_rating"
                half-increments
                :size="20"
                readonly
                dense
                color="yellow"
              ></v-rating>
              <span v-else>No Ratings</span>
            </td>
            <td>
              <v-btn icon size="x-small" color="red" @click.stop="confirmDelete(item)">
                <v-icon>mdi-trash-can</v-icon>
              </v-btn>
            </td>
          </tr>
        </template>
      </v-data-table>
    </v-card>

    <!-- Barcode Scanner Dialog -->
    <v-dialog v-model="showScanner" max-width="600px" @click:outside="closeScanner">
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span>Scan Barcode</span>
          <v-btn icon @click="closeScanner">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <div id="interactive" class="viewport"></div>
          <div v-if="scannerError" class="error-message red--text mt-2">
            {{ scannerError }}
          </div>
          <div v-if="lastResult" class="success-message green--text mt-2">
            Detected: {{ lastResult }}
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Add Product Dialog -->
    <v-dialog v-model="showAddProductDialog" max-width="600px">
      <v-card>
        <v-card-title>
          <span class="text-h6">Add New Product</span>
        </v-card-title>
        <v-card-text>
          <!-- Embed the ProductForm component -->
          <ProductForm
            :productBrands="productBrands"
            :productFlavors="productFlavors"
            @add-product="handleAddProduct"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="showAddProductDialog = false">
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="400px">
      <v-card>
        <v-card-title class="text-h6">Confirm Deletion</v-card-title>
        <v-card-text>
          Are you sure you want to delete this product? This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="red" text @click="deleteProduct">Delete</v-btn>
          <v-btn color="blue darken-1" text @click="showDeleteDialog = false">
            Cancel
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
  <!-- Add New Product Button -->
  <v-btn color="primary" @click="showAddProductDialog = true">
    Add New Product
  </v-btn>
</template>

<script>
import ProductForm from "./ProductForm.vue";
import Quagga from '@ericblade/quagga2';

export default {
  components: { ProductForm },
  props: {
    products: {
      type: Array,
      required: true,
    },
    productBrands: {
      type: Array,
      required: true,
    },
    productFlavors: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      search: "",
      showAddProductDialog: false,
      showDeleteDialog: false,
      productToDelete: null,
      showScanner: false,
      isScanning: false,
      scannerError: null,
      lastResult: null,
      headers: [
        { title: "Brand", value: "brand", sortable: true },
        { title: "Flavor", value: "flavor", sortable: true },
        { title: "Avg. Rating", value: "average_rating", sortable: true },
        { title: "", value: "actions", sortable: false },
      ],
    };
  },
  computed: {
    filteredProducts() {
      return this.products;
    },
  },
  methods: {
    handleAddProduct(formData) {
      this.$emit("add-product", formData);
      this.showAddProductDialog = false;
    },
    selectProduct(product) {
      if (product && product.id) {
        this.$emit("view-product", product.id);
      } else {
        console.error("Invalid product item:", product);
      }
    },
    confirmDelete(product) {
      this.productToDelete = product;
      this.showDeleteDialog = true;
    },
    deleteProduct() {
      this.$emit("delete-product", this.productToDelete);
      this.showDeleteDialog = false;
      this.productToDelete = null;
    },
    customFilter(value, search, item) {
      if (!search) return true;

      const searchLower = search.toLowerCase();

      const matchesDisplayedFields =
        item.raw.brand.toLowerCase().includes(searchLower) ||
        item.raw.flavor.toLowerCase().includes(searchLower);

      const matchesBarcode =
        item.raw.barcodes &&
        item.raw.barcodes.some((barcode) =>
          barcode.code.toLowerCase().includes(searchLower)
        );

      return matchesDisplayedFields || matchesBarcode;
    },
    openBarcodeScanner() {
      this.showScanner = true;
      this.scannerError = null;
      this.lastResult = null;

      this.$nextTick(() => {
        this.initQuagga();
      });
    },
    closeScanner() {
      if (Quagga) {
        Quagga.stop();
      }
      this.showScanner = false;
      this.isScanning = false;
    },
    initQuagga() {
      this.isScanning = true;

      Quagga.init({
        inputStream: {
          type: "LiveStream",
          target: document.querySelector("#interactive"),
          constraints: {
            width: { min: 640 },
            height: { min: 480 },
            facingMode: "environment",
            aspectRatio: { min: 1, max: 2 }
          }
        },
        locator: {
          patchSize: "medium",
          halfSample: true
        },
        numOfWorkers: 4,
        frequency: 10,
        decoder: {
          readers: [
            { format: "upc_reader", config: {} }
          ]
        },
        locate: true
      }, (err) => {
        if (err) {
          this.scannerError = `Camera error: ${err.message || 'Unknown error'}`;
          this.isScanning = false;
          return;
        }

        Quagga.start();
        this.startScanner();
      });
    },
    startScanner() {
      // Process frames for visual feedback
      Quagga.onProcessed((result) => {
        const drawingCtx = Quagga.canvas.ctx.overlay;
        const drawingCanvas = Quagga.canvas.dom.overlay;

        if (result) {
          if (result.boxes) {
            drawingCtx.clearRect(
              0,
              0,
              parseInt(drawingCanvas.getAttribute("width")),
              parseInt(drawingCanvas.getAttribute("height"))
            );
            result.boxes.filter(box => box !== result.box).forEach(box => {
              Quagga.ImageDebug.drawPath(box, { x: 0, y: 1 }, drawingCtx, { color: "green", lineWidth: 2 });
            });
          }

          if (result.box) {
            Quagga.ImageDebug.drawPath(result.box, { x: 0, y: 1 }, drawingCtx, { color: "#00F", lineWidth: 2 });
          }

          if (result.codeResult && result.codeResult.code) {
            Quagga.ImageDebug.drawPath(result.line, { x: 'x', y: 'y' }, drawingCtx, { color: 'red', lineWidth: 3 });
          }
        }
      });

      // Handle successful scans
      Quagga.onDetected((result) => {
        if (result && result.codeResult && result.codeResult.code) {
          this.lastResult = result.codeResult.code;
          this.search = result.codeResult.code;

          // Close scanner after a short delay to show the result
          setTimeout(() => {
            this.closeScanner();
          }, 1000);
        }
      });
    }
  },
  beforeUnmount() {
    if (Quagga) {
      Quagga.stop();
    }
  }
};
</script>

<style>
.clickable-row {
  cursor: pointer;
}

.clickable-row:hover {
  background-color: #f5f5f5;
}

.v-data-table-header th {
  color: black !important;
  font-weight: bold;
}

#interactive {
  position: relative;
  width: 100%;
}

#interactive canvas {
  position: absolute;
  top: 0;
  left: 0;
}

#interactive canvas.drawingBuffer {
  width: 100%;
}

.viewport {
  position: relative;
  width: 100%;
  height: 300px;
  overflow: hidden;
  border: 1px solid #ddd;
  margin-bottom: 10px;
}
</style>
