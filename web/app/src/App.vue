<template>
  <div class="app">
    <div class="discard-pile">
      <FlashCard v-for="({ gender, value, translation}, index) in successCards" :gender="gender" :value="value" :translation="translation" :key="index" :order="index" disabled/>
    </div>
    <div class="flash-card-container" v-if="cards.length">
      <FlashCard v-for="({ gender, value, translation}, index) in cards" :gender="gender" :value="value" :translation="translation" :key="index" :order="index" @success="success" @fail="fail" />
    </div>
    <div class="discard-pile">
      <FlashCard v-for="({ gender, value, translation}, index) in failedCards" :gender="gender" :value="value" :translation="translation" :key="index" :order="index" disabled/>
    </div>
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
      successCards: [],
      failedCards: [],
      score: 0
    }
  },
  methods: {
    success() {
      this.score += 1;
      this.successCards.push(this.cards.pop());
    },
    fail() {
      this.failedCards.push(this.cards.pop());
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
  background-color: #0e387a;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  display: flex;
  justify-content: space-evenly;
  align-items: center;
}

.flash-card-container {
  position: relative;
  height: 75vh;
  width: 50vh;
}

.discard-pile {
  position: relative;
  height: 45vh;
  width: 30vh;
  background-color: #3A5BA0;
  border-radius: 2vh;
}

</style>
