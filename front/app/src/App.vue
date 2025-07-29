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
      <FlashDeck name="➕" @pick="createMode()" v-if="showCreationMode"/>
    </div>
    <div class="decks-container" v-if="showCreationPanel">
      <FlashDeck name="↩️" @pick="reset()" />
      <FlashDeck name="Profile" @pick="createProfile()" />
      <FlashDeck name="Deck" @pick="createDeck()" v-if="currentProfileId" />
      <FlashDeck name="Card" @pick="createCard()" v-if="currentDeckIndex != null" />
    </div>
    <FlashOverlay :title="currentQuestion.title" :choices="currentQuestion.choices || []" v-if="currentQuestion" @submit="addFormValue" @cancel="cancelForm()"/>
  </div>
</template>

<script>
import axios from 'axios'
import FlashCard from './components/FlashCard.vue'
import FlashDeck from './components/FlashDeck.vue'
import FlashOverlay from './components/FlashOverlay.vue'

export default {
  name: 'App',
  components: {
    FlashCard,
    FlashDeck,
    FlashOverlay,
  },
  data() {
    return {
      profilePath: [],
      profiles: [],
      decks: [],
      currentDeckIndex: null,
      cards: [],
      discardCards: [],
      formQuestions: [],
      currentQuestion: null,
      formAnswers: [],
      formCallback: () => {},
      state: 0 // 0: Profile/Deck selection, 1: Flash cards, 2: Creation panel
    }
  },
  computed: {
    isMobile() {
      return screen.width <= 760;
    },
    showDecks() {
      if (this.state > 1) return false;

      if (this.isMobile) return this.state === 0;

      return true;
    },
    showBoard() {
      if (this.isMobile) return this.state === 1;

      return true;
    },
    showDiscardPile() {
      return !this.isMobile;
    },
    showCreationMode() {
      return !this.isMobile;
    },
    showCreationPanel() {
      if (this.isMobile) return false;

      return this.state === 2;
    },
    currentProfileId() {
      return this.profilePath.length ? this.profilePath.slice(-1)[0] : null;
    },
  },
  methods: {
    reset() {
      this.state = 0;
      this.currentDeckIndex = null;
      this.fetchProfileAndDecks();
    },
    discard() {
      this.discardCards.push(this.cards.pop());
      if (this.cards.length === 0) {
        this.reset();
      }
    },
    fetchProfileAndDecks() {
      this.decks = [];
      this.profiles = [];

      if (this.currentProfileId) {
        axios
        .get(`${process.env.VUE_APP_API_URL}/profiles/${this.currentProfileId}`)
        .then(res => {
          this.profiles = res.data;
        })
        
        axios
        .get(`${process.env.VUE_APP_API_URL}/decks/${this.currentProfileId}`)
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
    },
    addProfile(name) {
      let url = `${process.env.VUE_APP_API_URL}/profile`;
        if (this.currentProfileId) {
          url = url.concat("/", this.currentProfileId);
        }
        
        let data = {
          name,
        };
        
        return axios.post(url, data)
    },
    addDeck(name, level) {
      let url = `${process.env.VUE_APP_API_URL}/deck/${this.currentProfileId}`;

      let data = {
        name,
        level
      };

      return axios.post(url, data)
    },
    addCard(deckId, recto, verso) {
      let url = `${process.env.VUE_APP_API_URL}/word/${deckId}`;

      let data = {
        recto,
        verso
      };

      return axios.post(url, data)
    },
    createMode() {
      this.state = 2;
    },
    createProfile() {
      this.formQuestions = [
        {
          title: "Profile name ?"
        }
      ];
      
      this.formCallback = () => {
        let name = this.formAnswers.shift();

        this
          .addProfile(name)
          .then(() => {
            this.reset();
          });
      }

      this.nextFormQuestion();
    },
    createDeck() {
      this.formQuestions = [
        {
          title: "Deck name ?"
        },
        {
          title: "Level ?",
          choices: ["easy", "medium", "hard"]
        },
        {
          title: "First card recto ?"
        },
        {
          title: "First card verso ?"
        },
      ];

      this.formCallback = () => {
        let name = this.formAnswers.shift();
        let level = this.formAnswers.shift();
        let recto = this.formAnswers.shift();
        let verso = this.formAnswers.shift();
        
        this
          .addDeck(name, level)
          .then(res => {
            let deckId = res.data.id;            

            this
              .addCard(deckId, recto, verso)
              .then(() => {
                this.reset();
              })
          });
      }

      this.nextFormQuestion();
    },
    createCard() {
      this.formQuestions = [
        {
          title: "Recto ?"
        },
        {
          title: "Verso ?"
        },
      ];
      
      this.formCallback = () => {
        let deckId = this.decks[this.currentDeckIndex].id;
        let recto = this.formAnswers.shift();
        let verso = this.formAnswers.shift();
        
        this
          .addCard(deckId, recto, verso)
          .then(() => {
            this.reset();
          })
      }

      this.nextFormQuestion();
    },
    addFormValue(value) {
      this.formAnswers.push(value);
      this.nextFormQuestion()
    },
    nextFormQuestion() {
      if (this.formQuestions.length === 0) {
        this.formCallback(); 
      }

      this.currentQuestion = this.formQuestions.shift();
    },
    cancelForm() {
      this.currentQuestion = null;
      this.formQuestions = [];
      this.formAnswers = [];
      this.formCallback = () => {};

      this.reset();
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
