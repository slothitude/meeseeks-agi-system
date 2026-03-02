/**
 * Test Communication Demo
 * Demonstrates workers sharing discoveries and voting via inline buttons
 * 
 * This simulates the ARC-AGI-2 research workflow:
 * 1. Workers explore and share discoveries
 * 2. User votes on best approach via inline buttons
 * 3. Results summarized
 */

const TelegramButtonHelper = require('../../telegram_button_helper');

// Get bot token from environment or config
const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || 'YOUR_TOKEN_HERE';
const CHAT_ID = process.env.TELEGRAM_CHAT_ID || 'YOUR_CHAT_ID';

const helper = new TelegramButtonHelper(BOT_TOKEN);

// Simulated worker discoveries
const discoveries = [
  {
    worker: 'Meeseeks Alpha',
    approach: 'Pattern Matching',
    description: 'Identified repeating patterns in grid cells',
    confidence: 0.85
  },
  {
    worker: 'Meeseeks Beta',
    approach: 'Object Detection',
    description: 'Found geometric shapes that transform predictably',
    confidence: 0.78
  },
  {
    worker: 'Meeseeks Gamma',
    approach: 'Color Analysis',
    description: 'Detected color mapping rules between input/output',
    confidence: 0.92
  }
];

/**
 * Display discoveries and ask user to vote
 */
async function askForVote() {
  console.log('🧪 Communication Demo - Worker Voting System\n');
  console.log('=' .repeat(50));
  
  // Display discoveries
  console.log('\n📊 Worker Discoveries:\n');
  discoveries.forEach((d, i) => {
    console.log(`${i + 1}. ${d.worker}`);
    console.log(`   Approach: ${d.approach}`);
    console.log(`   ${d.description}`);
    console.log(`   Confidence: ${(d.confidence * 100).toFixed(0)}%\n`);
  });
  
  // Create voting buttons
  const options = discoveries.map((d, i) => 
    `${i + 1}. ${d.approach} (${(d.confidence * 100).toFixed(0)}%)`
  );
  
  const text = `🧪 *ARC-AGI-2 Research Results*\n\n` +
    `Workers have analyzed the task and found ${discoveries.length} approaches:\n\n` +
    discoveries.map((d, i) => 
      `*${i + 1}. ${d.approach}*\n` +
      `   By: ${d.worker}\n` +
      `   ${d.description}\n` +
      `   Confidence: ${(d.confidence * 100).toFixed(0)}%\n`
    ).join('\n') +
    `\n\n👇 *Vote for the best approach:*`;
  
  const keyboard = helper.createQuizButtons('vote_approaches', options);
  
  try {
    const result = await helper.sendMessage(CHAT_ID, text, keyboard);
    console.log('✅ Sent voting message to Telegram!');
    console.log(`   Message ID: ${result.message_id || result.result?.message_id}`);
    console.log('\n📱 Check your Telegram for voting buttons!');
    console.log('   You should see:');
    options.forEach((opt, i) => {
      console.log(`   [${i + 1}] ${opt}`);
    });
    
    // Start listening for votes
    console.log('\n🔄 Listening for your vote (60 seconds)...\n');
    
    let lastUpdateId = 0;
    const startTime = Date.now();
    const timeout = 60000; // 60 seconds
    
    while (Date.now() - startTime < timeout) {
      const params = {
        timeout: 5,
        allowed_updates: ['callback_query']
      };
      
      if (lastUpdateId > 0) {
        params.offset = lastUpdateId + 1;
      }
      
      const updates = await helper.apiRequest('getUpdates', params);
      
      for (const update of updates) {
        lastUpdateId = update.update_id;
        
        if (update.callback_query) {
          const callback = update.callback_query;
          const decoded = helper.decodeCallback(callback.data);
          
          if (decoded.type === 'quiz_answer' && decoded.payload.questionId === 'vote_approaches') {
            const voteIndex = decoded.payload.optionIndex;
            const chosenApproach = discoveries[voteIndex];
            
            console.log(`\n🗳️ Vote received from @${callback.from.username || callback.from.first_name}!`);
            console.log(`   Voted for: ${chosenApproach.approach}`);
            
            // Answer callback
            await helper.answerCallback(callback.id, {
              text: `✅ You voted for: ${chosenApproach.approach}!`,
              showAlert: false
            });
            
            // Show results
            await showResults(CHAT_ID, callback.message.message_id, chosenApproach);
            
            console.log('\n✅ Demo complete! Results sent to Telegram.');
            console.log('=' .repeat(50));
            return;
          }
        }
      }
      
      // Small delay
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    console.log('\n⏱️ Timeout - no vote received within 60 seconds.');
    console.log('   Run the script again to try once more.');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.message.includes('chat not found')) {
      console.log('\n💡 Tip: Make sure to:');
      console.log('   1. Set TELEGRAM_CHAT_ID environment variable');
      console.log('   2. Start a chat with your bot first');
      console.log('   3. Send /start to the bot');
    }
  }
}

/**
 * Show voting results
 */
async function showResults(chatId, messageId, winner) {
  const text = `📊 *Voting Results*\n\n` +
    `🏆 *Winner: ${winner.approach}*\n` +
    `   By: ${winner.worker}\n` +
    `   ${winner.description}\n` +
    `   Confidence: ${(winner.confidence * 100).toFixed(0)}%\n\n` +
    `✅ This approach will be used for solving the task.\n\n` +
    `_Demo completed successfully!_`;
  
  await helper.editMessage(chatId, messageId, text);
}

// Run the demo
console.log('🥒 Meeseeks Communication Demo');
console.log('   Testing inline buttons for worker voting\n');

askForVote().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
