<template>
  <div class="app">
    <FlashCard v-for="({ gender, value, translation}, index) in cards" :gender="gender" :value="value" :translation="translation" :key="index" :order="index" @success="success" @fail="fail" />
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
      cards: [],
      score: 0
    }
  },
  methods: {
    removeCard() {
      this.cards.pop();
      console.log(this.score);
    },
    success() {
      this.score += 1;
      this.removeCard();
    },
    fail() {
      this.removeCard();
    }
  },
  mounted () {
    axios
      .get("http://localhost:5000/words")
      .then(res => {
        this.cards = res.data.reverse();
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
  background-color: #1F4690;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

</style>
