# Architectural Decision Records (ADRs)

This directory contains Architectural Decision Records (ADRs) for the AI Marketing Director project. ADRs document significant architectural decisions along with their context, alternatives considered, and consequences.

---

## What is an ADR?

An Architectural Decision Record captures:
- **Context**: The forces at play (technical, business, organizational)
- **Decision**: The chosen solution
- **Alternatives**: Other options that were considered
- **Consequences**: Both positive and negative outcomes of the decision

ADRs help teams:
- Understand why decisions were made
- Onboard new team members quickly
- Avoid revisiting settled decisions
- Learn from past choices

---

## ADR Status

- **Accepted**: Decision has been made and is currently implemented
- **Proposed**: Decision is under consideration
- **Deprecated**: Decision has been superseded by a newer ADR
- **Superseded**: Replaced by a specific newer ADR

---

## All ADRs

### Core Architecture

#### [ADR-001: Multiagent Department Architecture](./ADR-001-multiagent-department-architecture.md)
**Status**: Accepted | **Date**: 2025-11-03

**Decision**: Implement three-tier hierarchical multiagent architecture (Executive, Management, Specialist layers) with 14 specialized agents that collaborate like a real marketing department.

**Why Important**: This is the foundational architectural decision that defines the entire system. It represents a paradigm shift from "AI as tool" to "AI as autonomous department."

**Key Points**:
- 80%+ autonomous decision-making
- Agent-to-agent collaboration and peer review
- No central orchestrator (distributed decision-making)
- Mimics real organizational hierarchy

---

### Development Practices

#### [ADR-002: Test-Driven Development (TDD) Methodology](./ADR-002-tdd-methodology.md)
**Status**: Accepted and Enforced | **Date**: 2025-11-03

**Decision**: Mandate TDD (RED-GREEN-REFACTOR cycle) for all code with 5 required test types: Unit, Integration, E2E, Lint, and Regression.

**Why Important**: Ensures code quality, enables confident refactoring, and provides living documentation. Critical for autonomous system making business decisions.

**Key Points**:
- 81% test coverage achieved (exceeds 80% target)
- 72 passing tests in Phase 1-2
- Tests written BEFORE implementation
- CI/CD blocks deployment if tests fail

---

### Infrastructure

#### [ADR-003: Redis Message Bus Pattern](./ADR-003-redis-message-bus-pattern.md)
**Status**: Accepted and Implemented | **Date**: 2025-11-03

**Decision**: Use Redis Pub/Sub and Lists for agent communication rather than RabbitMQ, Kafka, or direct HTTP calls.

**Why Important**: Enables the multiagent architecture by providing low-latency, reliable inter-agent communication.

**Key Points**:
- < 10ms message delivery latency
- 100k+ messages/second capacity (far exceeds needs)
- Supports Pub/Sub (broadcast) and Queue (direct) patterns
- Already using Redis for caching (minimal new dependencies)

---

### AI/LLM Integration

#### [ADR-004: Multi-Provider LLM Abstraction Layer](./ADR-004-multi-provider-llm-abstraction.md)
**Status**: Accepted and Implemented | **Date**: 2025-11-03

**Decision**: Abstract LLM operations behind common interface supporting multiple providers (Anthropic, OpenAI) with automatic fallback.

**Why Important**: Eliminates vendor lock-in, enables cost optimization, and ensures reliability through automatic failover.

**Key Points**:
- Primary: Anthropic Claude (Opus, Sonnet, Haiku)
- Fallback: OpenAI (GPT-4, GPT-3.5-Turbo)
- Automatic provider failover on errors
- Task-based provider selection (quality vs cost vs speed)
- Centralized cost and usage tracking

---

### Error Handling

#### [ADR-005: Exception Wrapping Standard (Golden Rule #7)](./ADR-005-exception-wrapping-standard.md)
**Status**: Accepted and Enforced | **Date**: 2025-11-03

**Decision**: Always wrap external library exceptions in application-specific exception types at integration boundaries.

**Why Important**: Decouples application from external libraries, provides consistent error interface, preserves debugging context.

