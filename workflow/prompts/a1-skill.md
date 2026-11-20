# Skill: Requirements Engineer (Autonomous Requirements Analysis & Specification Synthesis)

## Metadata
- **Name**: `requirements-engineer`
- **Version**: `1.2.0`
- **Author**: Automated Software Engineering Laboratory
- **Standard Alignment**: IEEE 830-1998 / ISO/IEC/IEEE 29148:2018 (Requirements Engineering)
- **Target Agents**: Claude Code, Antigravity, OpenAI Codex, and Autonomous LLM Harnesses
- **Description**: Transforms vague, buzzword-dense, or incomplete software ideas into structured, reviewable, testable Software Requirements Specifications (SRS), paired with an Assumptions & Open-Questions Register and an Empirical Validation Scorecard.

---

## 1. Purpose and Scope

### 1.1 Objective
The `requirements-engineer` skill provides an autonomous agent with a rigorous, repeatable methodology to extract, clarify, formalize, and validate software requirements from raw, ambiguous, or incomplete problem statements. The skill systematically eliminates ungrounded assumptions, isolates buzzwords, detects hidden contradictions, and enforces a verifiable "Definition of Ready" before software enters implementation.

### 1.2 Intended Users & Personas
- **Autonomous Coding Agents & Harvesters**: Uses the structured output as an invariant contract prior to code generation, preventing hallucinated implementations.
- **Software Architects & Lead Engineers**: Reviews architectural trade-offs, non-functional constraints, and system boundaries.
- **Product Managers & Stakeholders**: Inspects the Open-Questions Register to resolve business, operational, and regulatory ambiguities.

### 1.3 Invocation Conditions
Invoke this skill whenever:
1. A new project, epic, or feature is initiated from an informal brief, chat message, transcript, or buzzword-heavy prompt.
2. An existing software idea requires decomposing into verifiable Functional Requirements (FRs) and Non-Functional Requirements (NFRs).
3. System boundaries, threat models, and interface constraints must be audited prior to implementation.

### 1.4 Exclusions & Strict Boundaries
- **NON-GOAL: Code Implementation**: This skill **strictly produces requirements artifacts**. It does NOT write production source code, unit tests, or scaffolding.
- **NON-GOAL: Autonomous Decision on Subjective Business Trade-offs**: The agent must never arbitrarily pick a winner between conflicting business priorities (e.g., choosing cost minimization over zero-latency) without documenting it as an explicit open question or assumption.
- **NON-GOAL: Guessing Stakeholder Intent**: Unsupported buzzwords (e.g., "enterprise-grade", "sovereign", "fully autonomous") must not be silently expanded into definitive architectural requirements without evidence or explicit classification.

---

## 2. Inputs & Ambiguity Triage

### 2.1 Input Specification
The skill consumes two classes of inputs:

| Input Category | Field Name | Type | Requirement Level | Description |
|---|---|---|---|---|
| **Primary** | `raw_problem_statement` | Text / Markdown | **Mandatory** | The verbatim software pitch, user brief, or meeting transcript. |
| **Primary** | `domain_context` | String | Optional | The application sector (e.g., FinTech, Healthcare, Autonomous Robotics, Developer Tools). If omitted, inferred and flagged. |
| **Supplementary**| `stakeholder_constraints` | Key-Value List | Optional | Explicit deadlines, budgets, compliance frameworks (e.g., HIPAA, GDPR, DPDP Act 2023). |
| **Supplementary**| `target_environment` | Key-Value List | Optional | Hardware targets, operating systems, cloud providers, or air-gapped constraints. |
| **Tooling** | `available_mcp_servers` | List of URIs | Optional | Accessible Model Context Protocol (MCP) server endpoints for external grounding. |

### 2.2 Triage Rules for Ambiguous, Missing, or Conflicting Inputs
The agent must execute deterministic triage routines upon receiving inputs:

1. **Buzzword Deconstruction Rule**:
   Every vague superlative or tech buzzword (e.g., "enterprise-grade", "hyper-scalable", "military-grade privacy", "model-agnostic") must be isolated into the **Lexical Triage Matrix**. The agent classifies the buzzword into:
   - *Measurable Metric Needed*: Needs explicit numeric bounds (e.g., "hyper-scalable" -> target QPS, p99 latency).
   - *Architectural Constraint*: Needs protocol/layer definition (e.g., "model-agnostic" -> provider abstraction interface).
   - *Marketing Fluff*: No technical requirement implied; flagged for elimination.

2. **Missing Information Protocol**:
   If a core dimension is missing (e.g., user identity, storage durability, deployment topology, authorization model), the agent:
   - Must NOT invent or hallucinate the default silently.
   - Must log the item into the `Assumptions & Open-Questions Register`.
   - May propose a *Standard Baseline Assumption* tagged explicitly as `[INFERRED - UNCONFIRMED]`.

