/// NEXUS 保险合约 - 星际保险协议
/// 为 EVE Frontier 玩家提供链上保险服务
///
/// 功能:
/// - InsurancePool: 共享保险资金池
/// - Policy: 保险单据
/// - buy_insurance: 购买保险
/// - claim: 申请理赔
/// - renew: 续保
/// - get_quote: 获取报价
///
/// 事件: PolicyCreated / ClaimProcessed / ClaimDenied
module eve_commander::insurance;

use sui::balance::{Self, Balance};
use sui::clock::Clock;
use sui::coin::{Self, Coin};
use sui::event;
use sui::sui::SUI;

// === Errors ===
#[error(code = 0)]
const EPolicyExpired: vector<u8> = b"Insurance policy has expired";
#[error(code = 1)]
const EPolicyNotActive: vector<u8> = b"Insurance policy is not active";
#[error(code = 2)]
const EInsufficientPool: vector<u8> = b"Insufficient funds in insurance pool";
#[error(code = 3)]
const EInvalidPremium: vector<u8> = b"Premium amount is invalid";
#[error(code = 4)]
const EClaimTooLarge: vector<u8> = b"Claim amount exceeds coverage";
#[error(code = 5)]
const ECooldownNotMet: vector<u8> = b"Claim cooldown period not met";
#[error(code = 6)]
const ENotPolicyOwner: vector<u8> = b"Only policy owner can perform this action";
#[error(code = 7)]
const EInvalidCoverage: vector<u8> = b"Invalid coverage tier";

// === Constants ===
/// 保险期限: 7 天 (毫秒)
const DEFAULT_DURATION_MS: u64 = 7 * 24 * 60 * 60 * 1000;
/// 理赔冷却: 1 小时 (毫秒)
const CLAIM_COOLDOWN_MS: u64 = 60 * 60 * 1000;
/// 最大赔付比例: 覆盖额的 80%
const MAX_PAYOUT_BPS: u64 = 8000; // 80%
/// BPS 基数
const BPS_BASE: u64 = 10000;

// === Coverage Tiers ===
/// 基础保险 - 低保费低赔付
const TIER_BASIC: u8 = 1;
/// 标准保险 - 中等保费中等赔付
const TIER_STANDARD: u8 = 2;
/// 高级保险 - 高保费高赔付
const TIER_PREMIUM: u8 = 3;

// === Structs ===

/// 保险资金池 - 共享对象
public struct InsurancePool has key {
    id: UID,
    /// 资金池余额
    pool_balance: Balance<SUI>,
    /// 管理员地址
    admin: address,
    /// 总保费收入
    total_premiums_collected: u64,
    /// 总理赔支出
    total_claims_paid: u64,
    /// 活跃保单数
    active_policies: u64,
    /// 总保单数
    total_policies_issued: u64,
    /// 总拒赔数
    total_claims_denied: u64,
    /// 基础保费率 (BPS, 如 500 = 5%)
    base_premium_rate_bps: u64,
}

/// 保险单据 - 由购买者持有
public struct Policy has key, store {
    id: UID,
    /// 保单持有人
    owner: address,
    /// 保险覆盖金额 (MIST)
    coverage_amount: u64,
    /// 已支付保费
    premium_paid: u64,
    /// 保险等级
    tier: u8,
    /// 生效时间
    start_time_ms: u64,
    /// 到期时间
    expiry_time_ms: u64,
    /// 是否活跃
    is_active: bool,
    /// 上次理赔时间
    last_claim_time_ms: u64,
    /// 剩余可赔付额度
    remaining_coverage: u64,
}

/// 管理员权限
public struct InsuranceAdminCap has key, store {
    id: UID,
}

// === Events ===

/// 保单创建事件
public struct PolicyCreated has copy, drop {
    policy_id: ID,
    owner: address,
    tier: u8,
    coverage_amount: u64,
    premium_paid: u64,
    expiry_time_ms: u64,
}

/// 理赔处理事件
public struct ClaimProcessed has copy, drop {
    policy_id: ID,
    owner: address,
    claim_amount: u64,
    payout_amount: u64,
    remaining_coverage: u64,
    timestamp_ms: u64,
}

/// 理赔拒绝事件
public struct ClaimDenied has copy, drop {
    policy_id: ID,
    owner: address,
    claim_amount: u64,
    reason: vector<u8>,
    timestamp_ms: u64,
}

