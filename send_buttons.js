const { execSync } = require('child_process');

const buttons = JSON.stringify([
  [
    { text: "4", callback_data: "correct" },
    { text: "5", callback_data: "wrong" }
  ]
]);

const escapedButtons = buttons.replace(/"/g, '\\"');
const cmd = `openclaw message send --channel telegram --target 5597932516 -m "What is 2+2?" --buttons "${escapedButtons}"`;
console.log("Running:", cmd);

try {
  execSync(cmd, { stdio: 'inherit', shell: true });
} catch (e) {
  console.error("Error:", e.message);
}
