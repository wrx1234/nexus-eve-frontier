/// Jarvis Vault — Agent 资金管理合约
/// 支持存入/取出 SUI，记录所有交易事件到链上
/// 事件可被 Walrus 索引，实现完整审计追踪
module jarvis::vault {
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;
    use sui::event;
    use sui::balance::{Self, Balance};

    // ==================== 错误码 ====================
    const ENotOwner: u64 = 0;
    const EInsufficientBalance: u64 = 1;
    const EExceedsLimit: u64 = 2;
    const EPaused: u64 = 3;

    // ==================== 事件 ====================
    
    /// 存入事件
    public struct DepositEvent has copy, drop {
        vault_id: ID,
        amount: u64,
        sender: address,
        new_balance: u64,
    }

    /// 取出事件
    public struct WithdrawEvent has copy, drop {
        vault_id: ID,
        amount: u64,
        recipient: address,
        new_balance: u64,
    }

    /// 交易记录事件（Agent 执行 swap 后记录）
    public struct TradeEvent has copy, drop {
        vault_id: ID,
        action: vector<u8>,        // "buy" or "sell"
        from_token: vector<u8>,    // e.g. "SUI"
        to_token: vector<u8>,      // e.g. "USDC"
        amount_in: u64,
        amount_out: u64,
        tx_digest: vector<u8>,     // 交易哈希
        timestamp: u64,
    }

    /// 策略信号事件（AI 决策记录）
    public struct StrategyEvent has copy, drop {
        vault_id: ID,
        signal: vector<u8>,        // "buy", "sell", "hold"
        confidence: u64,           // 0-100
        reasoning: vector<u8>,     // AI 分析原因
        timestamp: u64,
    }

    /// 风控事件
    public struct RiskEvent has copy, drop {
        vault_id: ID,
        event_type: vector<u8>,    // "stop_loss", "limit_reached", "emergency_stop"
        details: vector<u8>,
        timestamp: u64,
    }

    // ==================== 对象 ====================

    /// Agent 资金保险库
    public struct Vault has key, store {
        id: UID,
        owner: address,
        balance: Balance<SUI>,
        // 配置
        single_trade_limit: u64,   // 单笔限额（MIST）
        daily_limit: u64,          // 日限额（MIST）
        paused: bool,              // 暂停开关
        // 统计
        total_deposits: u64,
        total_withdrawals: u64,
        trade_count: u64,
    }

    /// Vault 管理权限 Cap
    public struct VaultCap has key, store {
        id: UID,
        vault_id: ID,
    }

    // ==================== 创建 ====================

    /// 创建新的 Vault
    public entry fun create_vault(
        single_trade_limit: u64,
        daily_limit: u64,
        ctx: &mut TxContext,
    ) {
        let vault = Vault {
            id: object::new(ctx),
            owner: ctx.sender(),
            balance: balance::zero<SUI>(),
            single_trade_limit,
            daily_limit,
            paused: false,
            total_deposits: 0,
            total_withdrawals: 0,
            trade_count: 0,
        };

        let vault_id = object::id(&vault);
        
        let cap = VaultCap {
            id: object::new(ctx),
            vault_id,
        };

        transfer::public_transfer(cap, ctx.sender());
        transfer::public_share_object(vault);
    }

    // ==================== 存取 ====================

    /// 存入 SUI
    public entry fun deposit(
        vault: &mut Vault,
        coin: Coin<SUI>,
        ctx: &TxContext,
    ) {
        let amount = coin.value();
        let coin_balance = coin.into_balance();
        vault.balance.join(coin_balance);
        vault.total_deposits = vault.total_deposits + amount;

        event::emit(DepositEvent {
            vault_id: object::id(vault),
            amount,
            sender: ctx.sender(),
            new_balance: vault.balance.value(),
        });
    }

    /// 取出 SUI（仅 owner）
    public entry fun withdraw(
        vault: &mut Vault,
        _cap: &VaultCap,
        amount: u64,
        ctx: &mut TxContext,
    ) {
        assert!(!vault.paused, EPaused);
        assert!(vault.balance.value() >= amount, EInsufficientBalance);

        let coin = coin::from_balance(vault.balance.split(amount), ctx);
        vault.total_withdrawals = vault.total_withdrawals + amount;

        event::emit(WithdrawEvent {
            vault_id: object::id(vault),
            amount,
            recipient: ctx.sender(),
            new_balance: vault.balance.value(),
        });

        transfer::public_transfer(coin, ctx.sender());
    }

    // ==================== 事件记录 ====================

    /// 记录交易事件（Agent 调用）
    public entry fun log_trade(
        vault: &mut Vault,
        _cap: &VaultCap,
        action: vector<u8>,
        from_token: vector<u8>,
        to_token: vector<u8>,
        amount_in: u64,
        amount_out: u64,
        tx_digest: vector<u8>,
        timestamp: u64,
    ) {
        vault.trade_count = vault.trade_count + 1;

        event::emit(TradeEvent {
            vault_id: object::id(vault),
            action,
            from_token,
            to_token,
            amount_in,
            amount_out,
            tx_digest,
            timestamp,
        });
    }

    /// 记录策略信号
    public entry fun log_strategy(
        vault: &Vault,
        _cap: &VaultCap,
        signal: vector<u8>,
        confidence: u64,
        reasoning: vector<u8>,
        timestamp: u64,
    ) {
        event::emit(StrategyEvent {
            vault_id: object::id(vault),
            signal,
            confidence,
            reasoning,
            timestamp,
        });
    }

    /// 记录风控事件
    public entry fun log_risk(
        vault: &Vault,
        _cap: &VaultCap,
        event_type: vector<u8>,
        details: vector<u8>,
        timestamp: u64,
    ) {
        event::emit(RiskEvent {
            vault_id: object::id(vault),
            event_type,
            details,
            timestamp,
        });
    }

    // ==================== 管理 ====================

    /// 暂停/恢复
    public entry fun set_paused(
        vault: &mut Vault,
        _cap: &VaultCap,
        paused: bool,
    ) {
        vault.paused = paused;
    }

    /// 修改限额
    public entry fun set_limits(
        vault: &mut Vault,
        _cap: &VaultCap,
        single_trade_limit: u64,
        daily_limit: u64,
    ) {
        vault.single_trade_limit = single_trade_limit;
        vault.daily_limit = daily_limit;
    }

    // ==================== 查询 ====================

    public fun get_balance(vault: &Vault): u64 {
        vault.balance.value()
    }

    public fun get_owner(vault: &Vault): address {
        vault.owner
    }

    public fun is_paused(vault: &Vault): bool {
        vault.paused
    }

    public fun get_trade_count(vault: &Vault): u64 {
        vault.trade_count
    }

    public fun get_single_trade_limit(vault: &Vault): u64 {
        vault.single_trade_limit
    }

    public fun get_daily_limit(vault: &Vault): u64 {
        vault.daily_limit
    }
}
