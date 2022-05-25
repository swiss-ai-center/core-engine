export default function DrawGraph(serviceConfiguration) {

  let nodes = [];
  let edges = [];

  if (serviceConfiguration !== null && Object.keys(serviceConfiguration).length > 0) {
    const nodesConfig = serviceConfiguration.nodes;

    let x = 0;
    let y = 0;
    for (let idx in nodesConfig) {
      const node = nodesConfig[idx];
      const newNode = {
        id: node.id,
        sourcePosition: "right",
        targetPosition: 'left',
        next: node.next,
        data: { label: node.id },
        position: { x: x, y: y }
      };

      nodes = [...nodes, newNode];

      let countEdges = 0;
      for (let nxt in node.next) {
        console.log(nxt, node.next, node.next[nxt])
        const edge = {
          id: `${node.id}-e-${countEdges}`,
          source: node.id,
          type: 'smoothstep',
          target: node.next[nxt],
          animated: true,
        };
        edges = [...edges, edge];
        countEdges += 1;
      }

      x += 200;
    }
  }

  return [nodes, edges];

}