"""
Phase 6, Step 1: Explicit Sock Shop service dependency map.

This is the real, documented microservices-demo (Sock Shop)
architecture - not inferred from our data, so we state that clearly.
Source: microservices-demo/microservices-demo reference architecture.
"""

# service -> services it directly calls
SOCK_SHOP_DEPENDENCIES = {
    "front-end": ["orders", "carts", "catalogue", "user", "shipping"],
    "orders": ["orders-db", "carts", "user", "payment", "shipping"],
    "carts": ["carts-db"],
    "catalogue": ["catalogue-db"],
    "user": ["user-db"],
    "shipping": ["rabbitmq"],
    "queue-master": ["rabbitmq"],
    "rabbitmq": ["rabbitmq-exporter"],
    "payment": [],
    "session-db": [],
}


def get_related_services(service: str) -> set:
    """Return a service plus everything it directly depends on,
    AND everything that directly depends on it (both directions -
    a downstream caller's symptom should be able to point back
    at what it calls, and vice versa)."""
    related = {service}
    related.update(SOCK_SHOP_DEPENDENCIES.get(service, []))
    for caller, callees in SOCK_SHOP_DEPENDENCIES.items():
        if service in callees:
            related.add(caller)
    return related

def get_downstream_dependencies(service: str) -> set:
    """Return a service plus ONLY what it directly depends on -
    never services that call it. Used for corroboration, so an
    upstream gateway's generic errors can't leak into every
    service it happens to call."""
    related = {service}
    related.update(SOCK_SHOP_DEPENDENCIES.get(service, []))
    return related



if __name__ == "__main__":
    # Quick check against what we've already observed
    for svc in ["orders", "catalogue", "user"]:
        print(f"{svc} -> related: {sorted(get_related_services(svc))}")
