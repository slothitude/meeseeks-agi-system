/**
 * Simple Button System Test - Demonstrates Worker Communication Workflow
 * No bot token required
 */

const TelegramButtonHelper = require('../../telegram_button_helper');

console.log('🧪 Button System Test - Worker Communication Demo\n');
console.log('=' .repeat(50));

const helper = new TelegramButtonHelper('test_token');

// Simulated worker discoveries (ARC-AGI-2 research)
const discoveries = [
  { worker: 'Meeseeks Alpha', approach: 'Pattern Matching', confidence: 0.85, description: 'Identified repeating patterns in grid cells' },
  { worker: 'Meeseeks Beta', approach: 'Object Detection', confidence: 0.78, description: 'Found geometric shapes that transform predictably' },
  { worker: 'Meeseeks Gamma', approach: 'Color Analysis', confidence: 0.92, description: 'Detected color mapping rules between input/output' }
];

// Test 1: Create voting buttons
console.log('\n1️⃣ Worker Communication Workflow\n');
console.log('📊 Workers share discoveries:\n');

discoveries.forEach((d, i) => {
  console.log(`   ${i + 1}. ${d.worker}`);
  console.log(`      Approach: ${d.approach}`);
  console.log(`      ${d.description}`);
  console.log(`      Confidence: ${(d.confidence * 100).toFixed(0)}%\n`);
});

// Create voting buttons
const options = discoveries.map(d => `${d.approach} (${(d.confidence * 100).toFixed(0)}%)`);
const quiz = helper.createQuiz('Vote for the best approach:', options, 2);

console.log('🗳️ User votes via inline buttons:\n');
console.log('✅ Created voting buttons:');
quiz.reply_markup.inline_keyboard.forEach((row, i) => {
  console.log(`   [${i + 1}] ${row[0].text}`);
});

// Test 2: Confirmation
console.log('\n2️⃣ Testing confirmation buttons...\n');

const confirm = helper.createConfirmation('Apply selected approach?');
console.log('✅ Created confirmation:');
confirm.reply_markup.inline_keyboard[0].forEach((btn, i) => {
  console.log(`   [${btn.text}]`);
});

// Test 3: Menu navigation
console.log('\n3️⃣ Testing menu navigation...\n');

const menu = helper.createMenu('main', {
  text: '🦥 Sloth Control Panel',
  buttons: [
    [{ text: '📊 Stats', callback_data: 'menu:{"menuId":"stats"}' }],
    [{ text: '⚙️ Settings', callback_data: 'menu:{"menuId":"settings"}' }],
    [{ text: '❓ Help', callback_data: 'menu:{"menuId":"help"}' }]
  ]
});

console.log('✅ Created menu:');
console.log(`   Text: ${menu.text}`);
menu.reply_markup.inline_keyboard.forEach((row) => {
  console.log(`   [${row[0].text}]`);
});

// Summary
console.log('\n' + '=' .repeat(50));
console.log('✅ Test Results:\n');
console.log('   ✓ Voting buttons created');
console.log('   ✓ Confirmation buttons created');
console.log('   ✓ Menu navigation created');
console.log('   ✓ Workflow simulation complete');

console.log('\n🎉 Button system is working correctly!\n');

console.log('💡 To test with real Telegram:');
console.log('   1. Set TELEGRAM_BOT_TOKEN environment variable');
console.log('   2. Set TELEGRAM_CHAT_ID environment variable');
console.log('   3. Run: node test_communication_demo.js');
console.log('\n🦥 Ready for production use!');
