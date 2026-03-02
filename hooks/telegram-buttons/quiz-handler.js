/**
 * Quiz Handler
 * Handles quiz question callbacks and scoring
 */

class QuizHandler {
  constructor(helper, quizConfig) {
    this.helper = helper;
    this.quizzes = quizConfig || {};
    
    // Track user progress (in-memory, could use database)
    this.userProgress = new Map();
  }

  /**
   * Handle quiz answer callback
   */
  async handleAnswer({ callbackQueryId, userId, username, chatId, messageId, questionId, optionIndex }) {
    console.log(`📝 Quiz answer: ${questionId} option ${optionIndex} by ${username}`);
    
    // Get the quiz question
    const question = this.quizzes[questionId];
    
    if (!question) {
      await this.helper.answerCallback(callbackQueryId, {
        text: '⚠️ Question not found',
        showAlert: true
      });
      return 'question_not_found';
    }
    
    // Check if answer is correct
    const isCorrect = optionIndex === question.correctIndex;
    const selectedOption = question.options[optionIndex];
    
    // Update user progress
    this.updateProgress(userId, questionId, isCorrect);
    
    // Provide feedback
    const feedbackText = isCorrect 
      ? `✅ Correct! "${selectedOption}" is the right answer.`
      : `❌ Incorrect. You selected "${selectedOption}". The correct answer was "${question.options[question.correctIndex]}".`;
    
    await this.helper.answerCallback(callbackQueryId, {
      text: feedbackText,
      showAlert: true,
      cacheTime: 0
    });
    
    // Update message with result
    const resultEmoji = isCorrect ? '✅' : '❌';
    const updatedText = `${resultEmoji} *${question.question}*\n\n` +
      `Your answer: ${selectedOption}\n` +
      `Result: ${isCorrect ? 'Correct!' : 'Incorrect'}\n\n` +
      `${question.explanation || ''}`;
    
    // Remove buttons after answering
    await this.helper.editMessage(chatId, messageId, updatedText);
    
    // Check if there's a next question
    const progress = this.getUserProgress(userId);
    const quizSequence = this.quizzes[questionId]?.sequence;
    
    if (quizSequence && progress.currentQuestion < quizSequence.length) {
      // Send next question after delay
      setTimeout(() => {
        this.sendNextQuestion(chatId, userId, quizSequence, progress.currentQuestion);
      }, 2000);
    } else if (quizSequence) {
      // Quiz complete, show score
      setTimeout(() => {
        this.showQuizResults(chatId, userId);
      }, 2000);
    }
    
    return isCorrect ? 'correct' : 'incorrect';
  }

  /**
   * Send next question in sequence
   */
  async sendNextQuestion(chatId, userId, sequence, questionNumber) {
    const nextQuestionId = sequence[questionNumber];
    const question = this.quizzes[nextQuestionId];
    
    if (!question) {
      console.error(`Question ${nextQuestionId} not found`);
      return;
    }
    
    const keyboard = this.helper.createQuizButtons(nextQuestionId, question.options);
    
    await this.helper.sendMessage(
      chatId,
      `❓ *Question ${questionNumber + 1}*\n\n${question.question}`,
      keyboard
    );
    
    // Update progress
    const progress = this.getUserProgress(userId);
    progress.currentQuestion = questionNumber + 1;
    this.userProgress.set(userId, progress);
  }

  /**
   * Show quiz results
   */
  async showQuizResults(chatId, userId) {
    const progress = this.getUserProgress(userId);
    const total = progress.totalAnswered;
    const correct = progress.correctAnswers;
    const percentage = total > 0 ? Math.round((correct / total) * 100) : 0;
    
    const resultText = `📊 *Quiz Complete!*\n\n` +
      `✅ Correct: ${correct}/${total}\n` +
      `📈 Score: ${percentage}%\n\n` +
      `${this.getPerformanceMessage(percentage)}`;
    
    await this.helper.sendMessage(chatId, resultText);
  }

  /**
   * Get performance message based on score
   */
  getPerformanceMessage(percentage) {
    if (percentage === 100) return '🏆 Perfect score! Outstanding!';
    if (percentage >= 80) return '🎉 Great job! Excellent work!';
    if (percentage >= 60) return '👍 Good effort! Keep practicing!';
    if (percentage >= 40) return '📚 Not bad, but room for improvement.';
    return '💪 Keep studying, you\'ll get better!';
  }

  /**
   * Update user progress
   */
  updateProgress(userId, questionId, isCorrect) {
    const progress = this.getUserProgress(userId);
    
    progress.totalAnswered++;
    if (isCorrect) progress.correctAnswers++;
    progress.answeredQuestions.add(questionId);
    
    this.userProgress.set(userId, progress);
  }

  /**
   * Get user progress
   */
  getUserProgress(userId) {
    if (!this.userProgress.has(userId)) {
      this.userProgress.set(userId, {
        totalAnswered: 0,
        correctAnswers: 0,
        currentQuestion: 0,
        answeredQuestions: new Set()
      });
    }
    
    return this.userProgress.get(userId);
  }

  /**
   * Reset user progress
   */
  resetProgress(userId) {
    this.userProgress.delete(userId);
    console.log(`🔄 Progress reset for user ${userId}`);
  }

  /**
   * Create a standalone quiz message
   */
  async sendQuiz(chatId, questionId) {
    const question = this.quizzes[questionId];
    
    if (!question) {
      throw new Error(`Quiz question ${questionId} not found`);
    }
    
    const keyboard = this.helper.createQuizButtons(questionId, question.options);
    
    return await this.helper.sendMessage(
      chatId,
      `📝 *Quiz Question*\n\n${question.question}`,
      keyboard
    );
  }
}

module.exports = QuizHandler;
