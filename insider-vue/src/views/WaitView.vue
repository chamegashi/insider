<template>
  <div class="bg-gray-100 h-screen">
    <p class="text-5xl p-8 text-center">テストインサイダー</p>
    <div class="text-center">
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from '@vue/composition-api';
import router from '../router/index'

export default defineComponent({
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
