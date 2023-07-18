import React from 'react';
import ReactFlow, {
    addEdge, ReactFlowProvider, Background, Controls, useNodesState, useEdgesState, MiniMap
} from 'react-flow-renderer';
import SelectorNode from './CustomNode';
import { ControlButton } from 'reactflow';
import { FullscreenExit } from '@mui/icons-material';
import { useSelector } from 'react-redux';
import { grey } from '@mui/material/colors';
import DrawGraph from './DrawGraph';
import { Service } from '../../models/Service';
import "./styles.css";
import { Pipeline } from '../../models/Pipeline';
import { useFileArray } from '../../utils/hooks/fileArray';
import { useWebSocketConnection } from '../../utils/useWebSocketConnection';

const Board: React.FC<{ description: any }> = ({description}) => {
    const {fileArray} = useFileArray();
    const nodeTypes = React.useMemo(() => ({customNode: SelectorNode}), []);
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const lightgrey = grey[300];
    const darkgrey = grey[900];

    const onConnect = React.useCallback(
        (params: any) => setEdges((eds: any) => addEdge({...params, animated: true}, eds)),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        []
    );

    const [taskUpdates, setTaskUpdates] = React.useState<any[]>([]);

    const {lastJsonMessage, sendJsonMessage} = useWebSocketConnection();

    function CustomControls() {
        return (
            <Controls>
                <ControlButton onClick={() => document.exitFullscreen()}>
                    <FullscreenExit/>
                </ControlButton>
            </Controls>
        );
    }

    React.useEffect(() => {
        if (description) {
            let entity
            if (description.url) {
                entity = Object.assign(new Service(), description);
            } else {
                entity = Object.assign(new Pipeline(), description);
            }
            const {
                nodes: layoutedNodes,
                edges: layoutedEdges
            } = DrawGraph(entity);
            setNodes([...layoutedNodes]);
            setEdges([...layoutedEdges]);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [description])


    React.useEffect(() => {
        if (lastJsonMessage !== null) {
            // Handle incoming messages from the WebSocket as text data
            const messageData = lastJsonMessage;
            console.log('Message received:', messageData);
            // add the message to the task updates
            setTaskUpdates((prev: any) => [...prev, messageData]);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [lastJsonMessage, setTaskUpdates]);

    React.useEffect(() => {
        console.log(fileArray);
    }, [fileArray]);

    return (
        <ReactFlowProvider>
            <ReactFlow
                id={"board"}
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                nodeTypes={nodeTypes}
                fitView
                nodesDraggable={false}
                about={colorMode}
            >
                <CustomControls/>
                <Background/>
                <MiniMap
                    style={{
                        backgroundColor: colorMode === 'dark' ? darkgrey : lightgrey,
                        padding: 0, margin: 0
                    }}
                    nodeStrokeColor={() => {
                        return 'primary';
                    }}
                />
            </ReactFlow>
        </ReactFlowProvider>
    );
};

export default Board;
