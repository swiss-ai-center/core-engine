import {ElkNode} from 'elkjs';
import {FieldDescription} from 'models/ExecutionUnit';
import {Pipeline} from 'models/Pipeline';
import {Service} from 'models/Service';
import {Edge} from 'reactflow';
import {ServiceStatus} from '../../enums/serviceStatusEnum';

const nodeWidth = 250;
const nodeHeight = 200;
const edgeType = 'default';

const getPipelineSource = (field: FieldDescription): string | null => {
    const hint = field.format_hint;
    if (typeof hint === "object" && hint !== null && !Array.isArray(hint)) {
        const source = (hint as { pipeline_source?: unknown }).pipeline_source;
        if (typeof source === "string") return source;
    }
    return null;
};

export default function getNodesAndEdges(entity: Service | Pipeline | null) {
    let nodes: ElkNode[] = [];
    let edges: Edge[] = [];

    if (entity && entity instanceof Service) {
        const entryNode = generateEntryNode("service", entity.slug, entity.data_in_fields, entity.status);
        const serviceNode = generateNode(entity.slug, "service", entity.status, entity.id, entity.data_in_fields, entity.data_out_fields);
        const exitNode = generateExitNode(entity.slug, entity.data_out_fields);
        nodes = [entryNode, serviceNode, exitNode];
        for (let i = 0; i < entity.data_in_fields.length; i++) {
            edges.push({
                id: `${entryNode.id}-${entity.data_in_fields[i].name}-${serviceNode.id}-${entity.data_in_fields[i].name}`,
                source: entryNode.id,
                sourceHandle: `${entryNode.id}-${entity.data_in_fields[i].name}`,
                target: serviceNode.id,
                targetHandle: `${serviceNode.id}-${entity.data_in_fields[i].name}`,
                animated: false,
                type: edgeType,
            });
        }
        for (let i = 0; i < entity.data_out_fields.length; i++) {
            edges.push({
                id: `${serviceNode.id}-${entity.data_out_fields[i].name}-${exitNode.id}-${entity.data_out_fields[i].name}`,
                source: serviceNode.id,
                sourceHandle: `${serviceNode.id}-${entity.data_out_fields[i].name}`,
                target: exitNode.id,
                targetHandle: `${exitNode.id}-${entity.data_out_fields[i].name}`,
                animated: false,
                type: edgeType,
            });
        }
        edges = edges.flat();
        return {nodes, edges};
    }

    if (!entity) return {nodes: [], edges: []};

    const entryNode = generateEntryNode("pipeline", entity.slug, entity.data_in_fields, ServiceStatus.AVAILABLE);
    const exitNode = generateExitNode(entity.slug, entity.data_out_fields);
    nodes.push(entryNode);

    // Group steps by group_identifier. Steps without one are standalone.
    // group_identifier is present on the step when the pipeline was imported from another.
    const groups = new Map<string, { steps: any[], sourcePipelineSlug: string, subPipeline: any }>();
    const standaloneSteps: any[] = [];

    for (const step of entity.steps) {
        if (step.group_identifier) {
            if (!groups.has(step.group_identifier)) {
                groups.set(step.group_identifier, {
                    steps: [],
                    sourcePipelineSlug: step.source_pipeline_slug ?? step.group_identifier,
                    subPipeline: step.source_pipeline ?? null,
                });
            }
            groups.get(step.group_identifier)!.steps.push(step);
        } else {
            standaloneSteps.push(step);
        }
    }

    // Map each step identifier to its effective node id (group or self)
    const stepToNodeId = new Map<string, string>();
    for (const step of standaloneSteps) stepToNodeId.set(step.identifier, step.identifier);
    Array.from(groups.entries()).forEach(([groupId, {steps: gSteps}]) => {
        gSteps.forEach(step => stepToNodeId.set(step.identifier, groupId));
    });

    // Add standalone step nodes
    for (const step of standaloneSteps) {
        nodes.push(generateNode(
            step.identifier, "pipeline",
            step.service?.status ?? ServiceStatus.AVAILABLE,
            step.service_id,
            step.service?.data_in_fields ?? [],
            step.service?.data_out_fields ?? [],
        ));
    }

    // Build raw edges from all steps (using original step identifiers)
    const rawEdges: Edge[] = [];
    for (const step of entity.steps) {
        for (let j = 0; j < step.inputs.length; j++) {
            const field = step.inputs[j];
            const fieldIdentifier = field.split(".")[1];
            const sourceStepId = field.split(".")[0];

            if (sourceStepId === "pipeline") {
                rawEdges.push({
                    id: `${entryNode.id}-${fieldIdentifier}-${step.identifier}-${step.service?.data_in_fields?.[j]?.name ?? j}`,
                    source: entryNode.id,
                    sourceHandle: `${entryNode.id}-${fieldIdentifier}`,
                    target: step.identifier,
                    targetHandle: `${step.identifier}-${step.service?.data_in_fields?.[j]?.name ?? j}`,
                    animated: false,
                    type: edgeType,
                });
            } else {
                rawEdges.push({
                    id: `${sourceStepId}-${fieldIdentifier}-${step.identifier}-${step.service?.data_in_fields?.[j]?.name ?? j}`,
                    source: sourceStepId,
                    sourceHandle: `${sourceStepId}-${fieldIdentifier}`,
                    target: step.identifier,
                    targetHandle: `${step.identifier}-${step.service?.data_in_fields?.[j]?.name ?? j}`,
                    animated: false,
                    type: edgeType,
                });
            }
        }
    }

    // Determine terminal steps (not consumed by any other step) for exit connections
    const requiredSteps = new Set<string>();
    for (const step of entity.steps) {
        for (const inp of step.inputs) {
            const src = inp.split(".")[0];
            if (src !== "pipeline") requiredSteps.add(src);
        }
    }

    const allStepOutputs: { stepIdentifier: string, field: FieldDescription }[] = [];
    const terminalOutputs: { stepIdentifier: string, field: FieldDescription }[] = [];
    for (const step of entity.steps) {
        for (const outField of (step.service?.data_out_fields ?? [])) {
            allStepOutputs.push({stepIdentifier: step.identifier, field: outField});
            if (!requiredSteps.has(step.identifier)) {
                terminalOutputs.push({stepIdentifier: step.identifier, field: outField});
            }
        }
    }

    const usedOutputSources = new Set<string>();
    for (const pipelineOutput of (entity.data_out_fields ?? [])) {
        const pipelineSource = getPipelineSource(pipelineOutput);

        // Group-direct reference "<groupId>.<subOutputName>": the parent consumes a
        // sub-pipeline output directly, so wire straight to the collapsed group's handle.
        if (pipelineSource) {
            const dot = pipelineSource.indexOf(".");
            const groupId = pipelineSource.slice(0, dot);
            const subOutput = pipelineSource.slice(dot + 1);
            if (groups.has(groupId)) {
                rawEdges.push({
                    id: `${groupId}-${subOutput}-${exitNode.id}-${pipelineOutput.name}`,
                    source: groupId,
                    sourceHandle: `${groupId}-${subOutput}`,
                    target: exitNode.id,
                    targetHandle: `${exitNode.id}-${pipelineOutput.name}`,
                    animated: false,
                    type: edgeType,
                });
                continue;
            }
        }

        let sourceIndex = pipelineSource
            ? allStepOutputs.findIndex(c => `${c.stepIdentifier}.${c.field.name}` === pipelineSource)
            : -1;
        let selectedOutputs = pipelineSource && sourceIndex !== -1 ? allStepOutputs : terminalOutputs;

        if (sourceIndex === -1) {
            sourceIndex = terminalOutputs.findIndex(
                c => !usedOutputSources.has(`${c.stepIdentifier}.${c.field.name}`) && c.field.name === pipelineOutput.name
            );
            selectedOutputs = terminalOutputs;
        }
        if (sourceIndex === -1) {
            sourceIndex = terminalOutputs.findIndex(c => !usedOutputSources.has(`${c.stepIdentifier}.${c.field.name}`));
        }
        if (sourceIndex === -1) continue;

        const sel = selectedOutputs[sourceIndex];
        usedOutputSources.add(`${sel.stepIdentifier}.${sel.field.name}`);
        rawEdges.push({
            id: `${sel.stepIdentifier}-${sel.field.name}-${exitNode.id}-${pipelineOutput.name}`,
            source: sel.stepIdentifier,
            sourceHandle: `${sel.stepIdentifier}-${sel.field.name}`,
            target: exitNode.id,
            targetHandle: `${exitNode.id}-${pipelineOutput.name}`,
            animated: false,
            type: edgeType,
        });
    }

    // Collapse raw edges: remap endpoints using stepToNodeId, drop internal edges
    if (groups.size === 0) {
        // No groups — emit edges as-is
        edges = rawEdges.flat();
    } else {
        // A handle id is "<nodeId>-<fieldName>"; recover the field name for labels/keys.
        const handleField = (nodeId: string, handle: string | null | undefined): string =>
            handle && handle.startsWith(nodeId + "-") ? handle.slice(nodeId.length + 1) : (handle ?? nodeId);

        // Boundary handles a group exposes once collapsed (handleId -> label).
        const groupTargetHandles = new Map<string, Map<string, string>>();
        const groupSourceHandles = new Map<string, Map<string, string>>();
        Array.from(groups.keys()).forEach(groupId => {
            groupTargetHandles.set(groupId, new Map<string, string>());
            groupSourceHandles.set(groupId, new Map<string, string>());
        });

        const seenEdgeIds = new Set<string>();
        const collapsedEdges: Edge[] = [];
        for (const e of rawEdges) {
            const sourceNodeId = stepToNodeId.get(e.source) ?? e.source;
            const targetNodeId = e.target === exitNode.id
                ? exitNode.id
                : (stepToNodeId.get(e.target) ?? e.target);

            // Drop internal edges (both endpoints in same group)
            if (sourceNodeId !== entryNode.id && sourceNodeId === targetNodeId) continue;

            let newSourceHandle = e.sourceHandle ?? e.source;
            let newTargetHandle = e.targetHandle ?? e.target;

            // Source is the collapsed group.
            if (groups.has(sourceNodeId)) {
                if (sourceNodeId !== e.source) {
                    // An internal step crosses out: map its output back to the matching
                    // sub-pipeline output field so the edge lands on the named handle.
                    const subStep = e.source.slice(sourceNodeId.length + 1);
                    const field = handleField(e.source, e.sourceHandle);
                    const subPipeline = groups.get(sourceNodeId)!.subPipeline;
                    const subOutput = (subPipeline?.data_out_fields ?? []).find(
                        (f: FieldDescription) => getPipelineSource(f) === `${subStep}.${field}`
                    );
                    if (subOutput) {
                        newSourceHandle = `${sourceNodeId}-${subOutput.name}`;
                    } else {
                        newSourceHandle = `${sourceNodeId}-out-${e.sourceHandle ?? e.source}`;
                        groupSourceHandles.get(sourceNodeId)!.set(newSourceHandle, field);
                    }
                } else {
                    // Group-direct edge: handle is already named after a sub-pipeline output.
                    groupSourceHandles.get(sourceNodeId)!.set(newSourceHandle, handleField(sourceNodeId, e.sourceHandle));
                }
            }
            // Target crosses into a group: coalesce by external source so steps that
            // share the same pipeline input collapse onto a single entry handle.
            if (groups.has(targetNodeId) && targetNodeId !== e.target) {
                const field = handleField(sourceNodeId, e.sourceHandle);
                newTargetHandle = `${targetNodeId}-in-${sourceNodeId}-${field}`;
                groupTargetHandles.get(targetNodeId)!.set(newTargetHandle, field);
            }

            const id = `${sourceNodeId}-${newSourceHandle}-${targetNodeId}-${newTargetHandle}`;
            if (seenEdgeIds.has(id)) continue;
            seenEdgeIds.add(id);

            collapsedEdges.push({
                ...e,
                id,
                source: sourceNodeId,
                sourceHandle: newSourceHandle,
                target: targetNodeId,
                targetHandle: newTargetHandle,
            });
        }

        // Generate collapsed group nodes with the collected boundary handles
        Array.from(groups.entries()).forEach(([groupId, {sourcePipelineSlug, subPipeline, steps: gSteps}]) => {
            const targetHandles = Array.from(groupTargetHandles.get(groupId)!.entries()).map(([id, label]) => ({id, label}));
            // Expose every sub-pipeline output (even unused ones), then add any handle an
            // edge resolved to that isn't in the declared interface (e.g. unhinted outputs).
            const sourceHandleMap = new Map<string, string>();
            for (const field of (subPipeline?.data_out_fields ?? [])) {
                sourceHandleMap.set(`${groupId}-${field.name}`, field.name);
            }
            Array.from(groupSourceHandles.get(groupId)!.entries()).forEach(([id, label]) => {
                if (!sourceHandleMap.has(id)) sourceHandleMap.set(id, label);
            });
            const sourceHandles = Array.from(sourceHandleMap.entries()).map(([id, label]) => ({id, label}));
            const serviceId = gSteps[0]?.service_id ?? groupId;
            nodes.push(generateGroupNode(groupId, sourcePipelineSlug, serviceId, targetHandles, sourceHandles));
        });

        edges = collapsedEdges.flat();
    }

    nodes.push(exitNode);
    return {nodes, edges};
}

