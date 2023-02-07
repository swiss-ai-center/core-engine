import { FieldDescription, Service } from '../../models/Service';
import { Pipeline } from '../../models/Pipeline';

const dagre = require("dagre");
const nodeWidth = 200;
const nodeHeight = 215;

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

export default function DrawGraph(entity: Service | Pipeline | null) {
    console.log(entity)
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

function handleLoop(node: { id: any; nodes: any[]; next: any; }) {
    const groupName = node.id;
    let startNodes = [
        {
            id: groupName,
            position: {x: 0, y: 0},
            style: {
                height: `${(node.nodes.length + 1) * 110}px`,
                width: `${nodeWidth}px`,
                backgroundColor: "rgba(255, 26, 224, 0.2)"
            },
            next: node.next,
        },
        {
            id: "loopBegin",
            type: "input",
            position: {x: 0, y: 0},
            data: {label: "loopBegin"},
            parentNode: groupName,
            extent: "parent",
            next: [node.nodes[0].id]
        }
    ]

    let loopNodes = node.nodes.map((n) => {
        const newNode: any = getNode(n);
        newNode.parentNode = groupName;
        newNode.extent = "parent";
        return newNode
    });

    // @ts-ignore
    loopNodes.push({
        id: "loopEnd",
        type: "output",
        position: {x: 0, y: 0},
        data: {label: "loopEnd"},
        next: [],
        parentNode: groupName,
        extent: "parent"
    })

    return startNodes.concat(loopNodes);
}

function getEdge(node: any) {
    let edges: any[] = [];
    let countEdges = 0;
    for (let nxt in node.next) {
        const edge = {
            id: `${node.id}-e-${countEdges}`,
            source: node.id,
            target: node.next[nxt],
            animated: false,
        };
        edges = [...edges, edge];
        countEdges += nodeWidth;
    }
    return edges;
}

function getNode(node: any) {

    let next: any[] = [];
    let label = node.id;

    switch (node.type) {
        case "branch":
            ["then", "else"].forEach((p) => {
                next = next.concat(node[p].hasOwnProperty("next") ? node[p].next : []);
            })

            if (node.hasOwnProperty("next")) {
                next = next.concat(node.next);
            }
            break;
        case "node":
            if (node.hasOwnProperty("ready")) {
                label = `${node.id} \n with ready condition`
            } else if (node.hasOwnProperty("after")) {
                label = `${node.id} \n with after condition`
            }
            next = node.next;
            break;
        default:
            next = node.next;
            break;
    }

    return {
        id: node.id,
        type: "customNode",
        next: next,
        data: {
            label: label,
            body: node.data_in_fields ? node.data_in_fields : null,
            bodyType: node.api?.bodyType ? node.api.bodyType : null,
            resultType: node.data_out_fields ? node.data_out_fields : null,
        },
        position: {x: 0, y: 0},
    };
}
