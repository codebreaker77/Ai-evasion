import Redis from 'ioredis';

let redisClient = null;

function getRedisUrl() {
  if (process.env.Store_REDIS_URL) return process.env.Store_REDIS_URL;
  if (process.env.STORE_REDIS_URL) return process.env.STORE_REDIS_URL;
  if (process.env.REDIS_URL) return process.env.REDIS_URL;

  // Scan for any environment variable ending in REDIS_URL (e.g. prefix_REDIS_URL)
  const key = Object.keys(process.env).find(k => k.toUpperCase().endsWith('REDIS_URL'));
  if (key) return process.env[key];

  return null;
}

function getRedis() {
  const redisUrl = getRedisUrl();
  if (!redisUrl) {
    return null;
  }

  if (!redisClient) {
    redisClient = new Redis(redisUrl, {
      maxRetriesPerRequest: 2,
      connectTimeout: 5000,
      lazyConnect: false,
    });
  }
  return redisClient;
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const redis = getRedis();
  if (!redis) {
    console.warn('Notice: REDIS_URL environment variable is not set.');
    return res.status(200).json({ count: 291 });
  }

  try {
    // Identify unique visitor using client token + IP
    const clientVisitorId = req.query.visitorId || 'anonymous';
    const rawIp =
      req.headers['x-forwarded-for'] ||
      req.headers['x-real-ip'] ||
      req.socket?.remoteAddress ||
      '';
    const clientIp = typeof rawIp === 'string' ? rawIp.split(',')[0].trim() : '';
    const uniqueKey = clientIp ? `${clientIp}_${clientVisitorId}` : clientVisitorId;

    const current = await redis.get('slop_spammer_count');
    let count;

    if (current === null || current === undefined) {
      // First user initialization: seed at 291
      await redis.set('slop_spammer_count', 291);
      await redis.sadd('unique_visitors', uniqueKey);
      count = 291;
    } else {
      // Check if visitor is unique
      const isNew = await redis.sadd('unique_visitors', uniqueKey);
      if (isNew === 1) {
        count = await redis.incr('slop_spammer_count');
      } else {
        count = current;
      }
    }

    return res.status(200).json({ count: Number(count) || 291 });
  } catch (error) {
    console.error('Redis error:', error);
    return res.status(200).json({ count: 291, error: error.message });
  }
}
