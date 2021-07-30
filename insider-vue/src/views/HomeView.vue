<template>
  <div class="bg-gray-100 h-screen">
    <p class="text-5xl p-8 text-center">テストインサイダー</p>


    <div class="text-center" v-if="status === 'login'">
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


    <div class="text-center" v-if="status === 'ready'">
      <div class="mb-4">
        <p class="text-xl font-semibold">プレイヤー</p>
        <div v-for="player in players" :key="player.name" class="m-2">
          <p>{{"- " + player.name}}</p>
        </div>
      </div>
      <button class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded" @click="start">
        次へ
      </button>
    </div>


    <div class="text-center" v-if="status === 'start'">
      <div v-if="player.role === 'people'">
        <div class="text-center">
          <p class="text-xl m-1 pt-5">あなたは</p>
          <p class="text-3xl font-bold m-4">庶民</p>
          <p class="text-xl m-1">です</p>
          <p class="text-xl m-1">誰がインサイダーか見極めましょう。</p>
        </div>
      </div>

      <div v-if="player.role === 'insider'">
        <div class="text-center bg-red-700 text-white">
          <p class="text-xl m-1 pt-5">あなたは</p>
          <p class="text-3xl font-bold m-4">インサイダー</p>
          <p class="text-xl m-1">です</p>
          <p class="text-xl m-1">庶民にバレずに正解へと導きましょう。</p>
          <p class="text-xl m-1">お題は</p>
          <p class="text-3xl font-bold m-4 pb-5">{{answer}}</p>
        </div>
      </div>

      <div v-if="player.role === 'master'">
        <div class="text-center bg-gray-800 text-white">
          <p class="text-xl m-1 pt-5">あなたは</p>
          <p class="text-3xl font-bold m-4">マスター</p>
          <p class="text-xl m-1">です</p>
          <p class="text-xl m-1">誰がインサイダーか見極めましょう。</p>
          <p class="text-xl m-1">お題は</p>
          <p class="text-3xl font-bold m-4">{{answer}}</p>
          <button class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded mb-20" @click="vote">
            頑張る
          </button>
        </div>
      </div>
    </div>


    <div class="text-center" v-if="status === 'vote'">
      <div class="flex justify-center m-5">
        <div v-for="player in players" :key="player.name" class="w-1/3 m-4">
          <label>
            <p class="text-xl">{{player.name}}</p>
            <input type="radio" :value="player.name" v-model="selected">
            <p>{{selected}}</p>
          </label>
        </div>
      </div>
      <p class="text-xl">あなたの投票先</p>
      <p class="text-3xl m-3">{{selected}}</p>
      <button v-if="!reserve" class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded m-20" @click="waitResult">
        投票する
      </button>
      <button v-if="reserve" class="bg-gray-700 text-white font-bold py-2 px-4 rounded m-20" disabled>
        投票完了
      </button>
    </div>


    <div class="text-center" v-if="status === 'waitResult'">
      <p class="text-3xl m-5">投票完了！</p>
      <button class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded m-20" @click="result">
        結果を見る
      </button>
    </div>

    <!-- <HelloWorld msg="Welcome to Your Vue.js + TypeScript App"/> -->
  </div>
</template>

<script lang="ts">
import Login from '../components/Login.vue';
import { defineComponent, ref } from '@vue/composition-api';

interface Player {
  name: string;
  status: string;
  role: string;
  vote: string;
}

export default defineComponent({
  components: {
    Login
  },
  setup() {
    const name = ref<string>();
    const players = ref<Player[]>();
    const player = ref<Player>();
    const answer = ref<string>();
    const selected = ref<string>();
    const reserve = ref<boolean>();
    const status = ref<string>("login");

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

    const start = () => {
      const data = {
        status: 'ready'
      }
      ws.send(JSON.stringify(data));
    }

    const vote = () => {
      const data = {
        status: 'start'
      }
      ws.send(JSON.stringify(data));
    }

    const waitResult = () => {
      const data = {
        status: 'vote',
        vote: selected.value
      }
      ws.send(JSON.stringify(data));
    }

    const result = () => {
      const data = {
        status: 'waitResult',
      }
      ws.send(JSON.stringify(data));
    }

    ws.onmessage = (event) => {
      const obj = JSON.parse(event.data)
      if(obj['next_status'] === "ready"){
        status.value = 'ready';
        players.value = obj.data
      }

      if(obj['next_status'] === "start"){
        status.value = 'start';
        player.value = obj.data;
        answer.value = obj.answer;
      }

      if(obj['next_status'] === "vote"){
        status.value = 'vote';
        players.value = obj.data;
        reserve.value = obj.reserve;
      }

      if(obj['next_status'] === "waitResult"){
        status.value = 'waitResult';
      }
    }

    players.value = [
      {
        name: "name1",
        status: "string",
        role: "string",
        vote: "string",
      },
      {
        name: "name2",
        status: "string",
        role: "string",
        vote: "string",
      },
      {
        name: "name3",
        status: "string",
        role: "string",
        vote: "string",
      },
    ]

    return {
      name,
      players,
      player,
      answer,
      selected,
      reserve,
      join,
      start,
      vote,
      waitResult,
      result,
      ws,
      status
    }
  },
});
</script>
