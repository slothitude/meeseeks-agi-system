/**
 * Quiz Handler
 * Handles quiz-specific button callbacks
 */

class QuizHandler {
  /**
   * Handle quiz answer callback
   */
  static async handle(callback, data, callbackHandler) {
    const { questionId, answerId, correctAnswer } = data;
    const userId = callback.from.id;
    const isCorrect = answerId === correctAnswer;

    // Build response
    const feedbackEmoji = isCorrect ? '✅' : '❌';
    const feedbackText = isCorrect 
      ? 'Correct! Well done! 🎉'
      : `Incorrect. The correct answer was: ${correctAnswer}`;

    // Answer the callback (shows popup)
    await callbackHandler.answerCallback(callback.id, feedbackText);

    // Update the message with visual feedback
    const originalText = callback.message?.text || '';
    const updatedText = `${originalText}\n\n${feedbackEmoji} ${feedbackText}`;

    try {
      await callbackHandler.editMessageText(
        callback.message.chat.id,
        callback.message.message_id,
        updatedText
      );
    } catch (error) {
      // Message might be too old to edit, that's okay
      console.log('Could not edit message:', error.message);
    }

    // Log the quiz result
    console.log(`📊 Quiz result: User ${userId} - ${isCorrect ? 'CORRECT' : 'INCORRECT'} (Q: ${questionId})`);

    return {
      questionId,
      answerId,
      isCorrect,
      userId
    };
  }

  /**
   * Create quiz inline keyboard
   */
  static createQuizKeyboard(questionId, options, correctAnswer) {
    const buttons = options.map((option, index) => [{
      text: option,
      callback_data: `quiz:{"questionId":"${questionId}","answerId":"${index}","correctAnswer":"${correctAnswer}"}`
    }]);

    return { inline_keyboard: buttons };
  }

  /**
   * Build quiz message with buttons
   */
  static buildQuizMessage(question, options, questionId, correctAnswer) {
    const keyboard = this.createQuizKeyboard(questionId, options, correctAnswer);
    
    return {
      text: `❓ *Question:* ${question}`,
      reply_markup: keyboard
    };
  }
}

module.exports = QuizHandler;
