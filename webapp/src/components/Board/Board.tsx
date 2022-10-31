import React, { useEffect, useCallback, useMemo } from 'react';
import ReactFlow, {
    addEdge,
    ReactFlowProvider,
    Background,
    Controls,
    useNodesState,
    useEdgesState,
    MiniMap
} from 'react-flow-renderer';

import DrawGraph from './DrawGraph';
import SelectorNode from './CustomNode';
import { ControlButton } from 'reactflow';
import { FullscreenExit } from '@mui/icons-material';

const Board: React.FC<{service: any}> = ({service}) => {
    const nodeTypes = useMemo(() => ({ selectorNode: SelectorNode }), []);
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);

    const onConnect = useCallback(
        (params: any) => setEdges((eds: any) => addEdge({...params, animated: true}, eds)),
        []
    );

    function CustomControls() {
        return (
            <Controls>
                <ControlButton onClick={() => document.exitFullscreen()}>
                    <FullscreenExit />
                </ControlButton>
            </Controls>
        );
    }

    useEffect(() => {
        const {nodes: layoutedNodes, edges: layoutedEdges} = DrawGraph(service);
        setNodes([...layoutedNodes]);
        setEdges([...layoutedEdges]);
    }, [service])

    return (
        <ReactFlowProvider>
            <ReactFlow
                id="board"
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                nodeTypes={nodeTypes}
                fitView
            >
                <CustomControls/>
                <Background />
                <MiniMap/>
            </ReactFlow>
        </ReactFlowProvider>
    );
};

export default Board;
