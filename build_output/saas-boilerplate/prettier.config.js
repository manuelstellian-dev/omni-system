/** @type {import('prettier').Config & import('prettier-plugin-tailwindcss').PluginOptions & import('@ianvs/prettier-plugin-sort-imports').PluginOptions & import('prettier-plugin-prisma').PluginOptions} */
const config = {
  semi: true,
  singleQuote: true,
  printWidth: 100,
  tabWidth: 2,
  trailingComma: 'all',
  arrowParens: 'always',
  importOrder: [
    '^(react/(.*)$)|^(react$)',
    '^(next/(.*)$)|^(next$)',
    '<THIRD_PARTY_MODULES>',
    '',
    '^@/types(.*)$',
    '^@/config(.*)$',
    '^@/lib(.*)$',
    '^@/hooks(.*)$',
    '^@/components(.*)$',
    '^@/app(.*)$',
    '^@/styles(.*)$',
    '^[./]',
  ],
  importOrderParserPlugins: ['typescript', 'jsx', 'decorators-legacy'],
  importOrderTypeScriptVersion: '5.0.0',
  plugins: ['@ianvs/prettier-plugin-sort-imports', 'prettier-plugin-tailwindcss', 'prettier-plugin-prisma'],
};

module.exports = config;