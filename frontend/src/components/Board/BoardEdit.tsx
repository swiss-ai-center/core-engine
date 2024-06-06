import React from 'react';
import ReactFlow, {
    Background, Controls,
} from 'reactflow';
import { useSelector } from 'react-redux';
import "./styles.css";
import 'reactflow/dist/style.css';
import EntryNodeEdit from '../Nodes/EntryNodeEdit';
import StepNodeEdit from '../Nodes/StepNodeEdit';
import ExitNodeEdit from '../Nodes/ExitNodeEdit'
import EditEdge from '../Edges/EdgeEdit';

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
    const colorMode = useSelector((state: any) => state.colorMode.value);


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
            <Background />
            <Controls/>
        </ReactFlow>
    );
};

export default BoardEdit;
