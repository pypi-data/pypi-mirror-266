import { hasPersonValidator } from "aleksis.core/routeValidators";

export default {
  component: () => import("aleksis.core/components/Parent.vue"),
  meta: {
    inMenu: true,
    titleKey: "cursus.menu_title",
    icon: "mdi-sign-text",
    validators: [hasPersonValidator],
    permission: "cursus.view_cursus_menu_rule",
  },
  children: [
    {
      path: "subjects/",
      component: () => import("./components/Subject.vue"),
      name: "cursus.subjects",
      meta: {
        inMenu: true,
        titleKey: "cursus.subject.menu_title",
        icon: "mdi-alphabetical-variant",
        permission: "cursus.view_subjects_rule",
      },
    },
    {
      path: "courses/",
      component: () => import("./components/Course.vue"),
      name: "cursus.courses",
      meta: {
        inMenu: true,
        titleKey: "cursus.course.menu_title",
        icon: "mdi-human-male-board",
        permission: "cursus.view_courses_rule",
      },
    },
    {
      path: "school_structure/",
      component: () => import("./components/SchoolStructure.vue"),
      name: "cursus.school_structure",
      meta: {
        inMenu: true,
        titleKey: "cursus.school_structure.menu_title",
        icon: "mdi-table",
        permission: "cursus.manage_school_structure_rule",
      },
    },
  ],
};
