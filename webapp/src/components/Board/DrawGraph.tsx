import { FieldDescription } from '../../models/ExecutionUnit';
import { Service } from '../../models/Service';
import { Pipeline } from '../../models/Pipeline';

const dagre = require("dagre");
const nodeWidth = 200;
const nodeHeight = 215;

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

export default function DrawGraph(
    entity: Service | Pipeline | null,
) {
    let nodes: any[] = [];
    let edges: any[] = [];

    if (entity && entity instanceof Service) {
        const entryNode = generateEntryNode("service", entity.slug, entity.data_in_fields);
        const serviceNode = generateNode(entity.slug);
        const exitNode = generateExitNode(entity.slug, entity.data_out_fields);
        nodes = [entryNode, serviceNode, exitNode];
        edges = [
            {id: "e0", source: entryNode.id, target: serviceNode.id, animated: false},
            {id: "e1", source: serviceNode.id, target: exitNode.id, animated: false},
        ];
        edges = edges.flat()
        return getAlignedElements(nodes, edges);

    } else if (entity) {
        const entryNode = generateEntryNode("pipeline", entity.slug, entity.data_in_fields);
        nodes.push(entryNode);

        for (let i = 0; i < entity.steps.length; i++) {
            const serviceNode = generateNode(entity.steps[i].identifier);
            nodes.push(serviceNode);
        }

        const exitNode = generateExitNode(entity.slug, entity.data_out_fields);
        nodes.push(exitNode);

        edges.push({id: "e0", source: entryNode.id, target: nodes[1].id, animated: false});
        for (let i = 1; i < entity.steps.length; i++) {
            edges.push({id: "e" + i, source: nodes[i].id, target: nodes[i + 1].id, animated: false});
        }
        edges.push({
            id: "e" + (nodes.length - 1),
            source: nodes[nodes.length - 2].id,
            target: exitNode.id,
            animated: false
        });
        edges = edges.flat()
        return getAlignedElements(nodes, edges);
    }

    return {nodes, edges}

}

const generateNode = (slug: string) => {
    return {
        id: slug,
        type: "customNode",
        next: slug + "-exit",
        data: {
            label: slug,
        }
    }
}

const generateEntryNode = (
    executionType: string,
    slug: string,
    data_in_fields: FieldDescription[]
) => {
    return {
        id: slug + "-entry",
        type: "customNode",
        next: slug,
        data: {
            label: slug + "-entry",
            executionType: executionType,
            data_in_fields: data_in_fields,
        },
        position: {x: 0, y: 0},
    }
}

const generateExitNode = (slug: string, data_out_fields: FieldDescription[]) => {
    return {
        id: slug + "-exit",
        type: "customNode",
        next: [],
        data: {
            label: slug + "-exit",
            data_out_fields: data_out_fields,
        }
    }
}

const getAlignedElements = (nodes: any[], edges: any[]) => {
    const direction = 'LR';

    dagreGraph.setGraph({rankdir: direction});

    nodes.forEach((node) => {
        dagreGraph.setNode(node.id, {width: nodeWidth, height: nodeHeight});
    });

    edges.forEach((edge) => {
        dagreGraph.setEdge(edge.source, edge.target);
    });

    dagre.layout(dagreGraph);

    nodes.filter((node) => !node.hasOwnProperty("parentNode")).forEach((node) => {
        const nodeWithPosition = dagreGraph.node(node.id);
        node.targetPosition = 'left'
        node.sourcePosition = 'right'

        node.position = {
            x: nodeWithPosition.x - nodeWidth / 2,
            y: nodeWithPosition.y - nodeHeight / 2,
        };

        return node;
    });

    let loopY = 20;
    nodes.filter((node) => node.hasOwnProperty("parentNode")).forEach((node) => {
        node.targetPosition = 'top'
        node.sourcePosition = 'bottom'

        node.position = {
            x: 25,
            y: loopY,
        };
        loopY += 2 * nodeHeight;
    })

    return {nodes, edges};
};