3. **Conflicting Stakeholder Claims Protocol**:
   When inputs contain mutually exclusive requirements (e.g., "zero cloud dependencies" vs "global model sync with centralized telemetry", or "fully autonomous action execution" vs "zero-risk enterprise compliance"):
   - The agent flags the collision as `[CRITICAL_CONFLICT]`.
   - Both claims are documented side-by-side with an Impact Analysis.
   - The requirement is marked `[BLOCKED_PENDING_CLARIFICATION]`.

4. **Unavailable Stakeholder Fallback**:
   When real-time clarification is unavailable (e.g., batch autonomous mode), the agent generates a bifurcated specification:
   - **Branch A (Conservative/Minimalist)**: Assumes strict air-gapping, least privilege, local storage.
   - **Branch B (Permissive/Extended)**: Assumes cloud connectivity, distributed coordination.
   - Both branches are detailed in the Register for asynchronous sign-off.

---

## 3. Requirements Analysis Framework

Every extracted requirement must be mapped to a standardized identifier and taxonomy:

### 3.1 Taxonomy and Identifiers
- `ACT-xxx`: System & Human Actors (Primary, Secondary, Environmental).
- `FR-xxx`: Functional Requirements (Input -> Processing -> Output).
- `NFR-xxx`: Non-Functional Requirements (Performance, Security, Privacy, Observability, Portability).
- `CON-xxx`: Hard Environmental, Legal, or Architectural Constraints.
- `ASM-xxx`: Documented Inferences and Assumptions.
- `DEP-xxx`: External Library, Hardware, Platform, or Network Dependencies.
- `RSK-xxx`: Technical, Security, Legal, or Operational Risks.
- `AC-xxx`: Verifiable Acceptance Criteria (Given-When-Then syntax).

### 3.2 Epistemological Status Tagging
Every single statement across the specification MUST carry one of the following four status tags:
1. `[CONFIRMED_FACT]`: Directly stated by the user/stakeholder in the problem brief.
2. `[EMPIRICALLY_GROUNDED]`: Derived and verified via an external tool or MCP server (e.g., standards spec, RFC, API schema).
3. `[INFERRED_ASSUMPTION]`: Logically necessary for system operation, proposed by the agent, but awaiting human sign-off.
4. `[UNRESOLVED_QUESTION]`: Missing information with multiple incompatible implementations; blocks implementation readiness.

### 3.3 Testability & Acceptance Criteria Formulation
All functional and non-functional requirements must culminate in at least one testable Acceptance Criterion using BDD (Behavior-Driven Development) formatting:
```gherkin
AC-[ID]-[SubID]:
Given: [Pre-condition & system state]
When:  [Specific stimulus or trigger event]
Then:  [Measurable, verifiable outcome within tolerance X]
```
*Prohibition*: Vague acceptance criteria such as "System performs quickly" or "Data is kept secure" are considered validation failures. Criteria must specify numeric bounds, cryptographic algorithms, or deterministic response codes.

---

## 4. Multi-Phase Analysis Workflow

The agent must execute the following ordered six-phase pipeline:

```
+-------------------------------------------------------------+
| Phase 1: Intake & Lexical Triage                            |
| Extract actors, raw statements, boundary terms, buzzwords   |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| Phase 2: Gap, Contradiction & Ambiguity Audit               |
| Identify missing dimensions, paradoxes, ungrounded claims   |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| Phase 3: External Context & MCP Tool Augmentation          |
| Query standards, RFCs, documentation via MCP tools          |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| Phase 4: Formal Requirements Synthesis (FR, NFR, CON, AC)   |
| Draft structured requirements with unique IDs and tags      |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| Phase 5: Gating & Definition-of-Ready (DoR) Audit           |
| Check completeness, consistency, traceability, testability  |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| Phase 6: Artifact Generation & Register Emission            |
| Synthesize SRS.md, Assumptions_Register.md, Summary.md      |
+-------------------------------------------------------------+
```

### Detailed Phase Specifications

#### Phase 1: Intake & Lexical Triage
1. Read the raw problem statement verbatim.
2. Extract all nouns (candidate actors, entities, data stores) and verbs (candidate operations).
3. Populate the **Lexical Buzzword Matrix**; isolate marketing buzzwords from technical specifications.

#### Phase 2: Gap, Contradiction & Ambiguity Audit
1. Audit against the **7 Core Systems Dimensions**:
   - (1) User Identity & Access Management
   - (2) Runtime Environment & Deployment Topology
   - (3) Model / Engine Execution Substrate
   - (4) Data Storage, Durability & Retention
   - (5) Security Perimeter & Cryptographic Controls
   - (6) Level of Autonomy & Human-in-the-Loop Safeguards
   - (7) Failure Recovery & Degraded Operation
