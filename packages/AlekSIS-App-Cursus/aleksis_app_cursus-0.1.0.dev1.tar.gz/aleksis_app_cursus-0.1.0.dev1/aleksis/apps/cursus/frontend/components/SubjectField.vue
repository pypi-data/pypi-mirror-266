<script setup>
import ForeignKeyField from "aleksis.core/components/generic/forms/ForeignKeyField.vue";
// eslint-disable-next-line no-unused-vars
import CreateSubject from "./CreateSubject.vue";
import SubjectChip from "./SubjectChip.vue";
</script>

<template>
  <foreign-key-field
    v-bind="$attrs"
    v-on="$listeners"
    :fields="headers"
    create-item-i18n-key="cursus.subject.create"
    :gql-query="gqlQuery"
    :gql-create-mutation="gqlCreateMutation"
    :gql-patch-mutation="{}"
    :default-item="defaultItem"
    :get-create-data="getCreateData"
    :get-patch-data="getPatchData"
    return-object
  >
    <template #item="{ item }">
      <subject-chip :subject="item" />
    </template>
    <template #createComponent="{ attrs, on, createMode }">
      <create-subject v-bind="attrs" v-on="on" />
    </template>
  </foreign-key-field>
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
  name: "SubjectField",
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
    };
  },
  methods: {
    getPatchData(items, headers) {
      return items.map((item) => {
        let dto = {};
        headers.map((header) => {
          if (header.value === "parent") {
            dto["parent"] = item.parent?.id;
          } else if (header.value === "teachers") {
            dto["teachers"] = item.teachers.map((teacher) => teacher.id);
          } else {
            dto[header.value] = item[header.value];
          }
        });
        return dto;
      });
    },
    getCreateData(item) {
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
