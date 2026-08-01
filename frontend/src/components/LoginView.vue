<template>
  <v-container class="fill-height" style="max-width: 420px">
    <v-card class="w-100" elevation="2">
      <v-card-title class="font-display text-h4 font-weight-bold pt-6 pb-2">Cask &amp; Cup</v-card-title>
      <v-card-subtitle class="pb-4">Log in to your tasting log</v-card-subtitle>
      <v-card-text>
        <v-form @submit.prevent="submit">
          <v-text-field
            v-model="email"
            label="Email"
            type="email"
            autocomplete="username"
            required
          ></v-text-field>
          <v-text-field
            v-model="password"
            label="Password"
            type="password"
            autocomplete="current-password"
            required
          ></v-text-field>
          <v-alert v-if="errorMessage" type="error" density="compact" class="mb-4">
            {{ errorMessage }}
          </v-alert>
          <v-btn type="submit" color="primary" class="font-weight-bold" block :loading="submitting">Log in</v-btn>
        </v-form>

        <template v-if="ssoEnabled">
          <v-divider class="my-4"></v-divider>
          <v-btn href="/api/auth/sso/login" color="primary" variant="outlined" block>Log in with SSO</v-btn>
        </template>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import { fetchAuthConfig, login } from "../services/auth";

export default {
  emits: ["logged-in"],
  data() {
    return {
      email: "",
      password: "",
      errorMessage: "",
      submitting: false,
      ssoEnabled: false,
    };
  },
  async mounted() {
    try {
      const config = await fetchAuthConfig();
      this.ssoEnabled = config.sso_enabled;
    } catch (error) {
      console.error("Error fetching auth config:", error);
    }

    const params = new URLSearchParams(window.location.search);
    if (params.get("error") === "no_account") {
      this.errorMessage = "No account is linked to that SSO identity.";
    }
  },
  methods: {
    async submit() {
      this.errorMessage = "";
      this.submitting = true;
      try {
        const user = await login(this.email, this.password);
        this.$emit("logged-in", user);
      } catch (error) {
        this.errorMessage =
          error.response?.data?.message || "Unable to log in.";
      } finally {
        this.submitting = false;
      }
    },
  },
};
</script>