/// 保单续保事件
public struct PolicyRenewed has copy, drop {
    policy_id: ID,
    owner: address,
    new_expiry_time_ms: u64,
    premium_paid: u64,
}

// === Init ===

fun init(ctx: &mut TxContext) {
    let admin_cap = InsuranceAdminCap { id: object::new(ctx) };
    transfer::transfer(admin_cap, ctx.sender());

    let pool = InsurancePool {
        id: object::new(ctx),
        pool_balance: balance::zero<SUI>(),
        admin: ctx.sender(),
        total_premiums_collected: 0,
        total_claims_paid: 0,
        active_policies: 0,
        total_policies_issued: 0,
        total_claims_denied: 0,
        base_premium_rate_bps: 500, // 5% 默认保费率
    };
    transfer::share_object(pool);
}

// === Core Functions ===

/// 获取报价: 根据覆盖金额和保险等级计算保费
public fun get_quote(
    pool: &InsurancePool,
    coverage_amount: u64,
    tier: u8,
): u64 {
    assert!(tier >= TIER_BASIC && tier <= TIER_PREMIUM, EInvalidCoverage);

    let base_rate = pool.base_premium_rate_bps;
    // 等级系数: basic=1x, standard=1.5x, premium=2x
    let tier_multiplier = if (tier == TIER_BASIC) {
        100
    } else if (tier == TIER_STANDARD) {
        150
    } else {
        200
    };

    // premium = coverage * base_rate * tier_multiplier / (BPS_BASE * 100)
    (coverage_amount * base_rate * tier_multiplier) / (BPS_BASE * 100)
}

/// 购买保险
public fun buy_insurance(
    pool: &mut InsurancePool,
    payment: Coin<SUI>,
    coverage_amount: u64,
    tier: u8,
    clock: &Clock,
    ctx: &mut TxContext,
): Policy {
    assert!(tier >= TIER_BASIC && tier <= TIER_PREMIUM, EInvalidCoverage);

    let premium = get_quote(pool, coverage_amount, tier);
    let payment_value = coin::value(&payment);
    assert!(payment_value >= premium, EInvalidPremium);

    // 收取保费到资金池
    let payment_balance = coin::into_balance(payment);
    balance::join(&mut pool.pool_balance, payment_balance);

    pool.total_premiums_collected = pool.total_premiums_collected + premium;
    pool.active_policies = pool.active_policies + 1;
    pool.total_policies_issued = pool.total_policies_issued + 1;

    let now_ms = clock.timestamp_ms();
    let expiry_ms = now_ms + DEFAULT_DURATION_MS;

    let policy = Policy {
        id: object::new(ctx),
        owner: ctx.sender(),
        coverage_amount,
        premium_paid: premium,
        tier,
        start_time_ms: now_ms,
        expiry_time_ms: expiry_ms,
        is_active: true,
        last_claim_time_ms: 0,
        remaining_coverage: coverage_amount,
    };

    event::emit(PolicyCreated {
        policy_id: object::id(&policy),
        owner: ctx.sender(),
        tier,
        coverage_amount,
        premium_paid: premium,
        expiry_time_ms: expiry_ms,
    });

    policy
}

