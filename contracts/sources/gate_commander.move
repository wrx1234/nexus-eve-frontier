/// EVE Commander - Smart Gate 扩展
/// AI 驱动的跳跃门权限管理
///
/// 支持多种规则组合:
/// - TribeRule: 按部落过滤
/// - AllowlistRule: 白名单
/// - TollRule: 收费通行（记录到链上）
/// - TimeRule: 时间段控制
///
/// 所有操作发出事件，供 Agent 链下监听分析
module eve_commander::gate_commander;

use eve_commander::config::{Self, AdminCap, CAuth, ExtensionConfig};
use sui::clock::Clock;
use sui::event;
use world::{character::Character, gate::{Self, Gate}};

// === Errors ===
#[error(code = 0)]
const EAccessDenied: vector<u8> = b"Character does not meet gate access rules";
#[error(code = 1)]
const ENoGateConfig: vector<u8> = b"Missing GateCommanderConfig on ExtensionConfig";
#[error(code = 2)]
const EExpiryOverflow: vector<u8> = b"Expiry timestamp overflow";
#[error(code = 3)]
const EGateClosed: vector<u8> = b"Gate is currently closed by time rule";
#[error(code = 4)]
const ECharacterNotAllowed: vector<u8> = b"Character not on allowlist";

// === Config Structs ===

/// 门禁主配置
public struct GateCommanderConfig has drop, store {
    /// 允许的部落 ID (0 = 不限制)
    allowed_tribe: u32,
    /// 通行证有效期 (毫秒)
    permit_duration_ms: u64,
    /// 是否启用白名单模式
    allowlist_enabled: bool,
    /// 是否启用时间控制
    time_control_enabled: bool,
    /// 开放时间段 (UTC timestamp ms)
    open_from_ms: u64,
    open_until_ms: u64,
    /// 统计: 总通行次数
    total_permits_issued: u64,
    /// 统计: 总拒绝次数
    total_denials: u64,
}

/// 白名单 (存储 character ID 列表)
public struct AllowlistConfig has drop, store {
    /// 允许的 character tribe IDs
    allowed_tribes: vector<u32>,
}

/// Dynamic field key
public struct GateConfigKey has copy, drop, store {}
public struct AllowlistKey has copy, drop, store {}

// === Events ===

/// 通行证签发事件 - Agent 监听用于流量分析
public struct PermitIssuedEvent has copy, drop {
    gate_id: ID,
    character_id: ID,
    character_tribe: u32,
    timestamp_ms: u64,
    expires_at_ms: u64,
}

/// 访问被拒事件 - Agent 监听用于威胁检测
public struct AccessDeniedEvent has copy, drop {
    gate_id: ID,
    character_id: ID,
    character_tribe: u32,
    reason: vector<u8>,
    timestamp_ms: u64,
}

/// 配置更新事件
public struct ConfigUpdatedEvent has copy, drop {
    gate_id: ID,
    allowed_tribe: u32,
    permit_duration_ms: u64,
    allowlist_enabled: bool,
    time_control_enabled: bool,
}

// === View Functions ===

public fun get_config(extension_config: &ExtensionConfig): &GateCommanderConfig {
    assert!(extension_config.has_rule<GateConfigKey>(GateConfigKey {}), ENoGateConfig);
    extension_config.borrow_rule<GateConfigKey, GateCommanderConfig>(GateConfigKey {})
}

public fun total_permits(extension_config: &ExtensionConfig): u64 {
    let cfg = get_config(extension_config);
    cfg.total_permits_issued
}

public fun total_denials(extension_config: &ExtensionConfig): u64 {
    let cfg = get_config(extension_config);
    cfg.total_denials
}

// === Core Function ===

