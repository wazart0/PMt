<template>
  <div class="home">
    <AnyGantt />
  </div>
</template>

<script>
// @ is an alias to /src
import AnyGantt from "@/components/AnyGantt.vue";

export default {
  name: "Home",
  components: {
    AnyGantt,
  },
};
</script>
