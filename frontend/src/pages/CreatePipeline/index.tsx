import ItemGrid from "../../components/ItemGrid/ItemGrid";
import {AutocompleteValue, Box, Container, SelectChangeEvent} from "@mui/material";
import {Tag} from "../../models/Tag";
import {useSearchParams} from "react-router-dom";
import ReactFlow, {
    addEdge,
    Background,
    Connection,
    Controls,
    Edge,
    Node,
    ReactFlowProvider,
    useEdgesState,
    useNodesState
} from "react-flow-renderer";
import {ArrowUpward} from "@mui/icons-material";
import ScrollToTop from "react-scroll-to-top";
import {useSelector} from "react-redux";
import ExitNode from "../../components/Board/ExitNode";
import EntryNodeEdit from "../../components/Nodes/EntryNodeEdit";
import {FieldDescription} from "../../models/ExecutionUnit";
import ServiceNode from "../../components/Nodes/ServiceNode";
import {handleAIToggle, handleNoFilter, handleSearch, handleTags} from "../../utils/functions";
import {PipelineStep} from "../../models/Pipeline";
import React from "react";
import test from "node:test";

let id = 0;
const getId = () => `${id++}`;

const nodeTypes = {
    entryNodeEdit: EntryNodeEdit, serviceNode: ServiceNode, exitNode: ExitNode
};
const CreatePipeline: React.FC<{ mobileOpen: boolean }> = (
    {
        mobileOpen,
    }) => {

    const orderByList = [
        {value: 'name-asc', label: 'Name (A-Z)'},
        {value: 'name-desc', label: 'Name (Z-A)'},
    ];

    const colorMode = useSelector((state: any) => state.colorMode.value);
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [pipeName, setPipeName] = React.useState('')
    const [pipeSlug, setPipeSlug] = React.useState('')
    const [pipeSummary, setPipeSummary] = React.useState('')
    const [pipeDescription, setPipeDescription] = React.useState('')
    const [search, setSearch] = React.useState('');
    const [orderBy, setOrderBy] = React.useState(orderByList[0].value);
    const [tags, setTags] = React.useState<Tag[]>([]);
    const [ai, setAI] = React.useState(false);
    const [pipeDataInFields, setPipeDataInFields] = React.useState<FieldDescription[]>([]);
    const [pipeDataOutFields, setPipeDataOutFields] = React.useState<FieldDescription[]>([]);
    const [pipeSteps, setPipeSteps] = React.useState<PipelineStep[]>([]);
    const [searchParams] = useSearchParams();
    const history = window.history;

    // TODO - explain why this is necessary. This is passed down to the children Nodes
    const nodesRef = React.useRef(nodes)
    const setNodesRef = React.useRef(setNodes)
    const edgesRef = React.useRef(edges)


    const handleNoFilterWrapper = () => handleNoFilter(searchParams, history)
    const handleTagsWrapper = (event: SelectChangeEvent, newValue: Tag[]) => {
        handleTags(event, newValue, setTags, searchParams, history, handleNoFilterWrapper);
    };

    const handleAIToggleWrapper = (event: React.ChangeEvent<HTMLInputElement>) => {
        handleAIToggle(event, setAI, searchParams, history, handleNoFilterWrapper)
    }

    const onDeleteNode = (deletedNodes: Node[]) => {
        deletedNodes.forEach((node) => {
            const edge = edgesRef.current.find((edge) => edge.source === node.id)
            if (edge) setSubsequentDataInOptions(edge, true);
        })
    }
    const onSelectServiceInput = (nodeId: string, inputIndex: number, value: string) => {
        const node = nodesRef.current.find((node) => node.id === nodeId)
        if (node === undefined) return;
        const selectedInput = [...node.data.selectedDataIn];
        selectedInput[inputIndex] = value;
        setNodesRef.current((nds) =>
            nds.map((node) => {
                if (node.id !== nodeId) {
                    return node;
                }

                return {
                    ...node,
                    data: {
                        ...node.data,
                        selectedDataIn: selectedInput,
                    },
                };
            })
        );
    };

    const onSelectEntryInput = (inputIndex: number, type: string[]) => {
        const node = nodesRef.current.find((node) => node.type === "entryNodeEdit")
        if (node === undefined) return;
        const dataIn = [...node.data.dataIn];
        dataIn[inputIndex].type = type;

        setNodesRef.current((nds) =>
            nds.map((node) => {
                if (node.type !== "entryNodeEdit") {
                    return node;
                }

                return {
                    ...node,
                    data: {
                        ...node.data,
                        dataIn: dataIn,
                    },
                };
            })
        );
    }

    const onSelectEntryInputName = (inputIndex: number, newName: string, previousName: string) => {
        const entryNode = nodesRef.current.find((node) => node.type === "entryNodeEdit")
        if (entryNode === undefined) return;
        const dataIn = [...entryNode.data.dataIn];
        dataIn[inputIndex].name = newName;
        setNodesRef.current((nds) =>
            nds.map((node) => {
                if (node.type !== "entryNodeEdit") {
                    return node;
                }

                return {
                    ...node,
                    data: {
                        ...node.data,
                        dataIn: dataIn,
                    },
                };
            })
        );


        const initialEdge = edgesRef.current.find((edge)=> edge.source === "entry" )
        if (initialEdge) {
            setSubsequentDataInOptions(initialEdge, false)

            // Propagate the name change of the selected input data in the other nodes
            const affectedNodes = findFollowingNodes(initialEdge.source)
            affectedNodes.forEach((nodeId: string) => {
                const affectedNode = nodesRef.current.find((node) => node.id === nodeId)
                if (affectedNode) updateSelectedInputOption(affectedNode, `${entryNode.data.identifier}.${newName}`,  `${entryNode.data.identifier}.${previousName}`);
            })
        }
    }

    const updateSelectedInputOption = (affectedNode: Node, newName:  string, previousName: string) => {
        const selectedDataIn = affectedNode.data.selectedDataIn.map((option: string) => {
            if (option === previousName) return newName;
            return option;
        })
        setNodesRef.current((nds) =>
            nds.map((node) => {
                if (node.id !== affectedNode.id) {
                    return node;
                }

                return {
                    ...node,
                    data: {
                        ...node.data,
                        selectedDataIn: selectedDataIn,
                    },
                };
            })
        );
    }

    const onConnect = (params: Edge<any> | Connection) =>  {
        setEdges((eds) => addEdge(params, eds));
        setSubsequentDataInOptions(params, false);
    }

    const setSubsequentDataInOptions = (edge: Edge<any> | Connection , deleted: boolean ) => {
        const sourceNode = nodesRef.current.find((node) => node.id === edge.source)
        if (!(sourceNode && edge.source && edge.target)) return;
        let possibleInput: string[] = [];


        if (!deleted) {
            possibleInput = getNodeDataInOptions(edge.source);
            const sourceNodeDataOut = sourceNode.id === "entry" ? sourceNode.data.dataIn : sourceNode.data.dataOut;
            sourceNodeDataOut.forEach((output: FieldDescription) => {
                possibleInput.push(`${sourceNode.data.identifier}.${output.name}`);
            })

        }

        // Find all the subsequent nodes (the ones after the link/connection that has been established)
        const affectedNodes = findFollowingNodes(edge.target)
        affectedNodes.unshift(edge.target)

        // Set the possible input options for all subsequent nodes
        affectedNodes.forEach((nodeId: string) => {
            // set the input options using a deep copy of the options to avoid unwillingly modifying the previous
            // nodes' options
            setNodeDataInOptions(nodeId, JSON.parse(JSON.stringify(possibleInput)))
            const affectedNode = nodes.find((node) => node.id === nodeId)
            affectedNode?.data.dataOut.forEach((output: FieldDescription) => {
                possibleInput.push(`${affectedNode.data.identifier}.${output.name}`);
            })
        })
    }

    const setNodeDataInOptions = (nodeId: string, possibleInput: string[]) => {
        setNodesRef.current((nds) =>
            nds.map((node) => {
                if (node.id !== nodeId) {
                    return node;
                }

                return {
                    ...node,
                    data: {
                        ...node.data,
                        dataInOptions: possibleInput,
                    },
                };
            })
        );
    }

    const getNodeDataInOptions = (node: string) => {
        const prevNodes = findPrecedingNodes(node)
        const possibleInput: string[] = []

        // Add all the output fields from the previous nodes to the options list
        prevNodes.forEach((nodeId) => {
            const node = nodes.find((nd) => nd.id === nodeId)
            const nodeDataOut: FieldDescription[] = node?.id === "entry" ? node?.data.dataIn : node?.data.dataOut;
            nodeDataOut.forEach((output: FieldDescription) => {
                possibleInput.push(`${node?.data.identifier}.${output.name}`);
            })
        })
        return possibleInput;
    }

    const onAddPipelineInput = () => {
        const entryNode = nodesRef.current.find((node) => node.type === "entryNodeEdit")
        if (!entryNode) return;
        const dataIn = [...entryNode.data.dataIn];
        dataIn.push(new FieldDescription())
        setNodesRef.current((nds) =>
            nds.map((node) => {
                if (node.type !== "entryNodeEdit") {
                    return node;
                }

                return {
                    ...node,
                    data: {
                        ...node.data,
                        dataIn: dataIn,
                    },
                };
            })
        );
    }


    const createEntryNode = () => {
        const dataIn: FieldDescription[] = [];
        return {
            id: "entry",
            type: "entryNodeEdit",
            data: {
                onAddPipelineInput: onAddPipelineInput,
                onSelectEntryInput: onSelectEntryInput,
                onSelectEntryInputName: onSelectEntryInputName,
                identifier: "entry",
                dataIn: dataIn,
                label: "entry",
            },
            position: {x: 0, y: 0},
        }
    }

    const addServiceNode = (serviceName: string, serviceSlug: string, dataIn: FieldDescription[], dataOut: FieldDescription[]) => {
        const id = getId();
        const selectedDataIn = new Array<string>(dataIn.length);
        const dataInOptions = new Array<string>();
        const newNode = {
            id,
            type: "serviceNode",
            position: {
                x: 150,
                y: 150,
            },
            data: {
                identifier: serviceSlug,
                onSelectInput: onSelectServiceInput,
                dataInOptions: dataInOptions,
                selectedDataIn: selectedDataIn,
                dataIn: dataIn,
                dataOut: dataOut,
                label: `${serviceName} ${id}`
            },
        };
        setNodes((nodes) => nodes.concat(newNode));
    };

    const findFollowingNodes = (nodeId: string) => {
        const followingNodes: string[] = [];
        let next: string | null = getNextNode(nodeId)
        while (next !== null) {
            followingNodes.push(next)
            next = getNextNode(next)
        }
        return followingNodes;
    }

    const getNextNode = (nodeId: string) => {
        let next = null;
        edgesRef.current.forEach((edge) => {
            if (edge.source === nodeId) {
                next = edge.target;
                return undefined;
            }
        })
        return next;
    }


    const findPrecedingNodes = (nodeId: string) => {
        const prevNodes: string[] = [];
        let prev: string | null = getPreviousNode(nodeId)
        while (prev !== null) {
            prevNodes.push(prev)
            prev = getPreviousNode(prev)
        }
        return prevNodes;
    }

    const getPreviousNode = (nodeId: string) => {
        let prev = null;
        edgesRef.current.forEach((edge) => {
            if (edge.target === nodeId) {
                prev = edge.source;
                return undefined;
            }
        })
        return prev;
    }


    React.useEffect(() => {
        const initialNodes: Node<any>[] = []
        initialNodes.push(createEntryNode())
        setNodes((nodes) => initialNodes);
    }, []);

    React.useEffect(() =>  {
        nodesRef.current = nodes;
        setNodesRef.current = setNodes
        edgesRef.current = edges
    }, [nodes, setNodes, edges])


    return (
        <Box sx={{display: 'flex'}}>
            <ScrollToTop smooth component={<ArrowUpward style={{color: (colorMode === 'light' ? 'white' : 'black')}}
                                                        sx={{paddingTop: '2px'}}/>}/>
            <Box component={"main"} sx={{flexGrow: 1, py: 10, px: 10}}>
                <Container maxWidth={false}>
                    <Box sx={{
                        height: 500,
                        width: "100%",
                        border: 2,
                        borderRadius: "5px",
                        borderColor: "primary.main"
                    }}
                    >
                        <ReactFlowProvider>
                            <ReactFlow
                                nodes={nodes}
                                edges={edges}
                                onNodesChange={onNodesChange}
                                onEdgesChange={onEdgesChange}
                                onNodesDelete={onDeleteNode}
                                nodeTypes={nodeTypes}
                                onConnect={onConnect}
                            >
                                <Controls/>
                                <Background gap={12} size={1}/>
                            </ReactFlow>
                        </ReactFlowProvider>
                    </Box>
                </Container>
                <Container maxWidth={false}>
                    <ItemGrid filter={search} orderBy={orderBy} tags={tags} handleTags={handleTagsWrapper}
                              ai={ai} handleAIToggle={handleAIToggleWrapper} addService={addServiceNode}/>
                </Container>
            </Box>
        </Box>
    );
}

export default CreatePipeline;