/// 申请理赔
public fun claim(
    pool: &mut InsurancePool,
    policy: &mut Policy,
    claim_amount: u64,
    clock: &Clock,
    ctx: &mut TxContext,
): Coin<SUI> {
    let now_ms = clock.timestamp_ms();
    let sender = ctx.sender();

    // 验证保单
    assert!(policy.owner == sender, ENotPolicyOwner);
    assert!(policy.is_active, EPolicyNotActive);
    assert!(now_ms <= policy.expiry_time_ms, EPolicyExpired);

    // 验证冷却期
    if (policy.last_claim_time_ms > 0) {
        assert!(now_ms >= policy.last_claim_time_ms + CLAIM_COOLDOWN_MS, ECooldownNotMet);
    };

    // 验证理赔金额
    let max_payout = (policy.remaining_coverage * MAX_PAYOUT_BPS) / BPS_BASE;
    if (claim_amount > max_payout) {
        pool.total_claims_denied = pool.total_claims_denied + 1;
        event::emit(ClaimDenied {
            policy_id: object::id(policy),
            owner: sender,
            claim_amount,
            reason: b"claim_exceeds_coverage",
            timestamp_ms: now_ms,
        });
        abort EClaimTooLarge
    };

    // 验证资金池有足够余额
    assert!(balance::value(&pool.pool_balance) >= claim_amount, EInsufficientPool);

    // 执行赔付
    policy.last_claim_time_ms = now_ms;
    policy.remaining_coverage = policy.remaining_coverage - claim_amount;
    pool.total_claims_paid = pool.total_claims_paid + claim_amount;

    // 如果剩余覆盖为 0, 标记保单为非活跃
    if (policy.remaining_coverage == 0) {
        policy.is_active = false;
        pool.active_policies = pool.active_policies - 1;
    };

    event::emit(ClaimProcessed {
        policy_id: object::id(policy),
        owner: sender,
        claim_amount,
        payout_amount: claim_amount,
        remaining_coverage: policy.remaining_coverage,
        timestamp_ms: now_ms,
    });

    // 从资金池提取赔付金额
    let payout_balance = balance::split(&mut pool.pool_balance, claim_amount);
    coin::from_balance(payout_balance, ctx)
}

/// 续保
public fun renew(
    pool: &mut InsurancePool,
    policy: &mut Policy,
    payment: Coin<SUI>,
    clock: &Clock,
    ctx: &mut TxContext,
) {
    let sender = ctx.sender();
    assert!(policy.owner == sender, ENotPolicyOwner);

    let premium = get_quote(pool, policy.coverage_amount, policy.tier);
    let payment_value = coin::value(&payment);
    assert!(payment_value >= premium, EInvalidPremium);

    // 收取保费
    let payment_balance = coin::into_balance(payment);
    balance::join(&mut pool.pool_balance, payment_balance);
    pool.total_premiums_collected = pool.total_premiums_collected + premium;

    let now_ms = clock.timestamp_ms();
    let new_expiry = now_ms + DEFAULT_DURATION_MS;

    // 更新保单
    policy.expiry_time_ms = new_expiry;
    policy.is_active = true;
    policy.remaining_coverage = policy.coverage_amount;
    policy.premium_paid = policy.premium_paid + premium;

    event::emit(PolicyRenewed {
        policy_id: object::id(policy),
        owner: sender,
        new_expiry_time_ms: new_expiry,
        premium_paid: premium,
    });
}

// === View Functions ===

public fun pool_balance(pool: &InsurancePool): u64 {
    balance::value(&pool.pool_balance)
}

public fun pool_stats(pool: &InsurancePool): (u64, u64, u64, u64, u64) {
    (
        pool.total_premiums_collected,
        pool.total_claims_paid,
        pool.active_policies,
        pool.total_policies_issued,
        pool.total_claims_denied,
    )
}

public fun policy_coverage(policy: &Policy): u64 {
    policy.coverage_amount
}

public fun policy_remaining(policy: &Policy): u64 {
    policy.remaining_coverage
}

public fun policy_is_active(policy: &Policy): bool {
    policy.is_active
}

public fun policy_expiry(policy: &Policy): u64 {
    policy.expiry_time_ms
}

public fun policy_tier(policy: &Policy): u8 {
    policy.tier
}

// === Admin Functions ===

/// 管理员设置保费率
public fun set_premium_rate(
    pool: &mut InsurancePool,
    _: &InsuranceAdminCap,
    new_rate_bps: u64,
) {
    pool.base_premium_rate_bps = new_rate_bps;
}

/// 管理员注入资金到池子
public fun deposit_to_pool(
    pool: &mut InsurancePool,
    _: &InsuranceAdminCap,
    funds: Coin<SUI>,
) {
    let funds_balance = coin::into_balance(funds);
    balance::join(&mut pool.pool_balance, funds_balance);
}

/// 管理员从池子提取资金 (紧急情况)
public fun withdraw_from_pool(
    pool: &mut InsurancePool,
    _: &InsuranceAdminCap,
    amount: u64,
    ctx: &mut TxContext,
): Coin<SUI> {
    assert!(balance::value(&pool.pool_balance) >= amount, EInsufficientPool);
    let withdrawn = balance::split(&mut pool.pool_balance, amount);
    coin::from_balance(withdrawn, ctx)
}
