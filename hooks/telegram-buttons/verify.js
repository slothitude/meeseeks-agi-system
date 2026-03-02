#!/usr/bin/env node

/**
 * Final Verification Script
 * Confirms all components are working correctly
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Telegram Button Hooks System - Final Verification\n');
console.log('=================================================\n');

let allGood = true;

// Check 1: Main helper module exists
console.log('1️⃣  Checking main helper module...');
const helperPath = path.join(__dirname, '..', '..', 'telegram_button_helper.js');
if (fs.existsSync(helperPath)) {
  const stats = fs.statSync(helperPath);
  console.log(`   ✅ telegram_button_helper.js (${(stats.size / 1024).toFixed(2)} KB)`);
} else {
  console.log('   ❌ telegram_button_helper.js NOT FOUND');
  allGood = false;
}

// Check 2: Core files exist
console.log('\n2️⃣  Checking core files...');
const coreFiles = [
  'callback-handler.js',
  'quiz-handler.js',
  'config.json',
  'index.js'
];

coreFiles.forEach(file => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    const stats = fs.statSync(filePath);
    console.log(`   ✅ ${file} (${(stats.size / 1024).toFixed(2)} KB)`);
  } else {
    console.log(`   ❌ ${file} NOT FOUND`);
    allGood = false;
  }
});

// Check 3: Documentation exists
console.log('\n3️⃣  Checking documentation...');
const docFiles = [
  'README.md',
  'SETUP.md',
  'INTEGRATION.md',
  'SUMMARY.md'
];

docFiles.forEach(file => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    const stats = fs.statSync(filePath);
    console.log(`   ✅ ${file} (${(stats.size / 1024).toFixed(2)} KB)`);
  } else {
    console.log(`   ❌ ${file} NOT FOUND`);
    allGood = false;
  }
});

// Check 4: Test suite exists
console.log('\n4️⃣  Checking test suite...');
const testPath = path.join(__dirname, 'test.js');
if (fs.existsSync(testPath)) {
  const stats = fs.statSync(testPath);
  console.log(`   ✅ test.js (${(stats.size / 1024).toFixed(2)} KB)`);
} else {
  console.log('   ❌ test.js NOT FOUND');
  allGood = false;
}

// Check 5: Config is valid JSON
console.log('\n5️⃣  Validating configuration...');
try {
  const configPath = path.join(__dirname, 'config.json');
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  
  if (config.botToken && config.quizzes && config.menus && config.confirmations) {
    console.log('   ✅ config.json is valid');
    console.log(`      - ${Object.keys(config.quizzes).length} quiz questions`);
    console.log(`      - ${Object.keys(config.menus).length} menus`);
    console.log(`      - ${Object.keys(config.confirmations).length} confirmations`);
  } else {
    console.log('   ⚠️  config.json missing required sections');
  }
} catch (error) {
  console.log(`   ❌ config.json invalid: ${error.message}`);
  allGood = false;
}

// Check 6: Module can be loaded
console.log('\n6️⃣  Testing module loading...');
try {
  const TelegramButtonHelper = require('../../telegram_button_helper');
  const helper = new TelegramButtonHelper('test_token');
  
  // Test basic functionality
  const button = helper.createButton('Test', 'test');
  const keyboard = helper.createKeyboard(helper.createRow(button));
  
  if (button.text === 'Test' && keyboard.inline_keyboard) {
    console.log('   ✅ Module loads and works correctly');
  } else {
    console.log('   ❌ Module loaded but functionality broken');
    allGood = false;
  }
} catch (error) {
  console.log(`   ❌ Module load failed: ${error.message}`);
  allGood = false;
}

// Check 7: Package.json
console.log('\n7️⃣  Checking package.json...');
try {
  const pkgPath = path.join(__dirname, 'package.json');
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
  
  if (pkg.name && pkg.version && pkg.main) {
    console.log(`   ✅ package.json valid (${pkg.name} v${pkg.version})`);
  } else {
    console.log('   ⚠️  package.json incomplete');
  }
} catch (error) {
  console.log(`   ❌ package.json invalid: ${error.message}`);
  allGood = false;
}

// Summary
console.log('\n=================================================');
if (allGood) {
  console.log('✅ ALL CHECKS PASSED - System Ready!');
  console.log('\n📚 Next Steps:');
  console.log('   1. Edit config.json with your bot token');
  console.log('   2. Run: node index.js');
  console.log('   3. Send messages with buttons to your bot');
  console.log('\n📖 Documentation:');
  console.log('   - README.md for full documentation');
  console.log('   - SETUP.md for quick start guide');
  console.log('   - INTEGRATION.md for integration examples');
  console.log('\n🧪 Testing:');
  console.log('   Run: node test.js');
} else {
  console.log('❌ SOME CHECKS FAILED - Review errors above');
}
console.log('=================================================\n');

process.exit(allGood ? 0 : 1);
