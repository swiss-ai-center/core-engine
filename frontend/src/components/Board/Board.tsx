import React from 'react';
import ReactFlow, {
    Background,
    Controls,
    useNodesState,
    useEdgesState,
    useReactFlow,
    Edge,
} from 'reactflow';
import EntryNode from './EntryNode';
import ExitNode from './ExitNode';
import ProgressNode from './ProgressNode';
import { useDispatch, useSelector } from 'react-redux';
import { grey } from '@mui/material/colors';
import DrawGraph from './DrawGraph';
import { Service } from '../../models/Service';
import { Pipeline } from '../../models/Pipeline';
import { useWebSocketConnection } from '../../utils/useWebSocketConnection';
import { toast } from 'react-toastify';
import { Message, MessageSubject } from '../../models/Message';
import {
    RunState,
    incrementTimer,
    setCurrentTask,
    setGeneralStatus,
    setResultIdList,
    setTaskArray
} from '../../utils/reducers/runStateSlice';
import { Task } from '../../models/Task';
import { ConnectionData } from '../../models/ConnectionData';
import { Box, Typography } from '@mui/material';
import { displayTimer } from '../../utils/functions';
import { ElkNode, EntryNodeData, ExitNodeData, ProgressNodeData } from '../../models/NodeData';
import ELK from 'elkjs/lib/elk.bundled';
import "./styles.css";
import 'reactflow/dist/style.css';

const layoutOptions = {
    'elk.layered.nodePlacement.strategy': 'NETWORK_SIMPLEX',
};

const elk = new ELK();

