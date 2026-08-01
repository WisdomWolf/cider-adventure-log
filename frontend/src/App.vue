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
          <v-tabs :model-value="selectedType" color="primary" class="mb-4" @update:model-value="onTabChange">
            <v-tab v-for="tab in typeTabs" :key="tab.value" :value="tab.value">{{ tab.label }}</v-tab>
          </v-tabs>
          <BeverageTable
            :beverages="beverages"
            :beverageBrands="beverageBrands"
            :beverageNames="beverageNames"
            :show-type-column="!selectedType"
            :initial-page="page"
            :initial-items-per-page="itemsPerPage"
            @add-beverage="addBeverage"
            @view-beverage="viewBeverage"
            @delete-beverage="deleteBeverage"
            @refresh-beverages="fetchBeverages"
            @update:page="onPageChange"
            @update:items-per-page="onItemsPerPageChange"
          />
        </div>
        <!-- Beverage Details -->
        <BeverageDetails
          v-else
          :beverage="selectedBeverage"
          :beverageBrands="beverageBrands"
          :beverageNames="beverageNames"
          @go-back="goBack"
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
      page: 1,
      itemsPerPage: 10,
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
  methods: {
    toggleTheme() {
      const next = this.isDark ? "cellarLight" : "cellarDark";
      this.$vuetify.theme.global.name = next;
      setStoredTheme(next);
    },
    async handleLoggedIn(user) {
      this.currentUser = user;
      this.applyStateFromUrl();
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
    onTabChange(newType) {
      this.selectedType = newType;
      this.page = 1;
      this.fetchBeverages();
      this.syncUrl();
    },
    onPageChange(newPage) {
      this.page = newPage;
      this.syncUrl();
    },
    onItemsPerPageChange(newVal) {
      this.itemsPerPage = newVal;
      this.syncUrl();
    },
    async viewBeverage(beverageId) {
      await this.fetchBeverageDetails(beverageId);
      this.syncUrl(true);
    },
    goBack() {
      window.history.back();
    },
    syncUrl(push = false) {
      const params = new URLSearchParams();
      if (this.selectedType) params.set("type", this.selectedType);
      if (this.page > 1) params.set("page", this.page);
      if (this.itemsPerPage !== 10) params.set("perPage", this.itemsPerPage);
      if (this.selectedBeverage) params.set("beverage", this.selectedBeverage.id);
      const query = params.toString();
      const url = window.location.pathname + (query ? `?${query}` : "");
      if (push) {
        window.history.pushState({}, "", url);
      } else {
        window.history.replaceState({}, "", url);
      }
    },
    async applyStateFromUrl() {
      const params = new URLSearchParams(window.location.search);
      this.selectedType = params.get("type") || null;
      this.page = parseInt(params.get("page"), 10) || 1;
      this.itemsPerPage = parseInt(params.get("perPage"), 10) || 10;

      await this.fetchBeverages();

      const beverageId = params.get("beverage");
      if (beverageId) {
        await this.fetchBeverageDetails(Number(beverageId));
      } else {
        this.selectedBeverage = null;
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

    window.addEventListener("popstate", () => {
      if (this.currentUser) {
        this.applyStateFromUrl();
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
      this.applyStateFromUrl();
    }
  },
};
</script>
