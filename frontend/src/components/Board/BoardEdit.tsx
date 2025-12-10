import EditEdge from 'components/Edges/EdgeEdit';
import EntryNodeEdit from 'components/Nodes/EntryNodeEdit';
import ExitNodeEdit from 'components/Nodes/ExitNodeEdit'
import StepNodeEdit from 'components/Nodes/StepNodeEdit';
import React from 'react';
import { useSelector } from 'react-redux';
import 'components/Board/styles.css';
import '@xyflow/react/dist/style.css';
import { Background, Controls, ReactFlow } from '@xyflow/react';
import { systemColorModeToLightOrDark } from '../../utils/functions';

const BoardEdit: React.FC<{
  nodes: any,
  edges: any,
  onNodesChange: any,
  onEdgesChange: any,
  onEdgeDelete: any,
  isValidConnection: any,
  onConnect: any
}> = (
  {nodes, edges, onNodesChange, onEdgesChange, onEdgeDelete, isValidConnection, onConnect}) => {
  const nodeTypes = React.useMemo(() => ({
    entryNodeEdit: EntryNodeEdit, serviceNode: StepNodeEdit, exitNodeEdit: ExitNodeEdit
  }), []);

  const edgeTypes = React.useMemo(() => ({
    editEdge: EditEdge,
  }), []);
  const colorMode = systemColorModeToLightOrDark(useSelector((state: any) => state.colorMode.value));


  return (
    <ReactFlow
      id={"board"}
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onEdgesDelete={onEdgeDelete}
      isValidConnection={isValidConnection}
      nodeTypes={nodeTypes}
      edgeTypes={edgeTypes}
      onConnect={onConnect}
      fitView
      snapToGrid
      about={colorMode}
      style={{
        backgroundColor: colorMode === 'dark' ? '#121212' : '#fff',
        borderRadius: 3,
      }}
    >
      <Background/>
      <Controls/>
    </ReactFlow>
  );
};

export default BoardEdit;
