import eslintPluginVue from "eslint-plugin-vue";
import eslintPluginAstro from "eslint-plugin-astro";

export default [
  ...eslintPluginVue.configs["flat/recommended"],
  ...eslintPluginAstro.configs.recommended,
  {
    ignores: ["dist/", "node_modules/", ".astro/"],
  },
];
