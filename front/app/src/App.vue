<template>
  <div class="app">
    <div class="board" v-if="showBoard">
      <div class="discard-pile" v-if="showDiscardPile">
        <FlashCard v-for="({ recto, verso }, index) in discardCards" :recto="recto" :verso="verso" :key="index"
          :order="index" disabled :show="index == discardCards.length - 1" />
      </div>
      <div class="flash-card-container">
        <FlashCard v-for="({ recto, verso, picture, description }, index) in cards" :recto="recto" :verso="verso" :picture="picture" :description="description"
          :key="index" :order="index" :show="cards.length - index < 10" @success="discard" @fail="discard" />
      </div>
    </div>
    <div class="decks-container" v-if="showDecks">
      <FlashDeck v-if="profilePath.length" name="↩️" @pick="back()" />
      <FlashDeck v-for="({ name }, index) in profiles" :name="name" :key="index" @pick="pickProfile(index)" :disabled="cards.length > 0"/>
      <FlashDeck v-for="({ name, level, size, score }, index) in decks" :name="name" :level="level" :size="size"
        :score="score" :key="index" @pick="pickDeck(index)"
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
      profilePath: [],
      profiles: [],
      decks: [],
      currentDeckIndex: null,
      cards: [],
      discardCards: [],
      state: 0 // 0: Profile/Deck selection, 1: Flash cards
    }
  },
  computed: {
    isMobile() {
      return screen.width <= 760;
    },
    showDecks() {
      return !this.isMobile || this.state === 0;
    },
    showBoard() {
      return !this.isMobile || this.state === 1;
    },
    showDiscardPile() {
      return !this.isMobile;
    }
  },
  methods: {
    discard() {
      this.discardCards.push(this.cards.pop());
      if (this.cards.length === 0) {
        this.state = 0;

        this.fetchProfileAndDecks()
      }
    },
    fetchProfileAndDecks() {
      let profileId = this.profilePath.length ? this.profilePath.slice(-1)[0] : null;

      this.decks = [];
      this.profiles = [];

      if (profileId) {
        axios
        .get(`${process.env.VUE_APP_API_URL}/profiles/${profileId}`)
        .then(res => {
          this.profiles = res.data;
        })
        
        axios
        .get(`${process.env.VUE_APP_API_URL}/decks/${profileId}`)
        .then(res => {
          this.decks = res.data;
        })
      } else {
        axios
        .get(`${process.env.VUE_APP_API_URL}/profiles`)
        .then(res => {
          this.profiles = res.data;
        })
      }
    },
    back() {
      this.cards = [];
      this.profilePath.pop();

      this.fetchProfileAndDecks();
    },
    pickProfile(index) {
      this.profilePath.push(this.profiles[index].id);

      this.fetchProfileAndDecks();
    },
    pickDeck(index) {
      if (this.cards.length) {
        return;
      }

      this.currentDeckIndex = index;
      let deckId = this.decks[index].id;

      axios
        .get(`${process.env.VUE_APP_API_URL}/words/${deckId}`)
        .then(res => {
          this.cards = res.data.reverse();
          this.state = 1;
        })
    }
  },
  mounted() {
    this.fetchProfileAndDecks();
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
  min-width: 80vw;
  padding: 0em 2em;
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
  padding: 0em 1em;
  overflow-y: scroll;
  flex-grow: 1;
}
</style>
