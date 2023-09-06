import React from 'react';
import ReactFlow, {
    addEdge, ReactFlowProvider, Background, Controls, useNodesState, useEdgesState, MiniMap
} from 'react-flow-renderer';
import EntryNode from './EntryNode';
import ExitNode from './ExitNode';
import ProgressNode from './ProgressNode';
import { ControlButton } from 'reactflow';
import { FullscreenExit } from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { grey } from '@mui/material/colors';
import DrawGraph from './DrawGraph';
import { Service } from '../../models/Service';
import { Pipeline } from '../../models/Pipeline';
import { useWebSocketConnection } from '../../utils/useWebSocketConnection';
import "./styles.css";
import { toast } from 'react-toastify';
import { Message, MessageSubject } from '../../models/Message';
import { RunState, setResultIdList, setRunState } from '../../utils/reducers/runStateSlice';

const Board: React.FC<{ description: any, fullscreen: boolean }> = ({description, fullscreen}) => {
    const dispatch = useDispatch();
    const nodeTypes = React.useMemo(() => ({
        entryNode: EntryNode, progressNode: ProgressNode, exitNode: ExitNode
    }), []);
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

    const {lastJsonMessage} = useWebSocketConnection();

    function CustomControls() {
        return (
            <Controls>
                <ControlButton onClick={() => document.exitFullscreen()}>
                    <FullscreenExit/>
                </ControlButton>
            </Controls>
        );
    }

    const handleMessage = (message: Message) => {
        const {message: messageData, type, subject} = message;
        if (messageData) {
            const {text, data} = messageData;
            if (text && data) {
                const dataObject = data as any;
                if (subject === MessageSubject.EXECUTION) {
                    const str = `${text}, status: ${dataObject.status}`;
                    dispatch(setRunState(dataObject.status));
                    toast(str, {type: type});
                    if (dataObject.status === RunState.FINISHED) {
                        dispatch(setResultIdList(dataObject.data_out));
                    }
                } else if (subject === MessageSubject.CONNECTION) {
                    let str = text;
                    if (dataObject.linked_id) {
                        str += `, linked_id: ${dataObject.linked_id}`;
                    }
                    if (dataObject.execution_type) {
                        str += `, execution_type: ${dataObject.execution_type}`;
                    }
                    toast(str, {type: type, theme: colorMode === 'light' ? 'dark' : 'light'});
                }
            } else {
                toast("Message is not valid", {type: "warning"});
            }
        } else {
            toast("Message is empty", {type: "warning"});
        }
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
            // Handle incoming messages from the WebSocket from json to object Message
            const message: Message = Object.assign(new Message(), lastJsonMessage);
            console.log('Message received:', message);
            handleMessage(message);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [lastJsonMessage]);

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
                style={{
                    backgroundColor: colorMode === 'dark' ? '#121212' : '#fff',
                    borderRadius: fullscreen ? 0 : 5,
                }}
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