2. Flag any missing dimension as `[UNRESOLVED_QUESTION]`.
3. Detect contradiction pairs (e.g., $C_1 \land C_2 \implies \bot$).

#### Phase 3: External Context & MCP Tool Augmentation
1. Identify technical claims requiring external verification (e.g., standard protocol definitions, local LLM execution runtimes, compliance frameworks).
2. Formulate targeted queries for connected MCP servers (e.g., querying local-first architecture patterns, Ollama/vLLM runtime specs, or ISO 27001 / DPDP requirements).
3. Capture tool output, parse evidence, and incorporate verified constraints under `[EMPIRICALLY_GROUNDED]`.
4. If tool call fails or times out, trigger the **MCP Failure Protocol** (Section 7.3).

#### Phase 4: Formal Requirements Synthesis
1. Formulate discrete, non-overlapping `FR-xxx` entries with clear Input, Processing, and Output.
2. Formulate `NFR-xxx` entries with ISO 25010 categorization and measurable SLA/SLO metrics.
3. Formulate `CON-xxx`, `DEP-xxx`, and `RSK-xxx` entries.
4. Generate corresponding `AC-xxx` test specifications.

#### Phase 5: Gating & Definition-of-Ready (DoR) Audit
1. Run the **Readiness Evaluator** on every requirement:
   - Is it uniquely identified?
   - Is it categorized and tagged with epistemological status?
   - Does it have at least one deterministic BDD acceptance criterion?
   - Are there unresolved dependencies or blocking open questions?
2. Mark requirement status: `IMPLEMENTATION_READY`, `CLARIFICATION_REQUIRED`, or `BLOCKED`.

#### Phase 6: Artifact Generation
1. Format and write the three mandatory deliverable artifacts (Section 5).
2. Emit the completion summary.

---

## 5. Required Output Artifacts

The skill produces three coordinated markdown artifacts using the naming pattern `<project_slug>_<artifact_type>.md`:

### 5.1 Artifact 1: `<project_slug>_SRS.md` (Software Requirements Specification)
Structure:
1. **Executive Summary & Scope Boundary**: System overview, in-scope capabilities, out-of-scope boundaries.
2. **Actor Catalog (`ACT-xxx`)**: Role definitions, permissions, environmental interaction.
3. **Functional Requirements (`FR-xxx`)**:
   - ID, Title, Description, Epistemological Tag.
   - Inputs, Processing Steps, Outputs.
   - Traceability links to Constraints, Risks, and Acceptance Criteria.
4. **Non-Functional Requirements (`NFR-xxx`)**:
   - ID, Category (Performance, Security, Privacy, Portability, Reliability).
   - Target Metric, Threshold, Measurement Method.
5. **System Constraints (`CON-xxx`) & Dependencies (`DEP-xxx`)**: Hardware, platform, legal, and operational constraints.
6. **Risk & Threat Model (`RSK-xxx`)**: Technical, operational, and ethical/autonomous failure modes with mitigations.
7. **Acceptance Criteria Matrix (`AC-xxx`)**: Gherkin/BDD scenarios for verification.

### 5.2 Artifact 2: `<project_slug>_Assumptions_Register.md`
Structure:
1. **Explicit Confirmed Facts Register**: Verifiable assertions directly from the client.
2. **Inferred Assumptions Register (`ASM-xxx`)**:
   - Inferred requirement, rationale, source inference, confidence rating (Low/Medium/High).
   - Downstream impact if invalidated.
3. **Open-Questions & Clarification Register (`OQ-xxx`)**:
   - Question ID, Target Stakeholder persona, Ambiguity being addressed.
   - Proposed Default Behavior (if no answer provided).
   - Blocking Status (Blocks Architecture / Blocks Implementation / Non-blocking).

### 5.3 Artifact 3: `<project_slug>_Validation_Summary.md`
Structure:
1. **Readiness Scorecard**:
   - Total Requirements extracted.
   - Percentage Implementation-Ready vs Clarification-Required vs Blocked.
2. **Quality Checklist Audit**:
   - Completeness (0-100%).
   - Consistency & Contradiction Check (Pass/Fail).
   - Testability (Percentage of requirements with deterministic ACs).
   - Traceability Coverage (Percentage of FRs mapped to Actors and ACs).
3. **MCP Tool Augmentation Log**: Exact records of external tool calls, schemas, and delta impacts.
4. **Final Recommendation**: Clear go/no-go verdict for sprint planning or architectural spikes.

---

## 6. Verification and Validation Gates

Before marking any requirement as `IMPLEMENTATION_READY`, the agent must verify five strict invariant checks:

