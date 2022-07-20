import { defineConfig } from 'vite'
import path from 'path'
import vue from '@vitejs/plugin-vue'
import eslintPlugin from 'vite-plugin-eslint'
import vueI18n from '@intlify/vite-plugin-vue-i18n'

export default defineConfig({
  define: {
    __VUE_I18N_FULL_INSTALL__: true,
    __VUE_I18N_LEGACY_API__: false,
    __VUE_I18N_PROD_DEVTOOLS__: false,
    __INTLIFY_PROD_DEVTOOLS__: false,
  },
  plugins: [
    vue(),
    eslintPlugin(),
    vueI18n({
      test: /\.(yml)$/, // target json, json5, yaml and yml files
      type: 'javascript/auto',
      loader: '@intlify/vue-i18n-loader',
      // eslint-disable-next-line no-undef
      include: path.resolve(__dirname, './src/locales/**'),
    }),
  ],
})
