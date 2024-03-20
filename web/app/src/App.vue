<template>
  <div class="app">
    <FlashCard v-for="({ gender, value, translation}, index) in cards" :gender="gender" :value="value" :translation="translation" :key="index" @done="removeCard" />
  </div>
</template>

<script>
import axios from 'axios'
import FlashCard from './components/FlashCard.vue'

export default {
  name: 'App',
  components: {
    FlashCard
  },
  data() {
    return {
      cards: []
    }
  },
  methods: {
    removeCard() {
      this.cards.pop();
    }
  },
  mounted () {
    axios
      .get("http://localhost:5000/words")
      .then(res => {
        this.cards = res.data;
        console.log(res.data[0]);
      })
  }
}
</script>

<style>

body {
  margin: 0;
}

.app {
  width: 100vw;
  height: 100vh;
  background-color: #3f3fb5;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

</style>
