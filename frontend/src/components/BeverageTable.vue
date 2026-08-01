<template>
  <v-container>
    <v-card>
      <v-card-title class="font-display text-h5 font-weight-bold py-4">
        Beverages
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

      <!-- Beverage Table -->
      <v-data-table
        :headers="headers"
        :items="beverages"
        :search="search"
        item-value="id"
        class="elevation-1"
        dense
        :custom-filter="customFilter"
      >
        <template v-slot:item="{ item }">
          <tr class="clickable-row" @click="selectBeverage(item)">
            <td>{{ item.brand }}</td>
            <td>{{ item.name }}</td>
            <td>
              <v-chip size="small" :color="item.type" variant="flat" class="font-mono text-uppercase" style="letter-spacing: 0.04em; font-size: 0.68rem;">
                {{ typeLabel(item.type) }}
              </v-chip>
            </td>
            <td>
              <div v-if="item.average_rating" class="d-flex align-center">
                <v-rating
                  v-model="item.average_rating"
                  half-increments
                  :size="18"
                  readonly
                  density="compact"
                  color="glow"
                ></v-rating>
                <span class="font-mono font-weight-bold ml-1 text-body-2">{{ item.average_rating.toFixed(1) }}</span>
              </div>
              <span v-else class="text-medium-emphasis">No Ratings</span>
            </td>
            <td>
              <v-btn icon size="x-small" color="error" variant="text" @click.stop="confirmDelete(item)">
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

    <!-- Add Beverage Dialog -->
    <v-dialog v-model="showAddBeverageDialog" max-width="600px">
      <v-card>
        <v-card-title class="font-display text-h6 font-weight-bold">
          Add New Beverage
        </v-card-title>
        <v-card-text>
          <!-- Embed the BeverageForm component -->
          <BeverageForm
            :beverageBrands="beverageBrands"
            :beverageNames="beverageNames"
            @add-beverage="handleAddBeverage"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showAddBeverageDialog = false">
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="400px">
      <v-card>
        <v-card-title class="font-display text-h6 font-weight-bold">Confirm Deletion</v-card-title>
        <v-card-text>
          Are you sure you want to delete this beverage? This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" variant="text" @click="deleteBeverage">Delete</v-btn>
          <v-btn variant="text" @click="showDeleteDialog = false">
            Cancel
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Import Ratings Dialog -->
    <v-dialog v-model="showImportDialog" max-width="800px" persistent>
      <ImportRatings @close="showImportDialog = false" @imported="handleImported" />
    </v-dialog>
  </v-container>
  <!-- Add New Beverage / Import Buttons -->
  <v-btn color="primary" class="font-weight-bold" @click="showAddBeverageDialog = true">
    Add New Beverage
  </v-btn>
  <v-btn variant="outlined" color="primary" class="ml-2" @click="showImportDialog = true">
    Import Ratings
  </v-btn>
</template>

<script>
import BeverageForm from "./BeverageForm.vue";
import ImportRatings from "./ImportRatings.vue";
import Quagga from '@ericblade/quagga2';
import { typeLabel } from "../beverageTypes";

export default {
  components: { BeverageForm, ImportRatings },
  props: {
    beverages: {
      type: Array,
      required: true,
    },
    beverageBrands: {
      type: Array,
      required: true,
    },
    beverageNames: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      search: "",
      showAddBeverageDialog: false,
      showImportDialog: false,
      showDeleteDialog: false,
      beverageToDelete: null,
      showScanner: false,
      isScanning: false,
      scannerError: null,
      lastResult: null,
      headers: [
        { title: "Brand", value: "brand", sortable: true },
        { title: "Name", value: "name", sortable: true },
        { title: "Type", value: "type", sortable: true },
        { title: "Avg. Rating", value: "average_rating", sortable: true },
        { title: "", value: "actions", sortable: false },
      ],
    };
  },
  methods: {
    typeLabel,
    handleAddBeverage(formData) {
      this.$emit("add-beverage", formData);
      this.showAddBeverageDialog = false;
    },
    handleImported() {
      this.showImportDialog = false;
      this.$emit("refresh-beverages");
    },
    selectBeverage(beverage) {
      if (beverage && beverage.id) {
        this.$emit("view-beverage", beverage.id);
      } else {
        console.error("Invalid beverage item:", beverage);
      }
    },
    confirmDelete(beverage) {
      this.beverageToDelete = beverage;
      this.showDeleteDialog = true;
    },
    deleteBeverage() {
      this.$emit("delete-beverage", this.beverageToDelete);
      this.showDeleteDialog = false;
      this.beverageToDelete = null;
    },
    customFilter(value, search, item) {
      if (!search) return true;

      const searchLower = search.toLowerCase();

      const matchesDisplayedFields =
        item.raw.brand.toLowerCase().includes(searchLower) ||
        item.raw.name.toLowerCase().includes(searchLower);

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
  background-color: rgba(var(--v-theme-on-surface), 0.06);
}

.v-data-table-header th {
  color: rgb(var(--v-theme-on-surface)) !important;
  font-weight: 700;
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
