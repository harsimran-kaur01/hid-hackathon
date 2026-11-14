from typing import Dict, Any

def make_decision(spoof: Dict[str, Any], identity: Dict[str, Any]) -> Dict[str, str]:
    """
    Core decision matrix.
    """
    spoof_label = spoof.get("label", "uncertain")
    identity_name = identity.get("name")
    similarity = identity.get("similarity", 0.0)

    # 1. Spoof detected → always DENY
    if spoof_label == "spoof":
        return {
            "decision": "DENY",
            "reason": "Spoof attack detected"
        }

    # 2. Uncertain liveness
    if spoof_label == "uncertain":
        return {
            "decision": "STEP_UP",
            "reason": "Liveness uncertain – please try again"
        }

    # 3. Genuine face
    if spoof_label == "genuine":
        if identity_name is not None and similarity >= 0.70:
            return {
                "decision": "ALLOW",
                "reason": f"Live person verified as {identity_name}"
            }
        elif identity_name is None or similarity < 0.55:
            return {
                "decision": "DENY",
                "reason": "Identity not recognized"
            }
        else:
            return {
                "decision": "STEP_UP",
                "reason": "Identity uncertain – additional verification required"
            }

    # Fallback
    return {
        "decision": "STEP_UP",
        "reason": "Unable to reach confident decision"
    }