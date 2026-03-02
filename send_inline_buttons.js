#!/usr/bin/env node
/**
 * Send Telegram message with inline buttons
 * 
 * Usage:
 *   node send_inline_buttons.js "Your question" "Option1" "Option2" "Option3" ...
 */

const { execSync } = require('child_process');

const args = process.argv.slice(2);
if (args.length < 2) {
  console.log("Usage: node send_inline_buttons.js \"Question\" \"Option1\" \"Option2\" ...");
  process.exit(1);
}

const [question, ...options] = args;

// Create button rows (2 buttons per row)
const buttons = [];
for (let i = 0; i < options.length; i += 2) {
  const row = [
    { text: options[i], callback_data: `option_${i}` }
  ];
  if (options[i + 1]) {
    row.push({ text: options[i + 1], callback_data: `option_${i + 1}` });
  }
  buttons.push(row);
}

const buttonsJson = JSON.stringify(buttons).replace(/"/g, '\\"');

const cmd = `openclaw message send --channel telegram --target 5597932516 -m "${question}" --buttons "${buttonsJson}"`;

try {
  execSync(cmd, { stdio: 'inherit', shell: true });
  console.log("\n✅ Sent with inline buttons!");
} catch (e) {
  console.error("❌ Error:", e.message);
}
