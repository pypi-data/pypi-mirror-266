<script setup>
import InlineCRUDList from "aleksis.core/components/generic/InlineCRUDList.vue";
import PositiveSmallIntegerField from "aleksis.core/components/generic/forms/PositiveSmallIntegerField.vue";
import SubjectChip from "./SubjectChip.vue";
import CreateButton from "aleksis.core/components/generic/buttons/CreateButton.vue";
// eslint-disable-next-line no-unused-vars
import CreateCourse from "./CreateCourse.vue";
import SubjectField from "./SubjectField.vue";
</script>

<template>
  <inline-c-r-u-d-list
    :headers="headers"
    :i18n-key="i18nKey"
    create-item-i18n-key="cursus.course.create"
    :gql-query="gqlQuery"
    :gql-create-mutation="gqlCreateMutation"
    :gql-patch-mutation="gqlPatchMutation"
    :gql-delete-mutation="gqlDeleteMutation"
    :default-item="defaultItem"
    :get-create-data="transformCreateData"
    :get-patch-data="transformPatchData"
  >
    <template #createComponent="{ attrs, on, createMode }">
      <create-button
        color="secondary"
        @click="on.input(true)"
        :disabled="createMode"
      />

      <create-course v-bind="attrs" v-on="on" />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #name.field="{ attrs, on }">
      <div aria-required="true">
        <v-text-field v-bind="attrs" v-on="on" required :rules="rules.name" />
      </div>
    </template>

    <template #subject="{ item }">
      <subject-chip v-if="item.subject" :subject="item.subject" />
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #subject.field="{ attrs, on }">
      <div aria-required="true">
        <subject-field
          v-bind="attrs"
          v-on="on"
          :rules="rules.subject"
          required
        />
      </div>
    </template>

    <template #teachers="{ item }">
      <v-chip v-for="teacher in item.teachers" :key="teacher.id">{{
        teacher.fullName
      }}</v-chip
      >&nbsp;
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #teachers.field="{ attrs, on }">
      <div aria-required="true">
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
          required
          :rules="rules.requiredList"
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
      </div>
    </template>

    <template #groups="{ item }">
      <v-chip v-for="group in item.groups" :key="group.id">{{
        group.name
      }}</v-chip
      >&nbsp;
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #groups.field="{ attrs, on }">
      <div aria-required="true">
        <v-autocomplete
          multiple
          :items="groups"
          item-text="name"
          item-value="id"
          v-bind="attrs"
          v-on="on"
          chips
          deletable-chips
          return-object
          required
          :rules="rules.requiredList"
        />
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #lessonQuota.field="{ attrs, on }">
      <positive-small-integer-field v-bind="attrs" v-on="on" />
    </template>
  </inline-c-r-u-d-list>
</template>

<script>
import {
  courses,
  createCourses,
  deleteCourses,
  updateCourses,
} from "./course.graphql";

import { gqlGroups, gqlPersons } from "./helper.graphql";

export default {
  name: "Course",
  data() {
    return {
      headers: [
        {
          text: this.$t("cursus.course.fields.name"),
          value: "name",
        },
        {
          text: this.$t("cursus.course.fields.subject"),
          value: "subject",
          orderKey: "subject__name",
        },
        {
          text: this.$t("cursus.course.fields.groups"),
          value: "groups",
        },
        {
          text: this.$t("cursus.course.fields.teachers"),
          value: "teachers",
        },
        {
          text: this.$t("cursus.course.fields.lesson_quota"),
          value: "lessonQuota",
        },
      ],
      i18nKey: "cursus.course",
      gqlQuery: courses,
      gqlCreateMutation: createCourses,
      gqlPatchMutation: updateCourses,
      gqlDeleteMutation: deleteCourses,
      defaultItem: {
        name: "",
        subject: null,
        teachers: [],
        groups: [],
        lessonQuota: null,
      },
      rules: {
        name: [
          (name) =>
            (name && name.length > 0) || this.$t("cursus.errors.name_required"),
        ],
        subject: [
          (subject) => !!subject || this.$t("cursus.errors.subject_required"),
        ],
        requiredList: [
          (list) =>
            (!!list && list.length > 0) || this.$t("forms.errors.required"),
        ],
      },
    };
  },
  methods: {
    transformPatchData(item) {
      let dto = { id: item.id };
      this.headers.map((header) => {
        if (header.value === "subject") {
          dto["subject"] = item.subject?.id;
        } else if (header.value === "groups") {
          dto["groups"] = item.groups?.map((group) => group.id);
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
        subject: item.subject?.id || null,
        groups: item.groups.map((group) => group.id),
        teachers: item.teachers.map((teacher) => teacher.id),
      };
    },
  },
  apollo: {
    persons: gqlPersons,
    groups: gqlGroups,
  },
};
</script>

<style scoped></style>
