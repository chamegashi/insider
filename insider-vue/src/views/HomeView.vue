<template>
  <div class="bg-gray-100 h-screen">
    <p class="text-5xl p-8 text-center">テストインサイダー</p>
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
    <!-- <HelloWorld msg="Welcome to Your Vue.js + TypeScript App"/> -->
  </div>
</template>

<script lang="ts">
import HelloWorld from '../components/HelloWorld.vue';
import { defineComponent, ref } from '@vue/composition-api';
import router from '../router/index'

export default defineComponent({
  components: {
    HelloWorld
  },
  setup() {
    const name = ref<string>();

    const ws = new WebSocket('ws://localhost:12345');

    const join = () => {
      if(name.value){
        const data = {
          name: name.value,
          status: "login"
        }
        ws.send(JSON.stringify(data));
      }
    }
    
    ws.onmessage = (event) => {
      console.log(event.data)
      const obj = JSON.parse(event.data)
      console.log(obj)
      if(obj['next_status'] === "ready"){
        router.push('/wait')
      }
    }

    return {
      name,
      join,
      ws
    }
  },
});
</script>
