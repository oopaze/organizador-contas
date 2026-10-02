const { resolveBabelOptions } = require('jest-expo/src/resolveBabelOptions');

const babelOptions = resolveBabelOptions(process.cwd());

module.exports = {
  preset: 'jest-expo',
  // A primeira renderização com NativeWind neste host leva alguns segundos por worker;
  // o timeout padrão de 5s estoura quando as suítes rodam em paralelo.
  testTimeout: 15000,
  transform: {
    // O preset do jest-expo só transforma .js/.jsx/.ts/.tsx; lucide-react-native publica ESM (.mjs).
    '^.+\\.mjs$': ['babel-jest', babelOptions],
  },
  transformIgnorePatterns: [
    'node_modules/(?!((jest-)?react-native|@react-native(-community)?|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|@sentry/react-native|native-base|react-native-svg|nativewind|lucide-react-native|@gorhom/.*))',
  ],
};
