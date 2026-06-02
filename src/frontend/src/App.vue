<script setup>
// solo necesario si usas pinia en algún guard o middleware
import { useAuthStore } from "./stores/auth";
useAuthStore(); // inicia el store si quieres asegurarte de que está listo antes de rutas
</script>

<template>
  <RouterView />
</template>
