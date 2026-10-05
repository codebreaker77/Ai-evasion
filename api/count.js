import { Redis } from '@upstash/redis';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Upstash Redis environment variables
  const url =
    process.env.UPSTASH_REDIS_REST_URL ||
    process.env.KV_REST_API_URL ||
    process.env.REDIS_REST_URL ||
    process.env.UPSTASH_URL;
  const token =
    process.env.UPSTASH_REDIS_REST_TOKEN ||
    process.env.KV_REST_API_TOKEN ||
    process.env.REDIS_REST_TOKEN ||
    process.env.UPSTASH_TOKEN;

  const availableKeys = Object.keys(process.env).filter(k =>
    k.toUpperCase().includes('REDIS') ||
    k.toUpperCase().includes('KV') ||
    k.toUpperCase().includes('UPSTASH')
  );

  if (!url || !token) {
    return res.status(200).json({
      count: 291,
      debug: {
        error: "missing_redis_env_vars",
        foundKeys: availableKeys
      }
    });
  }

  const redis = new Redis({ url, token });

  try {
    // Identify the unique user using client visitorId + IP address
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
      // First time initialization: start at 291 for the first user
      await redis.set('slop_spammer_count', 291);
      await redis.sadd('unique_visitors', uniqueKey);
      count = 291;
    } else {
      // Check if this visitor is unique
      const isNew = await redis.sadd('unique_visitors', uniqueKey);
      if (isNew === 1) {
        count = await redis.incr('slop_spammer_count');
      } else {
        count = current;
      }
    }

    return res.status(200).json({ count: Number(count) || 291 });
  } catch (error) {
    console.error('Redis count error:', error);
    return res.status(200).json({
      count: 291,
      debug: {
        error: "redis_exception",
        message: error.message
      }
    });
  }
}
