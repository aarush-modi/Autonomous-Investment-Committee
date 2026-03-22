# Committee Decision: {{ ticker }}

**Date:** {{ date }}
**Hypothesis:** {{ hypothesis }}

---

## Agent Contributions

{% for agent_name, output in agent_outputs.items() %}
### {{ agent_name }}

{{ output }}

{% endfor %}

---

## Chair's Synthesis

{{ chair_synthesis }}

---

## Final Decision

**Recommendation:** {{ recommendation }}
**Conviction Level:** {{ conviction }}

{{ reasoning }}

---

*Decision reached by autonomous investment committee with {{ agent_outputs | length }} contributing agents.*
