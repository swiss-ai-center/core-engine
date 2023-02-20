import { FieldDescription, Service } from '../../models/Service';
import { Pipeline } from '../../models/Pipeline';

const dagre = require("dagre");
const nodeWidth = 200;
const nodeHeight = 215;

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

export default function DrawGraph(entity: Service | Pipeline | null) {
    let nodes: any[] = [];
    let edges: any[] = [];

    if (entity && entity instanceof Service) {
        const entryNode = generateEntryNode(entity.slug, entity.data_in_fields);
        const serviceNode = generateNode(entity.slug);
        const exitNode = generateExitNode(entity.slug, entity.data_out_fields);
        nodes = [entryNode, serviceNode, exitNode];
        edges = [
            {id: "e1", source: entryNode.id, target: serviceNode.id, animated: false},
            {id: "e2", source: serviceNode.id, target: exitNode.id, animated: false},
        ];
        edges = edges.flat()
        return getAlignedElements(nodes, edges);

    } else if (entity) {
        // TODO: implement pipeline graph
    }

    return {nodes, edges}

}

const generateNode = (slug: string) => {
    return {
        id: slug,
        type: "customNode",
        next: slug+"-exit",
        data: {
            label: slug,
        }
    }
}

const generateEntryNode = (slug: string, data_in_fields: FieldDescription[]) => {
    return {
        id: slug+"-entry",
        type: "customNode",
        next: slug,
        data: {
            label: slug+"-entry",
            data_in_fields: data_in_fields,
        },
        position: {x: 0, y: 0},
    }
}

const generateExitNode = (slug: string, data_out_fields: FieldDescription[]) => {
    return {
        id: slug+"-exit",
        type: "customNode",
        next: [],
        data: {
            label: slug+"-exit",
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
