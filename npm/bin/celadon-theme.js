#!/usr/bin/env node
'use strict';

// Prints the location of the shipped theme files. Run via
// `npx -y celadon-theme` or `npm exec celadon-theme`.

const fs = require('node:fs');
const path = require('node:path');

const themesDir = path.join(__dirname, '..', 'themes');

console.log('Celadon Theme files are located in:');
console.log(`  ${themesDir}`);
console.log('');

const themeFiles = fs
  .readdirSync(themesDir)
  .filter((file) => file.endsWith('.json'))
  .sort();

for (const file of themeFiles) {
  console.log(`  - ${file}`);
}

console.log('');
console.log('For installation instructions see INSTRUCTIONS.md in the same package directory.');
