const { Pool } = require('pg');

const pool = new Pool({
  user: 'postgres',
  host: 'roombot-new.chuqo4maweif.us-east-2.rds.amazonaws.com',
  database: 'postgres',
  password: 'ju041803',
  port: 5432,
});

module.exports = pool; 