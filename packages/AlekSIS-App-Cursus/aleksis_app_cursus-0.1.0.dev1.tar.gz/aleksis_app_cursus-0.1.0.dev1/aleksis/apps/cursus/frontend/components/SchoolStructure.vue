<script setup>
import DialogObjectForm from "aleksis.core/components/generic/dialogs/DialogObjectForm.vue";
import CreateButton from "aleksis.core/components/generic/buttons/CreateButton.vue";
import SecondaryActionButton from "aleksis.core/components/generic/buttons/SecondaryActionButton.vue";
import SchoolTermField from "aleksis.core/components/school_term/SchoolTermField.vue";
</script>

<template>
  <v-card>
    <!-- Create grade form -->
    <dialog-object-form
      v-model="createGradeForm"
      :fields="createGradeFields"
      :default-item="createGradeDefaultItem"
      :is-create="true"
      create-item-i18n-key="cursus.school_structure.add_grade"
      :gql-create-mutation="gqlCreateGrades"
      :get-create-data="transformCreateGradeItem"
      @cancel="createGradeForm = false"
      @save="updateSchoolStructure"
    />
    <!-- Create class form -->
    <dialog-object-form
      v-model="createClassForm"
      :fields="createClassFields"
      :default-item="createClassDefaultItem"
      :is-create="true"
      create-item-i18n-key="cursus.school_structure.add_class"
      :gql-create-mutation="gqlCreateClasses"
      :get-create-data="transformCreateClassItemForGrade"
      @cancel="createClassForm = false"
      @save="updateSchoolStructure"
    >
      <!-- Hide parentGroups field - it is set on grade -->
      <!-- eslint-disable-next-line vue/valid-v-slot -->
      <template #parentGroups.field="{ on, attrs }">
        <input type="hidden" v-bind="attrs" v-on="on" />
      </template>
    </dialog-object-form>
    <!-- Title -->
    <div class="d-flex flex-nowrap justify-space-between">
      <div>
        <v-card-title class="text-h4">
          {{ $t("cursus.school_structure.title") }}
        </v-card-title>
      </div>
      <div>
        <school-term-field v-model="currentTerm" return-object required />
      </div>
      <v-spacer />
      <div>
        <v-card-actions>
          <create-button
            v-if="this.$data.currentTerm"
            i18n-key="cursus.school_structure.add_grade"
            @click="createGrade"
          />
        </v-card-actions>
      </div>
    </div>
    <!-- Grades -->
    <v-container v-if="this.$data.currentTerm">
      <v-row class="overflow-x-auto flex-nowrap slide-n-snap-x-container">
        <!-- responsive 1, 2, 3, 4 col layout -->
        <v-col
          v-for="grade in grades"
          :key="grade.id"
          class="slide-n-snap-contained"
          cols="12"
          sm="6"
          md="4"
          lg="3"
          xl="auto"
        >
          <v-card>
            <v-card-title class="justify-end">
              {{ $t("cursus.school_structure.grade") }}
              <span class="ml-3 text-h4">{{ grade.shortName }}</span>
            </v-card-title>
            <v-list
              :max-height="$vuetify.breakpoint.height - 333"
              class="overflow-y-auto slide-n-snap-y-container"
            >
              <!-- class is a "forbidden" name in v-for -->
              <v-list-item
                v-for="clas in grade.childGroups"
                :key="clas.id"
                class="slide-n-snap-contained"
              >
                <v-card class="mx-3 my-2">
                  <div class="d-flex flex-nowrap justify-space-between">
                    <div>
                      <v-card-title class="text-h4">
                        {{ clas.shortName }}
                      </v-card-title>
                      <v-card-subtitle>
                        {{ clas.name }}
                      </v-card-subtitle>
                    </div>
                    <div>
                      <v-chip-group
                        active-class="primary--text"
                        column
                        class="px-2"
                      >
                        <v-chip
                          v-for="teacher in clas.owners"
                          :key="teacher.id"
                          :to="{
                            name: 'core.personById',
                            params: { id: teacher.id },
                          }"
                          :outlined="true"
                        >
                          {{ teacher.shortName }}
                        </v-chip>
                      </v-chip-group>
                      <v-card-actions>
                        <secondary-action-button
                          i18n-key="cursus.school_structure.timetable"
                          :to="{
                            name: 'lesrooster.timetable_management',
                            params: { id: clas.id },
                          }"
                        />
                      </v-card-actions>
                    </div>
                  </div>
                </v-card>
              </v-list-item>
            </v-list>
            <v-card-actions>
              <v-spacer />
              <!-- MAYBE: ADD PLAN COURSES LINK -->
              <create-button
                i18n-key="cursus.school_structure.add_class"
                color="secondary"
                @click="createClass(grade.id)"
              />
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-card>
</template>

<script>
import {
  gqlSchoolGrades,
  gqlCreateGrades,
  gqlCreateClasses,
} from "./schoolStructure.graphql";

export default {
  name: "SchoolStructure",
  data() {
    return {
      createGradeForm: false,
      createGradeFields: [
        {
          text: this.$t("cursus.school_structure.grade_fields.name"),
          value: "name",
        },
        {
          text: this.$t("cursus.school_structure.grade_fields.short_name"),
          value: "shortName",
        },
      ],
      createGradeDefaultItem: {
        name: "",
        shortName: "",
      },
      createClassForm: false,
      createClassFields: [
        {
          text: this.$t("cursus.school_structure.class_fields.name"),
          value: "name",
        },
        {
          text: this.$t("cursus.school_structure.class_fields.short_name"),
          value: "shortName",
        },
        {
          text: "NEVER SHOWN",
          value: "parentGroups",
        },
      ],
      createClassDefaultItem: {
        name: "",
        shortName: "",
        parentGroups: [],
      },
      createClassCurrentGradeID: 0,
      currentTerm: null,
    };
  },
  apollo: {
    grades: {
      query: gqlSchoolGrades,
      variables() {
        return {
          schoolTerm: this.$data.currentTerm.id,
        };
      },
      skip() {
        return !this.$data.currentTerm;
      },
    },
  },
  methods: {
    createGrade() {
      this.$data.createGradeForm = true;
    },
    createClass(id) {
      this.$data.createClassCurrentGradeID = id;
      this.$data.createClassForm = true;
    },
    transformCreateGradeItem(item) {
      return {
        ...item,
        schoolTerm: this.$data.currentTerm.id,
      };
    },
    transformCreateClassItemForGrade(item) {
      return {
        ...item,
        schoolTerm: this.$data.currentTerm.id,
        parentGroups: this.$data.createClassCurrentGradeID,
      };
    },
    updateSchoolStructure() {
      this.$apollo.queries.grades.refetch();
    },
  },
};
</script>

<style>
.slide-n-snap-x-container {
  scroll-snap-type: x mandatory;
  /* scroll-snap-stop: always; */
}
.slide-n-snap-y-container {
  scroll-snap-type: y mandatory;
  /* scroll-snap-stop: always; */
}
.slide-n-snap-contained {
  scroll-snap-align: start;
}
</style>
