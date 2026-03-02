/**
 * Test Suite for Telegram Button Hooks System
 * Verifies all components work correctly without requiring a bot token
 */

const TelegramButtonHelper = require('../../telegram_button_helper');
const assert = require('assert');

console.log('🧪 Telegram Button Hooks Test Suite\n');
console.log('==================================\n');

let testsPassed = 0;
let testsFailed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`✅ ${name}`);
    testsPassed++;
  } catch (error) {
    console.log(`❌ ${name}`);
    console.log(`   Error: ${error.message}`);
    testsFailed++;
  }
}

// Create helper instance (token not needed for these tests)
const helper = new TelegramButtonHelper('test_token');

// Test 1: Create single button
test('Create single button', () => {
  const button = helper.createButton('Click Me', 'test_callback');
  assert.strictEqual(button.text, 'Click Me');
  assert.strictEqual(button.callback_data, 'test_callback');
});

// Test 2: Create button row
test('Create button row', () => {
  const row = helper.createRow(
    helper.createButton('A', 'a'),
    helper.createButton('B', 'b')
  );
  assert.strictEqual(row.length, 2);
  assert.strictEqual(row[0].text, 'A');
  assert.strictEqual(row[1].text, 'B');
});

// Test 3: Create keyboard
test('Create keyboard', () => {
  const keyboard = helper.createKeyboard(
    helper.createRow(helper.createButton('1', 'one')),
    helper.createRow(helper.createButton('2', 'two'))
  );
  assert.ok(keyboard.inline_keyboard);
  assert.strictEqual(keyboard.inline_keyboard.length, 2);
});

// Test 4: Encode/decode callback
test('Encode and decode callback', () => {
  const original = { type: 'quiz', payload: { id: 123 } };
  const encoded = helper.encodeCallback(original.type, original.payload);
  const decoded = helper.decodeCallback(encoded);
  
  assert.strictEqual(decoded.type, original.type);
  assert.strictEqual(decoded.payload.id, original.payload.id);
});

// Test 5: Create confirmation buttons
test('Create confirmation buttons', () => {
  const keyboard = helper.createConfirmation('delete', { itemId: 456 });
  assert.ok(keyboard.inline_keyboard);
  assert.strictEqual(keyboard.inline_keyboard.length, 1);
  assert.strictEqual(keyboard.inline_keyboard[0].length, 2);
  
  const yesButton = keyboard.inline_keyboard[0][0];
  const noButton = keyboard.inline_keyboard[0][1];
  
  assert.ok(yesButton.text.includes('Yes'));
  assert.ok(noButton.text.includes('No'));
});

// Test 6: Create quiz buttons
test('Create quiz buttons', () => {
  const options = ['Option A', 'Option B', 'Option C'];
  const keyboard = helper.createQuizButtons('q1', options);
  
  assert.ok(keyboard.inline_keyboard);
  assert.strictEqual(keyboard.inline_keyboard.length, 3);
  
  keyboard.inline_keyboard.forEach((row, index) => {
    assert.strictEqual(row[0].text, options[index]);
  });
});

// Test 7: Create menu
test('Create menu buttons', () => {
  const items = [
    { label: 'Settings', action: 'settings' },
    { label: 'Help', action: 'help' }
  ];
  const keyboard = helper.createMenu(items, 'main');
  
  assert.ok(keyboard.inline_keyboard);
  assert.strictEqual(keyboard.inline_keyboard.length, 3); // 2 items + back
});

// Test 8: URL button
test('Create URL button', () => {
  const button = helper.createButton('Visit', '', { url: 'https://example.com' });
  assert.strictEqual(button.url, 'https://example.com');
  assert.ok(!button.callback_data);
});

// Test 9: Callback compression
test('Compress large callback', () => {
  const largePayload = {
    data: 'x'.repeat(100), // Large payload
    more: 'y'.repeat(100)
  };
  const encoded = helper.encodeCallback('test', largePayload);
  
  // Should be compressed to type:id format
  assert.ok(encoded.length < 100);
  assert.ok(encoded.includes(':'));
});

// Test 10: Log interaction
test('Log interaction', () => {
  const log = helper.logInteraction(123, 'testuser', 'quiz', { answer: 1 }, 'correct');
  
  assert.strictEqual(log.userId, 123);
  assert.strictEqual(log.username, 'testuser');
  assert.strictEqual(log.type, 'quiz');
  assert.strictEqual(log.result, 'correct');
  assert.ok(log.timestamp);
});

// Test 11: Quiz Handler
console.log('\nTesting Quiz Handler...');
const QuizHandler = require('./quiz-handler');

const quizConfig = {
  test_q1: {
    question: 'Test question?',
    options: ['A', 'B', 'C'],
    correctIndex: 1,
    explanation: 'B is correct'
  }
};

const quizHandler = new QuizHandler(helper, quizConfig);

test('Quiz handler initialization', () => {
  assert.ok(quizHandler.quizzes);
  assert.ok(quizHandler.quizzes.test_q1);
});

test('Get user progress', () => {
  const progress = quizHandler.getUserProgress(999);
  assert.strictEqual(progress.totalAnswered, 0);
  assert.strictEqual(progress.correctAnswers, 0);
});

test('Update progress', () => {
  quizHandler.updateProgress(999, 'test_q1', true);
  const progress = quizHandler.getUserProgress(999);
  assert.strictEqual(progress.totalAnswered, 1);
  assert.strictEqual(progress.correctAnswers, 1);
});

test('Reset progress', () => {
  quizHandler.updateProgress(888, 'test_q1', false);
  quizHandler.resetProgress(888);
  const progress = quizHandler.getUserProgress(888);
  assert.strictEqual(progress.totalAnswered, 0);
});

test('Performance message', () => {
  assert.ok(quizHandler.getPerformanceMessage(100).includes('Perfect'));
  assert.ok(quizHandler.getPerformanceMessage(80).includes('Great'));
  assert.ok(quizHandler.getPerformanceMessage(60).includes('Good'));
});

// Test 12: Config loading
console.log('\nTesting Config Loading...');
const fs = require('fs');
const path = require('path');

test('Load config file', () => {
  const configPath = path.join(__dirname, 'config.json');
  const configData = fs.readFileSync(configPath, 'utf8');
  const config = JSON.parse(configData);
  
  assert.ok(config.botToken);
  assert.ok(config.quizzes);
  assert.ok(config.menus);
  assert.ok(config.confirmations);
});

test('Config has example quiz', () => {
  const configPath = path.join(__dirname, 'config.json');
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  
  assert.ok(config.quizzes.example_q1);
  assert.ok(config.quizzes.example_q1.question);
  assert.ok(config.quizzes.example_q1.options);
  assert.strictEqual(typeof config.quizzes.example_q1.correctIndex, 'number');
});

test('Config has example menus', () => {
  const configPath = path.join(__dirname, 'config.json');
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  
  assert.ok(config.menus.main);
  assert.ok(config.menus.quiz);
  assert.ok(config.menus.info);
  assert.ok(config.menus.settings);
});

// Summary
console.log('\n==================================');
console.log(`📊 Test Results:`);
console.log(`   ✅ Passed: ${testsPassed}`);
console.log(`   ❌ Failed: ${testsFailed}`);
console.log(`   📝 Total:  ${testsPassed + testsFailed}`);
console.log('==================================\n');

if (testsFailed === 0) {
  console.log('🎉 All tests passed!\n');
  process.exit(0);
} else {
  console.log('⚠️  Some tests failed.\n');
  process.exit(1);
}
