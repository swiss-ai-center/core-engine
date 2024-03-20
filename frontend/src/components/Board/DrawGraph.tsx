import { FieldDescription } from '../../models/ExecutionUnit';
import { Service } from '../../models/Service';
import { Pipeline } from '../../models/Pipeline';
import { Edge } from 'reactflow';
import { ElkNode } from 'elkjs';

const nodeWidth = 250;
const nodeHeight = 200;
const edgeType = 'smoothstep';

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
                id: "e" + i,
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
                id: "e" + (i + entity.data_in_fields.length),
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

        // Connect the entry node to the first step
        edges.push({
            id: "e0",
            source: entryNode.id,
            sourceHandle: `${entryNode.id}-${entity.data_in_fields[0].name}`,
            target: entity.steps[0].identifier,
            targetHandle: `${entity.steps[0].identifier}-${entity.steps[0].service.data_in_fields[0].name}`,
            animated: false,
            type: edgeType,
        });

        // Connect the steps to each other
        for (let i = 0; i < entity.steps.length - 1; i++) {
            edges.push({
                id: "e" + (i + 1),
                source: entity.steps[i].identifier,
                sourceHandle: `${entity.steps[i].identifier}-${entity.steps[i].service.data_out_fields[0].name}`,
                target: entity.steps[i + 1].identifier,
                targetHandle: `${entity.steps[i + 1].identifier}-${entity.steps[i + 1].service.data_in_fields[0].name}`,
                animated: false,
                type: edgeType,
            });
        }

        // Connect the last step to the exit node
        edges.push({
            id: "e" + entity.steps.length,
            source: entity.steps[entity.steps.length - 1].identifier,
            sourceHandle: `${entity.steps[entity.steps.length - 1].identifier}-${entity.steps[entity.steps.length - 1].service.data_out_fields[0].name}`,
            target: exitNode.id,
            targetHandle: `${exitNode.id}-${entity.data_out_fields[0].name}`,
            animated: false,
            type: edgeType,
        });

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
