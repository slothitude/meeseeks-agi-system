const { execSync } = require('child_process');

// Simple 2-button test
const buttons = [
  [
    { text: "✅ Yes", callback_data: "yes" },
    { text: "❌ No", callback_data: "no" }
  ]
];

const buttonsJson = JSON.stringify(buttons).replace(/"/g, '\\"');

const cmd = `openclaw message send --channel telegram --target 5597932516 -m "Do you see buttons?" --buttons "${buttonsJson}"`;

console.log("Sending...");
execSync(cmd, { stdio: 'inherit', shell: true });
console.log("\nDone! Check Telegram for buttons.");
