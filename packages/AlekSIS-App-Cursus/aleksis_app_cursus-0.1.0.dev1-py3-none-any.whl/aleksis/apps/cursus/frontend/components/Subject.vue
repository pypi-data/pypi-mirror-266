<script setup>
import InlineCRUDList from "aleksis.core/components/generic/InlineCRUDList.vue";
import ColorField from "aleksis.core/components/generic/forms/ColorField.vue";
import ForeignKeyField from "aleksis.core/components/generic/forms/ForeignKeyField.vue";
import CreateButton from "aleksis.core/components/generic/buttons/CreateButton.vue";
// eslint-disable-next-line no-unused-vars
import CreateSubject from "./CreateSubject.vue";
import SubjectChip from "./SubjectChip.vue";
</script>

<template>
  <inline-c-r-u-d-list
    :headers="headers"
    :i18n-key="i18nKey"
    create-item-i18n-key="cursus.subject.create"
    :gql-query="gqlQuery"
    :gql-create-mutation="gqlCreateMutation"
    :gql-patch-mutation="gqlPatchMutation"
    :gql-delete-mutation="gqlDeleteMutation"
    :default-item="defaultItem"
    :get-create-data="transformCreateData"
    :get-patch-data="transformPatchData"
    filter
  >
    <template #createComponent="{ attrs, on, createMode }">
      <create-button
        color="secondary"
        @click="on.input(true)"
        :disabled="createMode"
      />

      <create-subject v-bind="attrs" v-on="on" />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #name.field="{ attrs, on }">
      <div aria-required="true">
        <v-text-field v-bind="attrs" v-on="on" :rules="rules.name" />
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #shortName.field="{ attrs, on }">
      <div aria-required="true">
        <v-text-field v-bind="attrs" v-on="on" :rules="rules.shortName" />
      </div>
    </template>

    <template #parent="{ item }">
      <subject-chip v-if="item.parent" :subject="item.parent" />
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #parent.field="{ attrs, on }">
      <foreign-key-field
        v-bind="attrs"
        v-on="on"
        :fields="headers"
        :default-item="defaultItem"
        :gql-query="gqlQuery"
        :gql-patch-mutation="gqlPatchMutation"
        :gql-create-mutation="gqlCreateMutation"
        :get-create-data="transformCreateData"
        create-item-i18n-key="cursus.subject.create"
        return-object
      >
        <template #createComponent="{ attrs: attrs2, on: on2 }">
          <create-subject
            v-bind="{ ...$props, ...attrs2 }"
            v-on="{ ...$listeners, ...on2 }"
          ></create-subject>
        </template>
      </foreign-key-field>
    </template>

    <template #name="{ item }">
      <v-chip :color="item.colourBg" :style="{ color: item.colourFg }">{{
        item.name
      }}</v-chip>
    </template>

    <template #colourFg="{ item }">
      <v-chip :color="item.colourFg" outlined>{{ item.colourFg }}</v-chip>
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #colourFg.field="{ attrs, on }">
      <color-field v-bind="attrs" v-on="on" />
    </template>

    <template #colourBg="{ item }">
      <v-chip :color="item.colourBg" outlined>{{ item.colourBg }}</v-chip>
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #colourBg.field="{ attrs, on }">
      <color-field v-bind="attrs" v-on="on" />
    </template>

    <template #teachers="{ item }">
      <v-chip v-for="teacher in item.teachers" :key="teacher.id">{{
        teacher.fullName
      }}</v-chip
      >&nbsp;
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

    <template #filters="{ attrs, on }">
      <v-checkbox
        v-bind="attrs('parent__isnull')"
        v-on="on('parent__isnull')"
        :label="$t('cursus.subject.has_parent')"
        :false-value="null"
        :true-value="false"
      ></v-checkbox>
    </template>
  </inline-c-r-u-d-list>
</template>

<script>
import {
  subjects,
  createSubjects,
  deleteSubjects,
  updateSubjects,
} from "./subject.graphql";

import { gqlPersons } from "./helper.graphql";

export default {
  name: "Subject",
  data() {
    return {
      headers: [
        {
          text: this.$t("cursus.subject.fields.name"),
          value: "name",
        },
        {
          text: this.$t("cursus.subject.fields.short_name"),
          value: "shortName",
        },
        {
          text: this.$t("cursus.subject.fields.parent"),
          value: "parent",
        },
        {
          text: this.$t("cursus.subject.fields.colour_fg"),
          value: "colourFg",
        },
        {
          text: this.$t("cursus.subject.fields.colour_bg"),
          value: "colourBg",
        },
        {
          text: this.$t("cursus.subject.fields.teachers"),
          value: "teachers",
        },
      ],
      i18nKey: "cursus.subject",
      gqlQuery: subjects,
      gqlCreateMutation: createSubjects,
      gqlPatchMutation: updateSubjects,
      gqlDeleteMutation: deleteSubjects,
      defaultItem: {
        name: "",
        shortName: "",
        parent: null,
        colourFg: "",
        colourBg: "",
        teachers: [],
      },
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
  methods: {
    transformPatchData(item) {
      let dto = { id: item.id };
      this.headers.map((header) => {
        if (header.value === "parent") {
          dto["parent"] = item.parent?.id;
        } else if (header.value === "teachers") {
          dto["teachers"] = item.teachers?.map((teacher) => teacher.id);
        } else {
          dto[header.value] = item[header.value];
        }
      });
      return dto;
    },
    transformCreateData(item) {
      return {
        ...item,
        parent: item.parent?.id,
        teachers: item.teachers.map((teacher) => teacher.id),
      };
    },
  },
  apollo: {
    persons: gqlPersons,
  },
};
</script>

<style scoped></style>
