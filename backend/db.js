const { Pool } = require('pg');

const pool = new Pool({
  user: 'jiyu',
  host: 'localhost',
  database: 'postgres',
  password: '', // 비밀번호 없음
  port: 5432,
});

module.exports = pool; 