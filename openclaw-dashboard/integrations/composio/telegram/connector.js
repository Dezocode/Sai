// Composio Telegram dashboard connector stub (A2)
// Loads secrets from VPS env only; never hardcodes values.

const COMPOSIO_API_KEY = process.env.COMPOSIO_API_KEY;

class ComposioTelegramConnector {
  constructor() {
    // Key presence does not imply OAuth completion; status remains Pending.
    this.status = COMPOSIO_API_KEY ? 'Pending' : 'Pending';
  }

  async connect() {
    // TODO: composio sessions.create with telegram toolkit
    throw new Error('OAuth not completed: Pending dezocode toolkit approval');
  }

  async listChats() {
    // TODO: list chats via Composio toolkit
    return [];
  }

  async sendMessage(chatId, text) {
    // TODO: send message via Composio toolkit
    throw new Error('Not implemented: connect first');
  }
}

module.exports = { ComposioTelegramConnector };
