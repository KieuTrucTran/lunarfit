<template>
  <div class="size-container">
    <div class="welcome-container">
      <div class="header">
        <q-btn flat dense round icon="arrow_back" to="/settings" />
        <div class="title">{{ $t('language.title') }}</div>
      </div>
      <div class="linie"></div>
      <div class="q-pa-md">
        <q-option-group :options="options" type="radio" v-model="group" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, getCurrentInstance } from 'vue';
import { useI18n } from 'vue-i18n';

export default {
  setup() {
    const { proxy } = getCurrentInstance();
    const i18n = useI18n();

    // Load the locale from localStorage if it exists
    const savedLocale = localStorage.getItem('locale') || i18n.locale.value;
    i18n.locale.value = savedLocale;

    const group = ref(i18n.locale.value);

    const getOptions = () => {
      return [
        { label: i18n.t('language.german'), value: 'de', color: 'primary' },
        { label: i18n.t('language.english'), value: 'en', color: 'primary' },
      ];
    };

    const options = ref(getOptions());

    watch(group, (newLocale) => {
      i18n.locale.value = newLocale;
      // Save the new locale to localStorage
      localStorage.setItem('locale', newLocale);
      options.value = getOptions(); // Update options when language changes
    });

    return {
      group,
      options,
    };
  },
};

</script>

<style scoped>
.welcome-container {
  display: flex;
  flex-direction: column;
  margin: auto;
}

.linie {
  height: 1px;
  background-color: rgba(0, 0, 0, 0.1);
  margin-top: 10px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 10px 0;
}

.title {
  font: 600 20px 'Inter', sans-serif;
  color: #000;
  text-align: center;
  flex-grow: 1;
  padding-right: 30px;
}
</style>