/// AI Commander 签发跳跃通行证
/// 根据配置的规则组合判断是否允许通行
public fun issue_jump_permit(
    extension_config: &mut ExtensionConfig,
    admin_cap: &AdminCap,
    source_gate: &Gate,
    destination_gate: &Gate,
    character: &Character,
    clock: &Clock,
    ctx: &mut TxContext,
) {
    assert!(extension_config.has_rule<GateConfigKey>(GateConfigKey {}), ENoGateConfig);

    let now_ms = clock.timestamp_ms();
    let char_tribe = character.tribe();
    let char_id = object::id(character);

    // 获取可变配置引用来更新统计
    let cfg = config::borrow_rule_mut<GateConfigKey, GateCommanderConfig>(
        extension_config,
        admin_cap,
        GateConfigKey {},
    );

    // 规则 1: 时间控制
    if (cfg.time_control_enabled) {
        if (now_ms < cfg.open_from_ms || now_ms > cfg.open_until_ms) {
            cfg.total_denials = cfg.total_denials + 1;
            event::emit(AccessDeniedEvent {
                gate_id: gate::id(source_gate),
                character_id: char_id,
                character_tribe: char_tribe,
                reason: b"gate_closed_time_rule",
                timestamp_ms: now_ms,
            });
            abort EGateClosed
        };
    };

    // 规则 2: 部落过滤
    if (cfg.allowed_tribe != 0) {
        if (char_tribe != cfg.allowed_tribe) {
            cfg.total_denials = cfg.total_denials + 1;
            event::emit(AccessDeniedEvent {
                gate_id: gate::id(source_gate),
                character_id: char_id,
                character_tribe: char_tribe,
                reason: b"tribe_not_allowed",
                timestamp_ms: now_ms,
            });
            abort EAccessDenied
        };
    };

    // 规则 3: 白名单 (检查 tribes 列表)
    if (cfg.allowlist_enabled) {
        assert!(
            extension_config.has_rule<AllowlistKey>(AllowlistKey {}),
            ECharacterNotAllowed,
        );
        let allowlist = extension_config.borrow_rule<AllowlistKey, AllowlistConfig>(AllowlistKey {});
        let mut found = false;
        let len = vector::length(&allowlist.allowed_tribes);
        let mut i = 0u64;
        while (i < len) {
            if (*vector::borrow(&allowlist.allowed_tribes, i) == char_tribe) {
                found = true;
                break
            };
            i = i + 1;
        };
        if (!found) {
            // 需要重新获取可变引用更新统计
            let cfg2 = config::borrow_rule_mut<GateConfigKey, GateCommanderConfig>(
                extension_config,
                admin_cap,
                GateConfigKey {},
            );
            cfg2.total_denials = cfg2.total_denials + 1;
            event::emit(AccessDeniedEvent {
                gate_id: gate::id(source_gate),
                character_id: char_id,
                character_tribe: char_tribe,
                reason: b"not_on_allowlist",
                timestamp_ms: now_ms,
            });
            abort ECharacterNotAllowed
        };
    };

    // 所有规则通过 - 签发通行证
    let expiry_ms = cfg.permit_duration_ms;
    assert!(now_ms <= (0xFFFFFFFFFFFFFFFFu64 - expiry_ms), EExpiryOverflow);
    let expires_at_ms = now_ms + expiry_ms;

    cfg.total_permits_issued = cfg.total_permits_issued + 1;

    // 发出签发事件
    event::emit(PermitIssuedEvent {
        gate_id: gate::id(source_gate),
        character_id: char_id,
        character_tribe: char_tribe,
        timestamp_ms: now_ms,
        expires_at_ms,
    });

    // 调用 world::gate 签发 JumpPermit
    gate::issue_jump_permit<CAuth>(
        source_gate,
        destination_gate,
        character,
        config::c_auth(),
        expires_at_ms,
        ctx,
    );
}

// === Admin Functions ===

/// 设置门禁主配置
public fun set_gate_config(
    extension_config: &mut ExtensionConfig,
    admin_cap: &AdminCap,
    allowed_tribe: u32,
    permit_duration_ms: u64,
    allowlist_enabled: bool,
    time_control_enabled: bool,
    open_from_ms: u64,
    open_until_ms: u64,
) {
    config::set_rule<GateConfigKey, GateCommanderConfig>(
        extension_config,
        admin_cap,
        GateConfigKey {},
        GateCommanderConfig {
            allowed_tribe,
            permit_duration_ms,
            allowlist_enabled,
            time_control_enabled,
            open_from_ms,
            open_until_ms,
            total_permits_issued: 0,
            total_denials: 0,
        },
    );

    event::emit(ConfigUpdatedEvent {
        gate_id: @0x0.to_id(),
        allowed_tribe,
        permit_duration_ms,
        allowlist_enabled,
        time_control_enabled,
    });
}

/// 设置白名单
public fun set_allowlist(
    extension_config: &mut ExtensionConfig,
    admin_cap: &AdminCap,
    allowed_tribes: vector<u32>,
) {
    config::set_rule<AllowlistKey, AllowlistConfig>(
        extension_config,
        admin_cap,
        AllowlistKey {},
        AllowlistConfig { allowed_tribes },
    );
}
