<template>
  <div class="text-gray-800">
    <div class="text-center">
      <div class="mb-4">
        <label class="block text-gray-700 text-xl font-bold mb-2">
          名前
        </label>
        <input class="shadow appearance-none border rounded w-1/2 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" type="text" placeholder="名前"  v-model="name">
      </div>
      <button class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded" @click="join">
        参加
      </button>
    </div>
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
