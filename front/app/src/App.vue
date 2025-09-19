<template>
  <div class="app">
    <div class="board" v-if="!isMobile || hasCards">
      <div class="discard-pile" v-if="!isMobile">
        <FlashCard v-for="({ recto, verso }, index) in discardCards" :recto="recto" :verso="verso" :key="index"
          :order="index" disabled :show="index == discardCards.length - 1" />
      </div>
      <div class="flash-card-container">
        <FlashCard v-for="({ recto, verso, picture, description, id }, index) in cards" :recto="recto" :verso="verso" :picture="picture" :description="description" :id="id"
        :key="index" :order="index" :show="cards.length - index < 10" @success="discard" @fail="discard" />
      </div>
    </div>
    <div class="decks-container" v-if="!isMobile || !hasCards">
      <div class="buttons-container">
        <button @click="selectPrevious()" :disabled="profilePath.length === 0" v-if="!hasCards">
          <img src="./assets/back.svg" />
        </button>
        <button @click="selectCancel()" v-if="hasCards">
          <img src="./assets/cancel.svg" />
        </button>
        <button @click="selectCreateProfile()" :disabled="isMobile || hasCards">
          <img src="./assets/new_folder.svg" />
        </button>
        <button @click="selectCreateDeck()" :disabled="isMobile || hasCards || currentProfileId === null">
          <img src="./assets/new_deck.svg" />
        </button>
        <button @click="selectCreateCard()" :disabled="isMobile || !hasCards">
          <img src="./assets/new_card.svg" />
        </button>
      </div>
      <FlashDeck v-for="({ name }, index) in profiles" :name="name" :key="index" @pick="selectProfile(index)" :disabled="hasCards" :isProfile="true"/>
      <FlashDeck v-for="({ name, level, size, score }, index) in decks" :name="name" :level="level" :size="size"
        :score="score" :key="index" @pick="selectDeck(index)"
        :disabled="hasCards && index !== currentDeckIndex" :isProfile="false"/>
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
    hasCards() {
      return this.cards.length > 0;
    },
    currentProfileId() {
      return this.profilePath.length ? this.profilePath.slice(-1)[0] : null;
    },
  },
  methods: {
    discard() {
      this.discardCards.push(this.cards.pop());
      if (this.cards.length === 0) {
        this.currentDeckIndex = null;

        this.saveHistoryState();
        this.fetchProfilesAndDecks();
      }
    },
    fetchProfilesAndDecks() {
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
    fetchDeck(deckId) {
      this.cards = [];

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

        return axios
          .post(url, data)
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
    selectPrevious() {
      this.profilePath.pop();
      
      this.saveHistoryState();
      this.fetchProfilesAndDecks();
    },
    selectCancel() {
      this.currentDeckIndex = null;
      this.cards = [];

      this.saveHistoryState();
      this.fetchProfilesAndDecks();
    },
    selectProfile(index) {
      let profileId = this.profiles[index].id;
      this.profilePath.push(profileId);

      this.saveHistoryState();
      this.fetchProfilesAndDecks();
    },
    selectDeck(index) {
      if (this.hasCards) {
        return;
      }
      this.currentDeckIndex = index;
      let deckId = this.decks[index].id;
      
      this.saveHistoryState(deckId);
      this.fetchDeck(deckId);
    },
    selectCreateProfile() {
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
            this.fetchProfilesAndDecks();
          });
      }

      this.nextFormQuestion();
    },
    selectCreateDeck() {
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
                this.fetchProfilesAndDecks();
              })
          });
      }

      this.nextFormQuestion();
    },
    selectCreateCard() {
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

      this.fetchProfilesAndDecks();
    },
    saveHistoryState(deckId) {
      if (deckId) {
        history.pushState({profile: this.currentProfileId, deck: deckId}, "", "");
      } else {
        history.pushState({profile: this.currentProfileId}, "", "");
      }
    },
    handlePopState(event) {
      if (event.state?.deck) {
        this.currentDeckIndex = null;

        this.fetchDeck(event.state.deck);
        return;
      }

      if (event.state === null || this.profilePath.includes(event.state.profile)) {
        if (this.hasCards) {
          this.cards = [];
        } else {
          this.profilePath.pop();
        }

        this.fetchProfilesAndDecks();
        return;
      }

      this.profilePath.push(event.state.profile);
      this.fetchProfilesAndDecks();
    }
  },
  mounted() {
    this.fetchProfilesAndDecks();
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
