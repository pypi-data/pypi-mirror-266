<script setup>
import ForeignKeyField from "aleksis.core/components/generic/forms/ForeignKeyField.vue";
import PositiveSmallIntegerField from "aleksis.core/components/generic/forms/PositiveSmallIntegerField.vue";
// eslint-disable-next-line no-unused-vars
import CreateSubject from "./CreateSubject.vue";
</script>
<template>
  <dialog-object-form v-bind="$props" v-on="$listeners">
    <template #activator="{ on, attrs }">
      <slot name="activator" v-bind="{ on, attrs }" />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #name.field="{ attrs, on }">
      <div aria-required="true">
        <v-text-field v-bind="attrs" v-on="on" :rules="rules.name" />
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #subject.field="{ attrs, on }">
      <div aria-required="true">
        <foreign-key-field
          v-bind="attrs"
          v-on="on"
          :fields="subject.fields"
          :default-item="subject.defaultItem"
          :gql-query="subject.gqlQuery"
          :gql-patch-mutation="{}"
          :gql-create-mutation="subject.gqlCreateMutation"
          :get-create-data="subject.transformCreateData"
          create-item-i18n-key="cursus.subject.create"
          :rules="rules.subject"
          return-object
          required
        >
          <template #createComponent="{ attrs: attrs2, on: on2 }">
            <create-subject v-bind="attrs2" v-on="on2"></create-subject>
          </template>
        </foreign-key-field>
      </div>
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
  </dialog-object-form>
</template>

<script>
import DialogObjectForm from "aleksis.core/components/generic/dialogs/DialogObjectForm.vue";

import { subjects, createSubjects } from "./subject.graphql";

import { gqlGroups, gqlPersons } from "./helper.graphql";

export default {
  name: "CreateCourse",
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
      subject: {
        gqlQuery: subjects,
        gqlCreateMutation: createSubjects,
        transformCreateData(item) {
          return { ...item, parent: item.parent?.id };
        },
        defaultItem: {
          name: "",
          shortName: "",
          parent: null,
          colourFg: "",
          colourBg: "",
        },
        fields: [
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
  apollo: {
    persons: gqlPersons,
    groups: gqlGroups,
  },
};
</script>

<style scoped></style>
