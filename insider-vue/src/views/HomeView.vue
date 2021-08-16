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


    <div class="text-center" v-if="status === 'result'">
      <p class="text-3xl m-5">結果発表</p>
      <div v-if="gameResult" class="pb-8">
        <p class="text-3xl m-5 p-4 text-blue-700">庶民側の勝利！</p>
        <div v-for="player in players" :key="player.name">
          <p class="text-xl m-2">
            <span v-if="player.role === 'master'" >(マスター) </span>
            <span v-if="player.role === 'insider'" >(インサイダー) </span>
            {{player.name + " => " + player.voted}}</p>
        </div>
      </div>
      <div v-else class="bg-red-700 text-white pb-8">
        <p class="text-3xl m-5 p-4">インサイダーの勝利！</p>
        <div v-for="player in players" :key="player.name">
          <p class="text-xl m-2">
            <span v-if="player.role === 'master'" >(マスター) </span>
            <span v-if="player.role === 'insider'" >(インサイダー) </span>
            {{player.name + " => " + player.voted}}</p>
        </div>
      </div>
      <button class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded m-10" @click="restart">
        もう一回する！
      </button>
    </div>

  </div>
</template>

<script lang="ts">
import Login from '../components/Login.vue';
import { defineComponent, ref } from '@vue/composition-api';

interface Player {
  name: string;
  status: string;
  role: string;
  voted: string;
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
    const gameResult = ref<boolean>();
    const status = ref<string>("login");

    const ws = new WebSocket('wss://87422686d3d4.ngrok.io');

    const join = () => {
      if(name.value){
        const data = {
          name: name.value,
          status: "login"
        }
        ws.send(JSON.stringify(data));
      }
    }

    setInterval(() => {
      console.log("done")
      const data = {
        status: 'interval'
      }
      ws.send(JSON.stringify(data));
    }, 60000);

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

    const restart = () => {
      const data = {
        status: 'restart',
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

      if(obj['next_status'] === "result"){
        status.value = 'result';
        players.value = obj.data;
        gameResult.value = obj.result;
      }
}

    return {
      name,
      players,
      player,
      answer,
      selected,
      reserve,
      gameResult,
      join,
      start,
      vote,
      waitResult,
      result,
      restart,
      ws,
      status
    }
  },
});
</script>
