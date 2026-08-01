<template>
  <v-app>
    <v-app-bar v-if="authChecked && currentUser" flat color="background">
      <v-container class="d-flex align-center py-0">
        <span class="font-display text-h5 font-weight-bold">Cask &amp; Cup</span>
        <v-spacer></v-spacer>
        <span class="text-body-2 mr-3 text-medium-emphasis d-none d-sm-inline">
          {{ currentUser.display_name || currentUser.email }}
        </span>
        <v-btn
          icon
          variant="text"
          size="small"
          :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          @click="toggleTheme"
        >
          <v-icon>{{ isDark ? "mdi-weather-sunny" : "mdi-weather-night" }}</v-icon>
        </v-btn>
        <v-btn size="small" variant="text" @click="handleLogout">Log out</v-btn>
      </v-container>
    </v-app-bar>

    <v-main>
      <v-container v-if="!authChecked">
        <!-- Waiting on the initial auth check -->
      </v-container>
      <LoginView v-else-if="!currentUser" @logged-in="handleLoggedIn" />
      <v-container v-else>
        <div v-if="!selectedBeverage">
          <v-tabs v-model="selectedType" color="primary" class="mb-4">
            <v-tab v-for="tab in typeTabs" :key="tab.value" :value="tab.value">{{ tab.label }}</v-tab>
          </v-tabs>
          <BeverageTable
            :beverages="beverages"
            :beverageBrands="beverageBrands"
            :beverageNames="beverageNames"
            @add-beverage="addBeverage"
            @view-beverage="fetchBeverageDetails"
            @delete-beverage="deleteBeverage"
          />
        </div>
        <!-- Beverage Details -->
        <BeverageDetails
          v-else
          :beverage="selectedBeverage"
          :beverageBrands="beverageBrands"
          :beverageNames="beverageNames"
          @go-back="selectedBeverage = null"
          @refresh-beverage="fetchBeverageDetails(selectedBeverage.id)"
        />
      </v-container>
    </v-main>

    <v-footer app color="background" class="justify-center text-caption text-medium-emphasis font-mono">
      Built {{ buildDate }}
    </v-footer>
  </v-app>
</template>

<script>
import BeverageTable from "./components/BeverageTable.vue";
import BeverageDetails from "./components/BeverageDetails.vue";
import BeverageForm from "./components/BeverageForm.vue";
import LoginView from "./components/LoginView.vue";
import axios from "./axios";
import { fetchCurrentUser, logout } from "./services/auth";
import { BEVERAGE_TYPE_OPTIONS } from "./beverageTypes";
import { getStoredTheme, setStoredTheme } from "./theme";

export default {
  components: {
    BeverageTable,
    BeverageDetails,
    BeverageForm,
    LoginView,
  },
  data() {
    return {
      typeTabs: [{ value: null, label: "All" }, ...BEVERAGE_TYPE_OPTIONS.map((o) => ({ value: o.value, label: o.title }))],
      selectedType: null,
      beverages: [],
      beverageBrands: [],
      beverageNames: [],
      selectedBeverage: null,
      authChecked: false,
      currentUser: null,
      buildDate: new Date(__BUILD_TIME__).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        timeZoneName: 'short',
      }),
    };
  },
  computed: {
    isDark() {
      return this.$vuetify.theme.global.name === "cellarDark";
    },
  },
  watch: {
    selectedType() {
      this.fetchBeverages();
    },
  },
  methods: {
    toggleTheme() {
      const next = this.isDark ? "cellarLight" : "cellarDark";
      this.$vuetify.theme.global.name = next;
      setStoredTheme(next);
    },
    async handleLoggedIn(user) {
      this.currentUser = user;
      this.fetchBeverages();
    },
    async handleLogout() {
      try {
        await logout();
      } catch (error) {
        console.error("Error logging out:", error);
      }
      this.currentUser = null;
      this.selectedBeverage = null;
    },
    async fetchBeverages() {
      try {
        const params = this.selectedType ? { type: this.selectedType } : {};
        const response = await axios.get(`/api/beverages`, { params });
        const beveragesData = response.data;

        // Populate dropdown options with unique values
        this.beverageBrands = [...new Set(beveragesData.map((b) => b.brand))];
        this.beverageNames = [...new Set(beveragesData.map((b) => b.name))];

        // Update the beverages array
        this.beverages = beveragesData;
      } catch (error) {
        console.error("Error fetching beverages:", error);
      }
    },
    async fetchBeverageDetails(beverageId) {
      if (!beverageId) {
        console.error("Invalid beverage ID:", beverageId);
        return;
      }

      try {
        const response = await axios.get(`/api/beverages/${beverageId}`);
        this.selectedBeverage = response.data;
      } catch (error) {
        console.error("Error fetching beverage details:", error);
      }
    },
    async addBeverage(formData) {
      try {
        await axios.post(`/api/beverages`, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        this.fetchBeverages(); // Refresh the beverage list after adding a new beverage
      } catch (error) {
        console.error("Error adding beverage:", error);
      }
    },
    async deleteBeverage(beverage) {
      try {
        await axios.delete(`/api/beverages/${beverage.id}`);
        this.fetchBeverages(); // Refresh the beverage list after deletion
      } catch (error) {
        console.error("Error deleting beverage:", error);
      }
    },
  },
  async mounted() {
    console.log("Running in", import.meta.env.MODE, "mode.");

    // Follow the system preference live until the user manually picks a theme.
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
      if (!getStoredTheme()) {
        this.$vuetify.theme.global.name = e.matches ? "cellarDark" : "cellarLight";
      }
    });

    try {
      this.currentUser = await fetchCurrentUser();
    } catch (error) {
      console.error("Error checking auth state:", error);
    } finally {
      this.authChecked = true;
    }
    if (this.currentUser) {
      this.fetchBeverages();
    }
  },
};
</script>
