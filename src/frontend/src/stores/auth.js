import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from "../api/axios";

export const useAuthStore = defineStore("auth", () => {
  const usuario = ref(null);

  const isLoggedIn = computed(() => !!usuario.value);
  const isAdmin = computed(() => usuario.value?.rol === "admin");

  async function fetchMe() {
    try {
      const { data } = await api.get("/auth/me/");
      usuario.value = data;
    } catch {
      usuario.value = null;
    }
  }

  async function register(payload) {
    const { data } = await api.post("/auth/register/", payload);
    return data;
  }

  async function login(payload) {
    const { data } = await api.post("/auth/login/", payload);

    usuario.value = data;
  }

  async function logout() {
    await api.post("/auth/logout/");
    usuario.value = null;
  }

  return { usuario, isLoggedIn, isAdmin, fetchMe, register, login, logout };
});
