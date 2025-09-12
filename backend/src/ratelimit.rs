use governor::{Quota, clock::DefaultClock, state::InMemoryState, RateLimiter};
use std::{num::NonZeroU32, sync::Arc};
use dashmap::DashMap;
use once_cell::sync::Lazy;
use governor::state::NotKeyed;

type ApiKey = String;

const RATE_LIMIT: u32 = 3;

// Global, thread-safe map: API key → rate limiter
static API_KEY_LIMITERS: Lazy<DashMap<ApiKey, Arc<RateLimiter<NotKeyed, InMemoryState, DefaultClock>>>> =
    Lazy::new(DashMap::new);

/// Checks if the given API key is within its rate limit.
/// Returns `true` if allowed, `false` if rate limit is exceeded.
pub fn check_rate_limit(api_key: &str) -> bool {
    let limiter = API_KEY_LIMITERS
        .entry(api_key.to_string())
        .or_insert_with(|| {
            let quota = Quota::per_minute(NonZeroU32::new(RATE_LIMIT).unwrap());
            Arc::new(RateLimiter::direct_with_clock(quota, DefaultClock::default()))
        })
        .clone();

    limiter.check().is_ok()
}
