import React, { useEffect } from 'react';
import ReactFlow, { Background, Controls, useNodesState, useEdgesState } from 'react-flow-renderer';

import DrawGraph from './DrawGraph'


function Board({service, dimensions}) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    const newGraph = DrawGraph(service);
    setNodes(newGraph[0]);
    setEdges(newGraph[1]);
  }, [service])

  return (
    <div className='column' style={{ height: dimensions.height - (dimensions.height / 5) }}>
      <ReactFlow
        id="board"
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        // onConnect={onConnect}
        fitView
      >
        <Controls />
        <Background />
      </ReactFlow>
    </div>
  );
}

export default Board;