const generateNode = (slug: string, type: string, status: ServiceStatus, service_id: string, data_in_fields: FieldDescription[], data_out_fields: FieldDescription[]) => {
    const targetHandles = data_in_fields.map((field) => ({id: slug + "-" + field.name, label: field.name}));
    const sourceHandles = data_out_fields.map((field) => ({id: slug + "-" + field.name, label: field.name}));
    return {
        id: slug,
        type: "progressNode",
        data: {
            label: slug,
            type,
            service_id,
            service_slug: slug,
            status,
            sourceHandles,
            targetHandles,
        },
        width: nodeWidth,
        height: nodeHeight,
    };
};

const generateGroupNode = (
    id: string,
    label: string,
    serviceId: string,
    targetHandles: { id: string, label: string }[],
    sourceHandles: { id: string, label: string }[]
) => {
    return {
        id,
        type: "progressNode",
        data: {
            // "subpipeline" makes StepNode link to the pipeline page and aggregate
            // status from the (representative) internal service rather than the group id.
            label,
            type: "subpipeline",
            service_id: serviceId,
            service_slug: label,
            status: ServiceStatus.AVAILABLE,
            sourceHandles,
            targetHandles,
        },
        width: nodeWidth,
        height: nodeHeight,
    };
};

const generateEntryNode = (
    executionType: string,
    slug: string,
    data_in_fields: FieldDescription[],
    status: ServiceStatus
) => {
    const id = slug + "-entry";
    const sourceHandles = data_in_fields.map((field) => ({id: id + "-" + field.name, label: field.name}));
    return {
        id,
        type: "entryNode",
        data: {
            label: slug + "-entry",
            executionType,
            data_in_fields,
            status,
            sourceHandles,
            targetHandles: [],
        },
        position: {x: 0, y: 0},
        width: nodeWidth,
        height: nodeHeight,
    };
};

const generateExitNode = (slug: string, data_out_fields: FieldDescription[]) => {
    const id = slug + "-exit";
    const targetHandles = data_out_fields.map((field) => ({id: id + "-" + field.name, label: field.name}));
    return {
        id,
        type: "exitNode",
        data: {
            label: slug + "-exit",
            data_out_fields,
            sourceHandles: [],
            targetHandles,
        },
        width: nodeWidth,
        height: nodeHeight,
    };
};
