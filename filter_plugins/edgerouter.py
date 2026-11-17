from typing import NotRequired, TypedDict

type ConfigValue = str | int | "ConfigTree"
type ConfigTree = dict[str, ConfigValue]


class AddrPort(TypedDict, total=False):
    address: str
    port: int | str


class Rule(TypedDict):
    action: str
    description: NotRequired[str]
    log: NotRequired[bool]
    protocol: NotRequired[str]
    destination: NotRequired[AddrPort]
    source: NotRequired[AddrPort]
    state: NotRequired[list[str]]


class Ruleset(TypedDict):
    default_action: str
    description: NotRequired[str]
    rules: NotRequired[list[Rule]]


class FilterModule:
    """Filters for building EdgeOS/VyOS-style firewall config trees"""

    def filters(self):
        return {
            "fw_ruleset_tree": self.fw_ruleset_tree,
        }

    def fw_rule_tree(self, rule: Rule) -> ConfigTree:
        tree: ConfigTree = {}

        tree["action"] = rule["action"]
        if "description" in rule:
            tree["description"] = f'"{rule["description"]}"'
        if not rule.get("log", True):
            tree["log"] = "disable"
        if "protocol" in rule:
            tree["protocol"] = rule["protocol"]

        for field in ("destination", "source"):
            if field not in rule:
                continue
            sub: ConfigTree = {}
            sub.update(rule[field])
            tree[field] = sub

        if "state" in rule:
            tree["state"] = {state: "enable" for state in rule["state"]}

        return tree

    def fw_ruleset_tree(self, ruleset: Ruleset) -> ConfigTree:
        tree: ConfigTree = {"default-action": ruleset["default_action"]}

        if "description" in ruleset:
            tree["description"] = f'"{ruleset["description"]}"'

        for index, rule in enumerate(ruleset.get("rules", []), start=1):
            tree[f"rule {index * 10}"] = self.fw_rule_tree(rule)

        return tree
