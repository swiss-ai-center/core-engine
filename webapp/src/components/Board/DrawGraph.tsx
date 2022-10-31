const dagre = require("dagre");
const nodeWidth = 200;
const nodeHeight = 35;

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

export default function DrawGraph(serviceConfiguration: { nodes?: any; } | null) {

    let nodes: any[] = [];
    let edges: any[] = [];

    if (serviceConfiguration !== null && Object.keys(serviceConfiguration).length > 0) {
        const nodesConfig = serviceConfiguration.nodes;

        for (let idx in nodesConfig) {
            const node = nodesConfig[idx];

            if (node.type !== "loop") {
                const newNode = getNode(node);
                const newEdges = getEdge(newNode);
                nodes = [...nodes, newNode];
                edges = [...edges, newEdges];
            } else {
                const newNodes = handleLoop(node);
                nodes = nodes.concat(newNodes);
                edges = edges.concat(newNodes.map((n) => getEdge(n).flat()));
            }
        }
        edges = edges.flat()
        return getAlignedElements(nodes, edges);
    }

    return {nodes, edges}

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

    console.log(nodes, edges)

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
                console.log(next);
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
        type: getTypeOfNode(node),
        next: next,
        data: {label: label},
        position: {x: 0, y: 0},
    };
}


function getTypeOfNode(node: any) {
    switch (node.type) {
        case "entry":
            return "input";
        case "end":
            return "output";
        default:
            return "";
    }
}
