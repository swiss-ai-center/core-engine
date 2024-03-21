import { FieldDescription } from '../../models/ExecutionUnit';
import { Service } from '../../models/Service';
import { Pipeline } from '../../models/Pipeline';
import { Edge } from 'reactflow';
import { ElkNode } from 'elkjs';

const nodeWidth = 250;
const nodeHeight = 200;
const edgeType = 'default';

export default function getNodesAndEdges(entity: Service | Pipeline | null) {
    let nodes: ElkNode[] = [];
    let edges: Edge[] = [];

    if (entity && entity instanceof Service) {
        const entryNode = generateEntryNode("service", entity.slug, entity.data_in_fields);
        const serviceNode = generateNode(entity.slug, "service", entity.id, entity.data_in_fields, entity.data_out_fields);
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

        edges = edges.flat()
        return {nodes: nodes, edges: edges};

    } else if (entity) {
        const entryNode = generateEntryNode("pipeline", entity.slug, entity.data_in_fields);
        nodes.push(entryNode);

        for (let i = 0; i < entity.steps.length; i++) {
            const step = entity.steps[i];
            const node = generateNode(step.identifier, "pipeline", step.service_id, step.service.data_in_fields, step.service.data_out_fields);
            nodes.push(node);
        }

        const exitNode = generateExitNode(entity.slug, entity.data_out_fields);
        nodes.push(exitNode);

        // Connect entry node to each other node
        // The rule is that a node defines his input with "<step.identifier>.<field.name>"
        // and if it requires entities from the pipeline, it uses "pipeline.<field.name>"
        for (let i = 0; i < entity.steps.length; i++) {
            const step = entity.steps[i];
            // for each input field of the step, connect the entry node to the step
            // the input array is an array of strings in the form "<node_identifier>.<field_identifier>"
            // in the same order as the fields in service.data_in_fields
            // so map the input array to the corresponding field in service.data_in_fields
            // and if the node_identifier is "pipeline", connect the entry node to the step
            for (let j = 0; j < step.inputs.length; j++) {
                const field = step.inputs[j];
                const fieldIdentifier = field.split(".")[1];
                if (field.split(".")[0] === "pipeline") {
                    // id should be unique depending on the edge source and target
                    edges.push({
                        id: `${entryNode.id}-${fieldIdentifier}-${step.identifier}-${step.service.data_in_fields[j].name}`,
                        source: entryNode.id,
                        sourceHandle: `${entryNode.id}-${fieldIdentifier}`,
                        target: step.identifier,
                        targetHandle: `${step.identifier}-${step.service.data_in_fields[j].name}`,
                        animated: false,
                        type: edgeType,
                    });
                } else {
                    const referredNode = nodes.find((node) => node.id === field.split(".")[0]);
                    if (referredNode) {
                        edges.push({
                            id: `${referredNode.id}-${fieldIdentifier}-${step.identifier}-${step.service.data_in_fields[j].name}`,
                            source: referredNode.id,
                            sourceHandle: `${referredNode.id}-${fieldIdentifier}`,
                            target: step.identifier,
                            targetHandle: `${step.identifier}-${step.service.data_in_fields[j].name}`,
                            animated: false,
                            type: edgeType,
                        });
                    }

                }
            }
        }
        // connect the required steps to the exit node
        // to do this, find the steps that are not required by any other step and connect them to the exit node
        const requiredSteps = new Set<string>();
        for (let i = 0; i < entity.steps.length; i++) {
            const step = entity.steps[i];
            for (let j = 0; j < step.inputs.length; j++) {
                if (step.inputs[j].split(".")[0] !== "pipeline") {
                    requiredSteps.add(step.inputs[j].split(".")[0]);
                }
            }
        }
        for (let i = 0; i < entity.steps.length; i++) {
            const step = entity.steps[i];
            if (!requiredSteps.has(step.identifier)) {
                for (let j = 0; j < step.service.data_out_fields.length; j++) {
                    edges.push({
                        id: `${step.identifier}-${step.service.data_out_fields[j].name}-${exitNode.id}-${step.service.data_out_fields[j].name}`,
                        source: step.identifier,
                        sourceHandle: `${step.identifier}-${step.service.data_out_fields[j].name}`,
                        target: exitNode.id,
                        targetHandle: `${exitNode.id}-${step.service.data_out_fields[j].name}`,
                        animated: false,
                        type: edgeType,
                    });
                }
            }
        }

        edges = edges.flat()
        return {nodes: nodes, edges: edges};
    }

    return {nodes: [], edges: []};
}

const generateNode = (slug: string, type: string, service_id: string, data_in_fields: FieldDescription[], data_out_fields: FieldDescription[]) => {
    const targetHandles = data_in_fields.map((field) => {
        return {id: slug + "-" + field.name, label: field.name};
    });
    const sourceHandles = data_out_fields.map((field) => {
        return {id: slug + "-" + field.name, label: field.name};
    });
    return {
        id: slug,
        type: "progressNode",
        data: {
            label: slug,
            type: type,
            service_id: service_id,
            service_slug: slug,
            sourceHandles: sourceHandles,
            targetHandles: targetHandles,
        },
        width: nodeWidth,
        height: nodeHeight,
    }
}

const generateEntryNode = (
    executionType: string,
    slug: string,
    data_in_fields: FieldDescription[]
) => {
    const id = slug + "-entry";
    const sourceHandles = data_in_fields.map((field) => {
        return {id: id + "-" + field.name, label: field.name};
    });
    return {
        id: id,
        type: "entryNode",
        data: {
            label: slug + "-entry",
            executionType: executionType,
            data_in_fields: data_in_fields,
            sourceHandles: sourceHandles,
            targetHandles: [],
        },
        position: {x: 0, y: 0},
        width: nodeWidth,
        height: nodeHeight,
    }
}

const generateExitNode = (slug: string, data_out_fields: FieldDescription[]) => {
    const id = slug + "-exit";
    const targetHandles = data_out_fields.map((field) => {
        return {id: id + "-" + field.name, label: field.name};
    });
    return {
        id: id,
        type: "exitNode",
        data: {
            label: slug + "-exit",
            data_out_fields: data_out_fields,
            sourceHandles: [],
            targetHandles: targetHandles,
        },
        width: nodeWidth,
        height: nodeHeight,
    }
}
