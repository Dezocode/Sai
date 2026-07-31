// Composio Google Drive connector stub (A2)
// Loads secrets from VPS env only; never hardcodes values.

const COMPOSIO_API_KEY = process.env.COMPOSIO_API_KEY;

class ComposioGoogleDriveConnector {
  constructor() {
    this.status = COMPOSIO_API_KEY ? 'Pending' : 'Pending';
  }

  async connect() {
    // TODO: composio sessions.create with googledrive toolkit
    throw new Error('OAuth not completed: Pending dezocode toolkit approval');
  }

  async listFiles(query) {
    // TODO: list files via Composio toolkit
    return [];
  }

  async download(fileId) {
    // TODO: download file via Composio toolkit
    throw new Error('Not implemented: connect first');
  }

  async upload(fileId, localPath) {
    // TODO: upload file via Composio toolkit
    throw new Error('Not implemented: connect first');
  }

  async syncMirror(localMirrorPath) {
    // TODO: bidirectional sync between vault/mirror and Drive
    return { synced: 0, skipped: 0 };
  }
}

module.exports = { ComposioGoogleDriveConnector };
