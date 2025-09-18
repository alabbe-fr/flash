<template>
  <div class="app">
    <div class="board" v-if="showBoard">
      <div class="discard-pile" v-if="showDiscardPile">
        <FlashCard v-for="({ recto, verso }, index) in discardCards" :recto="recto" :verso="verso" :key="index"
          :order="index" disabled :show="index == discardCards.length - 1" />
      </div>
      <div class="flash-card-container">
        <FlashCard v-for="({ recto, verso, picture, description, id }, index) in cards" :recto="recto" :verso="verso" :picture="picture" :description="description" :id="id"
          :key="index" :order="index" :show="cards.length - index < 10" @success="discard" @fail="discard" />
      </div>
    </div>
    <div class="decks-container" v-if="showDecks">
      <div class="buttons-container">
        <button @click="pickPrevious()" :disabled="profilePath.length === 0" v-if="cards.length === 0">
          <img src="./assets/back.svg" />
        </button>
        <button @click="pickPrevious()" v-if="cards.length > 0">
          <img src="./assets/cancel.svg" />
        </button>
        <button @click="createProfile()" :disabled="isMobile || cards.length > 0">
          <img src="./assets/new_folder.svg" />
        </button>
        <button @click="createDeck()" :disabled="isMobile || cards.length > 0 || currentProfileId === null">
          <img src="./assets/new_deck.svg" />
        </button>
        <button @click="createCard()" :disabled="isMobile || cards.length === 0">
          <img src="./assets/new_card.svg" />
        </button>
      </div>
      <FlashDeck v-for="({ name }, index) in profiles" :name="name" :key="index" @pick="pickProfile(index)" :disabled="cards.length > 0" :isProfile="true"/>
      <FlashDeck v-for="({ name, level, size, score }, index) in decks" :name="name" :level="level" :size="size"
        :score="score" :key="index" @pick="pickDeck(index)"
        :disabled="cards.length > 0 && index !== currentDeckIndex" :isProfile="false"/>      
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
    }
  },
  computed: {
    isMobile() {
      return screen.width <= 768;
    },
    showDecks() {
      return !this.isMobile || this.cards.length === 0;
    },
    showBoard() {
      return !this.isMobile || this.cards.length > 0;
    },
    showDiscardPile() {
      return !this.isMobile;
    },
    currentProfileId() {
      return this.profilePath.length ? this.profilePath.slice(-1)[0] : null;
    },
  },
  methods: {
    discard() {
      this.discardCards.push(this.cards.pop());
      if (this.cards.length === 0) {
        this.fetchProfileAndDecks();
      }
    },
    fetchProfileAndDecks() {
      this.currentDeckIndex = null;
      this.cards = [];
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
      if (this.cards.length === 0) {
        this.profilePath.pop();
      }

      this.fetchProfileAndDecks();
    },
    forward(profileId) {
      this.profilePath.push(profileId);
      this.fetchProfileAndDecks();
    },
    pickPrevious() {
      if (this.cards.length > 0) {
        history.pushState({profile: this.currentProfileId}, "", "");
      } else {
        history.pushState({profile: this.profilePath[this.profilePath.length - 2]}, "", "")
      }

      this.back();
    },
    pickProfile(index) {
      let profileId = this.profiles[index].id;
      history.pushState({profile: profileId}, "", "");

      this.forward(profileId);
    },
    pickDeck(index) {
      if (this.cards.length) {
        return;
      }
      this.currentDeckIndex = index;
      
      let deckId = this.decks[index].id;
      history.pushState({profile: this.currentProfileId, deck: deckId}, "", "");

      this.fetchDeck(deckId);
    },
    fetchDeck(deckId) {
      axios
        .get(`${process.env.VUE_APP_API_URL}/words/${deckId}`)
        .then(res => {
          this.cards = res.data.reverse();
        });
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

      return axios
        .post(url, data)
        .then(res => res.data.id)
    },
    addCard(deckId, recto, verso) {
      let url = `${process.env.VUE_APP_API_URL}/word/${deckId}`;

      let data = {
        recto,
        verso
      };

      return axios
        .post(url, data)
        .then(res => res.data.id)
    },
    createProfile() {
      this.formQuestions = [
        {
          title: "Category name ?"
        }
      ];
      
      this.formCallback = () => {
        let name = this.formAnswers.shift();

        this
          .addProfile(name)
          .then(() => {
            this.fetchProfileAndDecks();
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
          .then(deckId => {
            this
              .addCard(deckId, recto, verso)
              .then(() => {
                this.fetchProfileAndDecks();
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
          .then(cardId => {
            this.cards.push({
              id: cardId,
              recto,
              verso,
              picture: "",
              description: "",
            });
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

      this.fetchProfileAndDecks();
    },
    handlePopState(event) {
      if (event.state?.deck) {
        this.currentDeckIndex = null;
        this.fetchDeck(event.state?.deck);
        return;
      }

      if (event.state === null || this.profilePath.includes(event.state.profile)) {
        this.back();
        return;
      }

      this.forward(event.state.profile);
    }
  },
  mounted() {
    this.fetchProfileAndDecks();
    window.addEventListener('popstate', this.handlePopState);
  }
}
</script>

<style>
:root {
  --primary-color: #3A5BA0;
  --secondary-color: #0e387a;
  --disable-background-color: #e5e5e5;
  --disable-color: #7b7b7b;
  --disable-border-color: #afafaf;
  
  --deck-font-size: 30px;
  --border-size: 8px;
  --spacing: 10px;
}


@media ((min-width: 768px) and (max-width: 1200px)) {
  :root {
    --deck-font-size: 15px;
    --border-size: 4px;
    --spacing: 5px;
  }
}


body {
  margin: 0;
}

.app {
  width: 100vw;
  height: 100vh;
  background-color: var(--secondary-color);
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  display: flex;
}

.board {
  height: 100%;
  display: flex;
  justify-content: space-evenly;
  align-items: center;
  min-width: 75vw;
  padding: 0 2%;
}

@media ((max-width: 768px)) {
  .board {
    padding: 0 8%;
  }
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
  background-color: var(--primary-color);
  border-radius: 2vh;
}

.decks-container {
  height: 100%;
  padding: 0 var(--spacing);
  overflow-y: scroll;
  flex-grow: 1;
}

.buttons-container {
  margin-top: calc(var(--spacing) * 2);
  display: flex;
  justify-content: space-evenly;

  & button {
    padding: calc(var(--border-size) * 2);
    border-radius: calc(var(--border-size) * 2);
    border-width: var(--border-size);
    cursor: pointer;
    border-color: var(--primary-color);
    width: 22%;
  }

  & button:disabled {
    background-color: var(--disable-background-color);
    color: var(--disable-color);
    border-color: var(--disable-border-color);

    & img {
      filter: grayscale(100%) opacity(0.5);
    }
  }
}

</style>
