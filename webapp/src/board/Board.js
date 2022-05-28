import React, { useEffect, useCallback } from 'react';
import ReactFlow, { addEdge, ReactFlowProvider, Background, Controls, useNodesState, useEdgesState, MiniMap } from 'react-flow-renderer';

import DrawGraph from './DrawGraph';


const Board = ({ service }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge({ ...params, animated: true }, eds)),
    []
  );


  useEffect(() => {
    const { nodes: layoutedNodes, edges: layoutedEdges } = DrawGraph(service);
    setNodes([...layoutedNodes]);
    setEdges([...layoutedEdges]);
  }, [service])

  return (
    <div className="column" style={{ height: "70vh"}}>
      <div className="content">
        <h4>{Object.keys(service).length > 0 ? service.nodes[0].api.route : "No pipeline selected"}</h4>
        <p>{Object.keys(service).length > 0 ? service.nodes[0].api.summary : ""}</p>
      </div>
      <ReactFlowProvider>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
        >
          <Controls />
          <Background />
          <MiniMap/>
        </ReactFlow>
      </ReactFlowProvider>
    </div>
  );
};

export default Board;