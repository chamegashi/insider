<template>
  <div class="text-gray-800">
    <p>test</p>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from '@vue/composition-api';

export default defineComponent({
  setup: () => {
    const msg = ref('Hello!');

    const changeMessage = () => {
      msg.value = 'What\'s up?';
    };

    return {
      msg,
      changeMessage,
    };
  },
});
</script>
