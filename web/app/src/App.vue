<template>
  <div class="app">
    <div class="board">
      <div class="discard-pile">
        <FlashCard v-for="({ gender, value, translation }, index) in discardCards" :gender="gender" :value="value"
          :translation="translation" :key="index" :order="index" disabled />
      </div>
      <div class="flash-card-container">
        <FlashCard v-for="({ gender, value, translation }, index) in cards" :gender="gender" :value="value"
          :translation="translation" :key="index" :order="index" @success="success" @fail="fail" />
      </div>
    </div>
    <div class="decks-container">
      <FlashDeck v-for="({ name }, index) in decks" :name="name" :key="index" @pick="pick(index)"
        :disabled="currentDeckIndex !== null && cards.length > 0 && index !== currentDeckIndex" />
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import FlashCard from './components/FlashCard.vue'
import FlashDeck from './components/FlashDeck.vue'

export default {
  name: 'App',
  components: {
    FlashCard,
    FlashDeck
  },
  data() {
    return {
      decks: [],
      currentDeckIndex: null,
      cards: [],
      discardCards: [],
      score: 0
    }
  },
  methods: {
    success() {
      this.score += 1;
      this.discardCards.push(this.cards.pop());
    },
    fail() {
      this.discardCards.push(this.cards.pop());
    },
    pick(index) {
      if (this.cards.length) {
        return;
      }

      this.currentDeckIndex = index;
      let deckName = this.decks[index].name;

      axios
        .get(`http://localhost:5000/words/${deckName}`)
        .then(res => {
          this.cards = res.data.reverse();
        })
    }
  },
  mounted() {
    axios
      .get("http://localhost:5000/decks")
      .then(res => {
        this.decks = res.data;
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
}

.board {
  display: flex;
  justify-content: space-evenly;
  align-items: center;
  flex-grow: 2;
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

.decks-container {
  height: 100vh;
  width: 30vh;
  padding: 0 1em;
}
</style>
