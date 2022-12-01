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

import "./styles.css";

const Board: React.FC<{description: any}> = ({description}) => {
    const nodeTypes = useMemo(() => ({ customNode: SelectorNode }), []);
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);

    const onConnect = useCallback(
        (params: any) => setEdges((eds: any) => addEdge({...params, animated: true}, eds)),
        // eslint-disable-next-line react-hooks/exhaustive-deps
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
        const {nodes: layoutedNodes, edges: layoutedEdges} = DrawGraph(description);
        setNodes([...layoutedNodes]);
        setEdges([...layoutedEdges]);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [description])

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
                <CustomControls />
                <Background />
                <MiniMap/>
            </ReactFlow>
        </ReactFlowProvider>
    );
};

export default Board;
