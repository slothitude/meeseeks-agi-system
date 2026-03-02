/**
 * Button Helper Integration for Sloth_rog
 * 
 * Easy integration with Telegram button helper for multiple choice questions.
 */

const TelegramButtonHelper = require('./telegram_button_helper');

const BOT_TOKEN = '7971019788:AAE-XzCbpoIS3Z8JN9d2PwdC4hbvATgiyYg';
const CHAT_ID = '5597932516';

let helper = null;
let started = false;

function getHelper() {
  if (!helper) {
    helper = new TelegramButtonHelper(BOT_TOKEN);
    
    // Register handlers
    helper.on('quiz', async (callback, data) => {
      console.log('📝 Quiz answer:', data);
      // The helper handles quiz logic automatically
      return { handled: true };
    });
    
    helper.on('confirm', async (callback, data) => {
      console.log('✅ Confirmation:', data);
      // The helper handles confirmations automatically
      return { handled: true };
    });
    
    helper.on('menu', async (callback, data) => {
      console.log('📋 Menu selection:', data);
      return { handled: true };
    });
    
    helper.on('custom', async (callback, data) => {
      console.log('🎯 Custom action:', data);
      return { handled: true };
    });
  }
  return helper;
}

/**
 * Send a multiple choice question with inline buttons
 * @param {string} question - The question to ask
 * @param {string[]} options - Array of option strings
 * @param {number} correctIndex - Index of correct answer (optional, for quizzes)
 * @returns {Promise<object>} - Message result
 */
async function askMultipleChoice(question, options, correctIndex = null) {
  const h = getHelper();
  
  // Start listening if not already
  if (!started) {
    h.start();
    started = true;
  }
  
  // Create quiz if correctIndex provided, otherwise create simple choice
  if (correctIndex !== null) {
    const quiz = h.createQuiz(question, options, correctIndex);
    return await h.sendMessageWithButtons(CHAT_ID, `❓ *Quiz*\n\n${question}`, quiz.buttons);
  } else {
    // Create simple choice buttons
    const buttons = [];
    for (let i = 0; i < options.length; i += 2) {
      const row = [];
      for (let j = 0; j < 2 && i + j < options.length; j++) {
        row.push({
          text: options[i + j],
          callback_data: `custom:{"type":"choice","index":${i + j},"option":"${options[i + j]}"}`
        });
      }
      buttons.push(row);
    }
    return await h.sendMessageWithButtons(CHAT_ID, `❓ *Question*\n\n${question}`, buttons);
  }
}

/**
 * Send a simple Yes/No confirmation
 * @param {string} question - The question to confirm
 * @param {object} context - Optional context data
 * @returns {Promise<object>} - Message result
 */
async function askConfirmation(question, context = null) {
  const h = getHelper();
  
  if (!started) {
    h.start();
    started = true;
  }
  
  const confirm = h.createConfirmation(question, context);
  return await h.sendMessageWithButtons(CHAT_ID, `⚠️ *Confirmation Required*\n\n${question}`, confirm.buttons);
}

/**
 * Start listening for button callbacks
 */
function startListening() {
  const h = getHelper();
  if (!started) {
    h.start();
    started = true;
    console.log('🔄 Button callback listener started');
  }
}

/**
 * Stop listening for callbacks
 */
function stopListening() {
  const h = getHelper();
  if (started) {
    h.stop();
    started = false;
    console.log('⏹️ Button callback listener stopped');
  }
}

module.exports = {
  askMultipleChoice,
  askConfirmation,
  startListening,
  stopListening,
  getHelper
};