const Board: React.FC<{ description: any }> = ({description}) => {
    const lightgrey = grey[300];
    const darkgrey = grey[500];
    const dispatch = useDispatch();
    const nodeTypes = React.useMemo(() => ({
        entryNode: EntryNode, progressNode: ProgressNode, exitNode: ExitNode
    }), []);
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const taskArray = useSelector((state: any) => state.runState.taskArray);
    const taskExecuting = useSelector((state: any) => state.runState.task);
    const timer = useSelector((state: any) => state.runState.timer);
    const [nodes, , onNodesChange] = useNodesState([]);
    const [edges, , onEdgesChange] = useEdgesState([]);
    const {setNodes, setEdges, fitView} = useReactFlow<EntryNodeData | ProgressNodeData | ExitNodeData>();
    const {lastJsonMessage} = useWebSocketConnection();

    React.useEffect(() => {
        if (taskExecuting) {
            const interval = setInterval(() => {
                dispatch(incrementTimer());
            }, 100);
            return () => clearInterval(interval);
        }
    }, [dispatch, taskArray, taskExecuting]);

    React.useEffect(() => {
        // uses elkjs to give each node a layouted position
        const getLayoutedNodes = async (nodes: ElkNode[], edges: Edge[]) => {
            const graph = {
                id: 'root',
                layoutOptions,
                children: nodes.map((n) => {
                    const targetPorts = n.data.targetHandles.map((t) => ({
                        id: t.id,

                        // ⚠️ it's important to let elk know on which side the port is
                        // in this example targets are on the left (WEST) and sources on the right (EAST)
                        properties: {
                            side: 'WEST',
                        },
                    }));

                    const sourcePorts = n.data.sourceHandles.map((s) => ({
                        id: s.id,
                        properties: {
                            side: 'EAST',
                        },
                    }));

                    return {
                        id: n.id,
                        width: n.width ?? 200,
                        height: n.height ?? 200,
                        // ⚠️ we need to tell elk that the ports are fixed, in order to reduce edge crossings
                        properties: {
                            'org.eclipse.elk.portConstraints': 'FIXED_ORDER',
                        },
                        // we are also passing the id, so we can also handle edges without a sourceHandle or targetHandle option
                        ports: [{id: n.id}, ...targetPorts, ...sourcePorts],
                    };
                }),
                edges: edges.map((e) => ({
                    id: e.id,
                    sources: [e.sourceHandle || e.source],
                    targets: [e.targetHandle || e.target],
                })),
            };
            const layoutedGraph = await elk.layout(graph);
            return nodes.map((node) => {
                const layoutedNode = layoutedGraph.children?.find(
                    (lgNode) => lgNode.id === node.id,
                );

                return {
                    ...node,
                    position: {
                        x: layoutedNode?.x ?? 0,
                        y: layoutedNode?.y ?? 0,
                    },
                };
            });
        };

        const layoutNodes = async () => {
            if (description) {
                let entity
                if (description.url) {
                    entity = Object.assign(new Service(), description);
                } else {
                    entity = Object.assign(new Pipeline(), description);
                }
                const {
                    nodes: baseNodes,
                    edges: baseEdges
                } = DrawGraph(entity);

                const layoutedNodes = await getLayoutedNodes(
                    baseNodes as ElkNode[],
                    baseEdges,
                );
                setNodes(layoutedNodes);
                setEdges(baseEdges);
            }

            setTimeout(() => fitView(), 0);
        };

        layoutNodes();
    }, [description, setNodes, setEdges, fitView]);


    React.useEffect(() => {
        const isExecuting = (task: any) => {
            return task && (task.status === RunState.PENDING ||
                task.status === RunState.PROCESSING ||
                task.status === RunState.SAVING ||
                task.status === RunState.FETCHING);
        }

        const isFinished = (task: any) => {
            return task.status === RunState.IDLE ||
                task.status === RunState.FINISHED ||
                task.status === RunState.SKIPPED ||
                task.status === RunState.ERROR;
        }

        const handleMessage = (message: Message) => {
            // extract data, type and subject from message
            const {message: messageData, type, subject} = message;
            // check if message is valid
            if (messageData) {
                // extract text and data from messageData
                const {text, data} = messageData;
                // check if text and data are valid
                if (text && data) {
                    // check if subject is execution
                    if (subject === MessageSubject.EXECUTION) {
                        // cast data to Task to be able to access properties
                        const dataObject = data as Task;
                        let str;
                        // check if general_status is set. In this case, the execution is finished
                        if (dataObject.general_status) {
                            if (dataObject.data_out) {
                                dispatch(setResultIdList(dataObject.data_out));
                            } else {
                                dispatch(setResultIdList(dataObject.data_in));
                            }
                            dispatch(setGeneralStatus(dataObject.general_status));
                            dispatch(setCurrentTask(null));
                            str = `${text}`;
                            // check if pipeline_execution_id is not set. In this case, the execution is finished but for a task
                        } else if (!dataObject.pipeline_execution_id) {
                            dispatch(setResultIdList(dataObject.data_out));
                            dispatch(setGeneralStatus(dataObject.status));
                            dispatch(setCurrentTask(null));
                            str = `${text}, status: ${dataObject.status}`;
                        } else {
                            str = `${text}, status: ${dataObject.status}`;
                        }
                        // display message in a toast
                        toast(str, {type: type});

                        // update taskArray and currentTask according to the message
                        if (taskArray) {
                            let oldTask;
                            // create the new taskArray by mapping over the old one. If the old one is already finished,
                            // do not update it. It means a message was received after the execution was finished.
                            const newTaskArray = taskArray.map((task: any) => {
                                if (task.id === dataObject.id) {
                                    oldTask = task;
                                    if (!isFinished(task)) {
                                        return dataObject;
                                    }
                                }
                                return task;
                            });
                            // update taskArray
                            dispatch(setTaskArray(newTaskArray));
                            // update currentTask if it is executing
                            if (isExecuting(dataObject) && (oldTask && !isFinished(oldTask))) {
                                dispatch(setCurrentTask(dataObject));
                            }
                        }
                        // check if subject is connection
                    } else if (subject === MessageSubject.CONNECTION) {
                        // cast data to ConnectionData to be able to access properties
                        // uncomment to show message in a toast (not enabled by default)
                        const dataObject = data as ConnectionData;
                        let str = text;
                        if (dataObject.linked_id) {
                            str += `, linked_id: ${dataObject.linked_id}`;
                        }
                        if (dataObject.execution_type) {
                            // eslint-disable-next-line @typescript-eslint/no-unused-vars
                            str += `, execution_type: ${dataObject.execution_type}`;
                        }
                        // toast(str, {type: type, theme: colorMode === 'light' ? 'dark' : 'light'});
                    }
                } else {
                    console.log("Message is not valid");
                }
            } else {
                console.log("Message is not valid");
            }
        }

        if (lastJsonMessage !== null) {
            // Handle incoming messages from the WebSocket from json to object Message
            const message: Message = Object.assign(new Message(), lastJsonMessage);
            handleMessage(message);
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [dispatch, lastJsonMessage]);

    return (
        <ReactFlow
            id={"board"}
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            elevateNodesOnSelect={false}
            elevateEdgesOnSelect={false}
            nodesConnectable={false}
            fitView
            snapToGrid
            about={colorMode}
            style={{
                backgroundColor: colorMode === 'dark' ? '#121212' : '#fff',
                borderRadius: 3,
            }}
        >
            <Box id={"timer-general"} className={"timer-general"} zIndex={99} about={colorMode}>
                <Typography
                    color={taskExecuting ? "primary" : (colorMode === 'dark' ? lightgrey : darkgrey)}>
                    {displayTimer(timer)}
                </Typography>
            </Box>
            <Background/>
            <Controls showInteractive={false}/>
        </ReactFlow>
    );
};

export default Board;
