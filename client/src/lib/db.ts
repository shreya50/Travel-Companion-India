import path from 'path';
import Database from 'better-sqlite3';

const dbPath = path.resolve(process.cwd(), '../database/travel_companion.db');

declare global {
  // eslint-disable-next-line no-var
  var dbInstance: Database.Database | undefined;
}

let db: Database.Database;

if (process.env.NODE_ENV === 'production') {
  db = new Database(dbPath);
} else {
  if (!global.dbInstance) {
    global.dbInstance = new Database(dbPath);
  }
  db = global.dbInstance;
}

export default db;
