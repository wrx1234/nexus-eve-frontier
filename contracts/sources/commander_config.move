/// EVE Commander 共享配置模块
/// 基于 builder-scaffold 的 config.move 模式
/// 提供 AdminCap + ExtensionConfig + CAuth witness
module eve_commander::config;

use sui::dynamic_field as df;

/// 共享配置对象，各扩展模块通过 dynamic field 挂载自己的规则
public struct ExtensionConfig has key {
    id: UID,
}

/// 管理员权限
public struct AdminCap has key, store {
    id: UID,
}

/// Commander Auth witness - 用于 authorize_extension
public struct CAuth has drop {}

fun init(ctx: &mut TxContext) {
    let admin_cap = AdminCap { id: object::new(ctx) };
    transfer::transfer(admin_cap, ctx.sender());

    let config = ExtensionConfig { id: object::new(ctx) };
    transfer::share_object(config);
}

// === Dynamic field helpers ===

public fun has_rule<K: copy + drop + store>(config: &ExtensionConfig, key: K): bool {
    df::exists_(&config.id, key)
}

public fun borrow_rule<K: copy + drop + store, V: store>(config: &ExtensionConfig, key: K): &V {
    df::borrow(&config.id, key)
}

public fun borrow_rule_mut<K: copy + drop + store, V: store>(
    config: &mut ExtensionConfig,
    _: &AdminCap,
    key: K,
): &mut V {
    df::borrow_mut(&mut config.id, key)
}

public fun set_rule<K: copy + drop + store, V: store + drop>(
    config: &mut ExtensionConfig,
    _: &AdminCap,
    key: K,
    value: V,
) {
    if (df::exists_(&config.id, copy key)) {
        let _old: V = df::remove(&mut config.id, copy key);
    };
    df::add(&mut config.id, key, value);
}

public fun remove_rule<K: copy + drop + store, V: store>(
    config: &mut ExtensionConfig,
    _: &AdminCap,
    key: K,
): V {
    df::remove(&mut config.id, key)
}

/// Mint CAuth witness. Package-restricted.
public(package) fun c_auth(): CAuth {
    CAuth {}
}
