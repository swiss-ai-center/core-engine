import React, { useEffect } from 'react';
import ReactFlow, { Background, Controls, useNodesState, useEdgesState } from 'react-flow-renderer';

import DrawGraph from './DrawGraph'


function Board({ service }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([{
    id: 1,
    next: [],
    sourcePosition: "right",
    targetPosition: 'left',
    data: { label: "Nothing to se here currently, please select a service to see its content" },
    position: { x: 0, y: 0 }
  }]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    if (Object.keys(service).length > 0){
      const newGraph = DrawGraph(service);
      setNodes(newGraph[0]);
      setEdges(newGraph[1]);
    }
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