**Key Points**:
- `wrap_exception()` utility for consistent wrapping
- Exception hierarchy: MarketingDirectorError → Category → Specific
- Preserves original exception and stack trace
- Structured context for debugging
- Mandatory at all integration boundaries

---

## ADR Index by Topic

### Architecture & Design
- [ADR-001: Multiagent Department Architecture](./ADR-001-multiagent-department-architecture.md)

### Development Practices
- [ADR-002: Test-Driven Development Methodology](./ADR-002-tdd-methodology.md)
- [ADR-005: Exception Wrapping Standard](./ADR-005-exception-wrapping-standard.md)

### Infrastructure
- [ADR-003: Redis Message Bus Pattern](./ADR-003-redis-message-bus-pattern.md)

### AI/LLM
- [ADR-004: Multi-Provider LLM Abstraction](./ADR-004-multi-provider-llm-abstraction.md)

---

## ADR Template

When creating a new ADR, use this template:

```markdown
# ADR-XXX: [Title]

**Date**: YYYY-MM-DD
**Status**: [Proposed|Accepted|Deprecated|Superseded]
**Decision Makers**: [Team/Role]
**Related Documents**: [Links to related docs]

---

## Context

[Describe the forces at play: business requirements, technical constraints, etc.]

### Business Requirements
[What business needs drive this decision?]

### Technical Requirements
[What technical constraints or requirements apply?]

---

## Decision

[The decision that was made - be specific]

### Key Components
[Break down the decision into components if complex]

---

## Alternatives Considered

### Alternative 1: [Name]
**Pros**:
- [List advantages]

**Cons**:
- [List disadvantages]
- **Rejected**: [Why this wasn't chosen]

[Repeat for each alternative]

---

## Consequences

### Positive Consequences
✅ [List positive outcomes]

### Negative Consequences
⚠️ [List negative outcomes]

### Mitigation Strategies
[How negative consequences will be addressed]

---

## Implementation Details

[Technical specifics of how decision is implemented]

---

## References

[Links to relevant documentation, books, articles]

---

## Related ADRs

[Links to related ADRs]

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | YYYY-MM-DD | [Author] | Initial ADR |

---

**Status**: [Current status]
**Next Review**: [Date]
```

---

## Creating a New ADR

1. **Copy the template** above
2. **Number sequentially**: Next available number (ADR-006, ADR-007, etc.)
3. **Use descriptive title**: Clear, concise description of decision
4. **Document thoroughly**: Include context, alternatives, and consequences
5. **Get review**: Have team review before marking as "Accepted"
6. **Update this index**: Add entry to "All ADRs" section above

---

## ADR Naming Convention

- **File**: `ADR-XXX-kebab-case-title.md`
- **Examples**:
  - `ADR-001-multiagent-department-architecture.md`
  - `ADR-002-tdd-methodology.md`
  - `ADR-003-redis-message-bus-pattern.md`

---

## When to Create an ADR

Create an ADR when making decisions about:

✅ **Architecture**: System structure, component organization, patterns
✅ **Technology**: Major library or framework choices
✅ **Standards**: Coding standards, testing practices, conventions
✅ **Infrastructure**: Deployment, scaling, monitoring approaches
✅ **Integration**: How to integrate with external systems
✅ **Performance**: Optimization strategies with trade-offs
✅ **Security**: Security patterns and practices

❌ **Don't create ADRs for**:
- Minor implementation details
- Temporary workarounds
- Team process decisions (use different documentation)
- Obvious choices with no alternatives

---

## Statistics

**Total ADRs**: 5
**Accepted**: 5
**Proposed**: 0
**Deprecated**: 0

**By Category**:
- Architecture & Design: 1
- Development Practices: 2
- Infrastructure: 1
- AI/LLM: 1

**Last Updated**: 2025-11-03

---

## References

- **ADR Concept**: https://adr.github.io/
- **Book**: "Design It!" - Michael Keeling (Chapter on ADRs)
- **Article**: "Documenting Architecture Decisions" - Michael Nygard

---

*ADRs are living documents. They should be reviewed and updated as the system evolves.*
