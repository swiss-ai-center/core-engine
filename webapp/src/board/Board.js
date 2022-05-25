import React, { useEffect } from 'react';
import ReactFlow, { Background, Controls, useNodesState, useEdgesState } from 'react-flow-renderer';

import DrawGraph from './DrawGraph'


function Board({ service }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    const newGraph = DrawGraph(service);
    setNodes(newGraph[0]);
    setEdges(newGraph[1]);
  }, [service])

  return (
    <div className='column' style={{ height: "70vh" }}>
      <div className="content">
        <h4>{Object.keys(service).length > 0 ? service.nodes[0].api.route : "No pipeline selected"}</h4>
        <p>{Object.keys(service).length > 0 ? service.nodes[0].api.summary : ""}</p>
      </div>
      <ReactFlow
        id="board"
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Controls />
        <Background />
      </ReactFlow>
    </div>
  );
}

export default Board;