| Gate | Validation Rule | Verification Criteria | Remediation if Failed |
|---|---|---|---|
| **1. Completeness** | No dangling references or unmapped inputs. | Every input noun/verb must map to an Actor, FR, NFR, CON, or Buzzword triage entry. | Append missing elements or file an Open Question. |
| **2. Consistency** | Zero logical contradictions. | No requirement $R_A$ can demand an operational mode that violates constraint $C_B$. | Flag collision as `[CRITICAL_CONFLICT]`; mark both `BLOCKED`. |
| **3. Traceability** | Bidirectional link graph. | Each `FR` must link upstream to an `ACT` and downstream to an `AC`. | Generate missing test criteria or discard orphaned requirements. |
| **4. Feasibility** | Physical & computational viability. | Proposed constraints must not require impossible physical bounds (e.g., sub-millisecond local LLM inference on low-power IoT). | Demote to `[UNFEASIBLE_CONSTRAINED]`; request hardware clarification. |
| **5. Testability** | Falsifiability & determinism. | Acceptance criteria must evaluate to a boolean pass/fail without subjective human judgment. | Rewrite criteria into measurable numeric or status thresholds. |

---

## 7. Failure Handling & Anti-Hallucination Guardrails

### 7.1 Strict Anti-Hallucination Invariant
> **THE CARDINAL RULE**: The agent MUST NEVER silently convert an unsupported assumption into a confirmed requirement. If the agent makes an inference to complete a system design, it must be prominently tagged `[INFERRED_ASSUMPTION]`, indexed in the Assumptions Register, and flagged with an associated Open Question.

### 7.2 Human Intervention Triggers
The agent must pause autonomous progression and request human stakeholder intervention when:
1. A regulatory or legal violation is detected (e.g., autonomous data extraction violating data residency laws or privacy statutes).
2. A critical unresolvable contradiction between stakeholder objectives exists ($P \land \neg P$).
3. The percentage of Implementation-Ready requirements falls below 50% due to pervasive input ambiguity.

### 7.3 Model Context Protocol (MCP) Failure Protocol
When invoking MCP tools for context augmentation:
1. **Timeout Handling**: Tool calls exceeding 5000ms must be aborted. The agent logs `MCP_TIMEOUT` and falls back to static reasoning with an explicit `[UNVERIFIED_EXTERNAL_TOOL]` tag.
2. **Service Unavailable / Error Handling**: If an MCP endpoint returns 4xx/5xx or protocol errors, the agent records the error trace, continues pipeline execution using conservative offline assumptions, and marks downstream dependencies as `CLARIFICATION_REQUIRED`.
3. **Conflicting External Evidence**: If an external MCP result contradicts the stakeholder brief, the stakeholder brief takes precedence for intent, but the conflict is documented as an architectural risk (`RSK-xxx`).

---

## 8. Side Quest: Model Context Protocol (MCP) Integration Specification

### 8.1 Selection Rationale
- **Selected MCP Server**: `deepwiki` (Standard Public Documentation & Knowledge Retrieval MCP Server)
- **Primary Tool**: `ask_wiki_question` / `read_wiki_contents`
- **Documentation Link**: `https://github.com/modelcontextprotocol/servers/tree/main/src/deepwiki` (Model Context Protocol Official Registry)
- **Engineering Justification**: Requirements engineering cannot occur in an epistemic vacuum. When evaluating vague technical requirements (e.g., "sovereign local-first agent harness"), the agent must ground buzzwords against verified architectural patterns, protocol RFCs, and runtime capabilities (e.g., local model runtime memory footprint, sandboxing isolation semantics, and local vector indexing protocols) rather than relying on stale parametric memory.

### 8.2 Standard Invocation Procedure
1. **Discovery**: Agent calls `tools/list` to inspect available MCP capabilities.
2. **Parameter Preparation**: Formulate a structured JSON query targeting the technical specification.
   ```json
   {
     "ServerName": "deepwiki",
     "ToolName": "ask_wiki_question",
     "Arguments": {
       "repo_name": "local-first-software/protocols",
       "question": "What are the core requirements and invariants for local-first software state synchronization and offline data durability?"
     }
   }
   ```
3. **Consumption & Parsing**: Agent parses the response JSON, extracts factual assertions, and incorporates them with citation into the SRS.

### 8.3 Epistemological Boundary Matrix
The agent strictly enforces three distinct boundary tiers:
1. **Tier 1 (Client Authority)**: Business goals, acceptable cost bounds, user personas. *Established exclusively from stakeholder inputs.*
2. **Tier 2 (Empirical Technical Evidence)**: API specs, RFC standards, latency limits, cryptographic primitive strengths. *Augmented and supported by MCP tool responses.*
3. **Tier 3 (Unresolved Architectural Decisions)**: Deployment preferences, failover policies, operational tolerances. *Requires explicit human stakeholder confirmation.*

---
*End of Skill Specification: `requirements-engineer`*
