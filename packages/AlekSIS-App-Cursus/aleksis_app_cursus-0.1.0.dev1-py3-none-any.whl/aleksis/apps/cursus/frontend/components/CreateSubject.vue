<script setup>
import ForeignKeyField from "aleksis.core/components/generic/forms/ForeignKeyField.vue";
import ColorField from "aleksis.core/components/generic/forms/ColorField.vue";
</script>
<template>
  <dialog-object-form v-bind="$props" v-on="$listeners">
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #name.field="{ attrs, on, item, setter }">
      <div aria-required="true">
        <v-text-field
          v-bind="attrs"
          v-on="on"
          :rules="rules.name"
          @input="handleNameInput($event, item, setter)"
        />
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #shortName.field="{ attrs, on }">
      <div aria-required="true">
        <v-text-field v-bind="attrs" v-on="on" :rules="rules.shortName" />
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #parent.field="{ attrs, on, item, setter }">
      <foreign-key-field
        v-bind="{ ...$props, ...attrs }"
        :gql-query="gqlQuery"
        v-on="on"
        return-object
        @input="handleParentInput($event, item, setter)"
      >
        <template #createComponent="{ attrs: attrs2, on: on2 }">
          <create-subject
            v-bind="{ ...$props, ...attrs2 }"
            v-on="{ ...$listeners, ...on2 }"
          ></create-subject>
        </template>
      </foreign-key-field>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #colourFg.field="{ attrs, on }">
      <color-field v-bind="attrs" v-on="on" />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #colourBg.field="{ attrs, on }">
      <color-field v-bind="attrs" v-on="on" />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #teachers.field="{ attrs, on }">
      <v-autocomplete
        multiple
        :items="persons"
        item-text="fullName"
        item-value="id"
        v-bind="attrs"
        v-on="on"
        chips
        deletable-chips
        return-object
      >
        <template #item="data">
          <v-list-item-action>
            <v-checkbox v-model="data.attrs.inputValue" />
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>{{ data.item.fullName }}</v-list-item-title>
            <v-list-item-subtitle v-if="data.item.shortName">{{
              data.item.shortName
            }}</v-list-item-subtitle>
          </v-list-item-content>
        </template>
      </v-autocomplete>
    </template>
  </dialog-object-form>
</template>

<script>
import DialogObjectForm from "aleksis.core/components/generic/dialogs/DialogObjectForm.vue";

import { gqlPersons } from "./helper.graphql";

export default {
  name: "CreateSubject",
  extends: DialogObjectForm,
  components: { DialogObjectForm },
  props: {
    gqlQuery: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      rules: {
        name: [
          (name) =>
            (name && name.length > 0) || this.$t("cursus.errors.name_required"),
        ],
        shortName: [
          (name) =>
            (name && name.length > 0) ||
            this.$t("cursus.errors.short_name_required"),
        ],
      },
    };
  },
  apollo: {
    persons: gqlPersons,
  },
  methods: {
    handleParentInput(parentSubject, itemModel, setter) {
      if (!itemModel.colourFg) {
        setter("colourFg", parentSubject.colourFg);
      }
      if (!itemModel.colourBg) {
        setter("colourBg", parentSubject.colourBg);
      }
      if (!itemModel.teachers.length) {
        setter("teachers", parentSubject.teachers);
      }
    },
    handleNameInput(input, itemModel, setter) {
      if (!itemModel.shortName || itemModel.shortName.length < 2) {
        setter("shortName", input.substring(0, 3));
      }
    },
  },
};
</script>

<style scoped></style>
