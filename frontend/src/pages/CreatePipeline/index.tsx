import ItemGrid from "../../components/ItemGrid/ItemGrid";
import {Box, Button, Container, SelectChangeEvent} from "@mui/material";
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
} from "reactflow";
import {ArrowUpward} from "@mui/icons-material";
import ScrollToTop from "react-scroll-to-top";
import {useSelector} from "react-redux";
import EntryNodeEdit from "../../components/Nodes/EntryNodeEdit";
import {FieldDescription} from "../../models/ExecutionUnit";
import ServiceNode from "../../components/Nodes/ServiceNode";
import {handleAIToggle, handleNoFilter, handleOrder, handleSearch, handleTags} from "../../utils/functions";
import {PipelineStep} from "../../models/Pipeline";
import React from "react";
import ExitNodeEdit from "../../components/Nodes/ExitNodeEdit";
import {toast} from "react-toastify";
import {FilterDrawer} from "../../components/FilterDrawer/FilterDrawer";
import CreatePipelineServiceCard from "../../components/ServiceCard/CreatePipelineServiceCard";

let id = 0;
const getId = () => `${id++}`;
const CreatePipeline: React.FC<{ mobileOpen: boolean, handleOpen: any }> = (
    {mobileOpen, handleOpen}) => {

    const nodeTypes = React.useMemo(() => ({
        entryNodeEdit: EntryNodeEdit, serviceNode: ServiceNode, exitNodeEdit: ExitNodeEdit
    }), []);

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

    const onNodeDelete = (deletedNodes: Node[]) => {
        deletedNodes.forEach((node) => {
            // Find a better way, to handle entry and exit node deletion. As of the current version of ReactFlow,
            // there doesn't seem to be a way to properly prevent certain nodes (and their associated edges) from being
            // deleted depending on their state or other variables. Future versions of ReactFlow might include a
            // "OnBeforeDelete" function which might be helpful.
            if (node.type === "exitNodeEdit") {
                setNodesRef.current(prevNodes => {
                    const exit: Node = createExitNode();
                    return [...prevNodes, exit];
                });
                return;
            } else if (node.type === "entryNodeEdit") {
                setNodesRef.current(prevNodes => {
                    const entry: Node = createEntryNode();
                    return [...prevNodes, entry];
                });
            }
        })
    }


    const onEdgeDelete = (deletedEdges: Edge[]) => {
        deletedEdges.forEach((edge) => {
            const targetNode = nodesRef.current.find((node) => edge.target === node.id)
            if(targetNode?.type === "exitNodeEdit") {
                const pipelineOutput: FieldDescription[] = [];
                setNodesRef.current((nds) =>
                    nds.map((node) => {
                        if (node.type !== "exitNodeEdit") {
                            return node;
                        }

                        return {
                            ...node,
                            data: {
                                ...node.data,
                                dataOut: pipelineOutput,
                            },
                        };
                    })
                );
            } else {
                const sourceNode = nodesRef.current.find((node) => edge.source === node.id)
                if (!targetNode || !sourceNode) return;
                const prevDataIn = [...targetNode.data.selectedDataIn];
                //const index  = affectedNode.data.selectedDataIn.findIndex((input: string) => input === edge.sourceHandle);
                const selectedDataIn = prevDataIn.filter((input) => {
                    return `${sourceNode.data.identifier}.${edge.sourceHandle}` !== input
                });
                setNodeSelectedDataIn(targetNode, selectedDataIn);
            }

        })
    }
    const onSelectEntryInput = (inputIndex: number, type: string[]) => {
        const entryNode = nodesRef.current.find((node) => node.type === "entryNodeEdit")
        if (entryNode === undefined) return;
        const dataIn = [...entryNode.data.dataIn];
        dataIn[inputIndex].type = type;
        setNodeDataIn(entryNode, dataIn);
    }

    const onSelectEntryInputName = (inputIndex: number, newName: string, previousName: string) => {
        const entryNode = nodesRef.current.find((node) => node.type === "entryNodeEdit")
        if (entryNode === undefined) return;
        const dataIn = [...entryNode.data.dataIn];
        dataIn[inputIndex].name = newName;
        setNodeDataIn(entryNode, dataIn);


        const initialEdge = edgesRef.current.find((edge)=> edge.source === entryNode.id)
        if (initialEdge) {
            // Propagate the name change of the selected input data in the other nodes
            const affectedNodes = edgesRef.current
                .map((edge) => edge.sourceHandle === previousName ? edge.target : null)
                .filter((target) => target !== null);


            affectedNodes.forEach((nodeId) => {
                const affectedNode = nodesRef.current.find((node) => node.id === nodeId)
                if (affectedNode && affectedNode.type !== "exitNodeEdit")
                    updateSelectedInputOption(affectedNode, `${entryNode.data.identifier}.${newName}`,  `${entryNode.data.identifier}.${previousName}`);
            })
        }
    }

    const updateSelectedInputOption = (affectedNode: Node, newName:  string, previousName: string) => {
        const selectedDataIn = affectedNode.data.selectedDataIn.map((option: string) => {
            if (option === previousName) return newName;
            return option;
        })
        setNodeSelectedDataIn(affectedNode, selectedDataIn);
    }

    const onConnect = (params: Edge<any> | Connection) =>  {
        if (params.target === params.source) return;
        const targetNode = nodesRef.current.find((node) => node.id === params.target);
        const sourceNode = nodesRef.current.find((node) => node.id === params.source);
        if(!(targetNode && sourceNode))  return;
        if (targetNode.type === "exitNodeEdit") {
            const pipelineOutput: FieldDescription[] = sourceNode.data.dataOut;
            setNodesRef.current((nds) =>
                nds.map((node) => {
                    if (node.type !== "exitNodeEdit") {
                        return node;
                    }

                    return {
                        ...node,
                        data: {
                            ...node.data,
                            dataOut: pipelineOutput,
                        },
                    };
                })
            );
        } else {
            const {sourceHandle, targetHandle} = params

            const sourceNodeDataOut = sourceNode.type === "entryNodeEdit" ? sourceNode.data.dataIn : sourceNode.data.dataOut;
            const dataInIndex  = targetNode.data.dataIn.findIndex((input: FieldDescription) => input.name === targetHandle)
            const sourceDataIndex = sourceNodeDataOut.findIndex((input: FieldDescription) => input.name === sourceHandle)
            const dataTypes: string [] = sourceNodeDataOut[sourceDataIndex]?.type;

            if (sourceHandle === null || dataTypes.length === 0) {
                toast("The data must be named and have a type to be connected", {type: "info"});
                return;
            }
            const allowedTypes : string[] = targetNode.data.dataIn[dataInIndex].type;
            let compatible  = false;
            dataTypes.forEach((type: string) => {
                if (allowedTypes.includes(type)) compatible = true;
            })

            if (!compatible) {
                toast("Incompatible types", {type: "info"});
                return;
            }
            const selectedDataIn = [...targetNode.data.selectedDataIn];
            selectedDataIn[dataInIndex] = `${sourceNode.data.identifier}.${params.sourceHandle}`;
            setNodeSelectedDataIn(targetNode, selectedDataIn);
        }
        setEdges((eds) => addEdge(params, eds));
    }

    const setNodeSelectedDataIn =  (affectedNode: Node, selectedDataIn: string[]) => {
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

    const setNodeDataIn = (affectedNode: Node, dataIn: FieldDescription[]) => {
        setNodesRef.current((nds) =>
            nds.map((node) => {
                if (node.id !== affectedNode.id) {
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

    const onAddPipelineInput = () => {
        const entryNode = nodesRef.current.find((node) => node.type === "entryNodeEdit")
        if (!entryNode) return;
        const dataIn = [...entryNode.data.dataIn];
        const inputField = new FieldDescription();
        inputField.type = []
        inputField.name = "Input Name"
        dataIn.push(inputField)
        setNodeDataIn(entryNode, dataIn);
    }


    const createEntryNode = () => {
        const dataIn: FieldDescription[] = [];
        const id = getId();
        return {
            id: `entry${id}`,
            type: "entryNodeEdit",
            data: {
                onAddPipelineInput: onAddPipelineInput,
                onSelectEntryInput: onSelectEntryInput,
                onSelectEntryInputName: onSelectEntryInputName,
                identifier: "entry",
                dataIn: dataIn,
                label: "Pipeline entry",
            },
            position: {x: 50, y: 200},
        }
    }

    const createExitNode = () => {
        const dataOut: FieldDescription[] = [];
        const id = getId();
        return {
            id: `exit${id}`,
            type: "exitNodeEdit",
            data: {
                identifier: "exit",
                dataOut: dataOut,
                label: "Exit",
            },
            position: {x: 550, y: 200},
        }
    }

    const addServiceNode = (serviceName: string, serviceSlug: string, dataIn: FieldDescription[], dataOut: FieldDescription[]) => {
        const id = getId();
        const selectedDataIn = new Array<string>(dataIn.length);
        const newNode = {
            id,
            type: "serviceNode",
            position: {
                x: 150,
                y: 150,
            },
            data: {
                identifier: serviceSlug,
                selectedDataIn: selectedDataIn,
                dataIn: dataIn,
                dataOut: dataOut,
                label: `${serviceName} ${id}`
            },
        };
        setNodesRef.current((nodes) => nodes.concat(newNode));
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

    const computeJSONRepresentation = () => {
        const entryNode = nodesRef.current.find((node) => node.id === "entryNodeEdit");
        if (!entryNode) return null;
        const data_in_fields = JSON.stringify(entryNode.data.dataIn);
        console.log(data_in_fields);
    }


    React.useEffect(() => {
        const initialNodes: Node<any>[] = []
        initialNodes.push(createEntryNode())
        initialNodes.push(createExitNode())
        setNodes(() => initialNodes);
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
            <FilterDrawer
                mobileOpen={mobileOpen} handleOpen={handleOpen}
                orderBy={orderBy} handleOrder={(event: SelectChangeEvent) => {
                handleOrder(event, setOrderBy,searchParams, history)}}
                orderByList={orderByList}
                search={search}
                handleSearch={(event: React.ChangeEvent<HTMLInputElement>) => {
                handleSearch(event, setSearch, searchParams, handleNoFilterWrapper, history)}}
                tags={tags}
                handleTags={(event: SelectChangeEvent, newValue: Tag[]) =>
                handleTags(event, newValue, setTags, searchParams, history, handleNoFilterWrapper)}
                ai={ai}
                handleAIToggle={(event: React.ChangeEvent<HTMLInputElement>) =>
                handleAIToggle(event, setAI, searchParams, history, handleNoFilterWrapper)}
            />
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
                                onNodesDelete={onNodeDelete}
                                onEdgesDelete={onEdgeDelete}
                                nodeTypes={nodeTypes}
                                onConnect={onConnect}
                            >
                                <Controls/>
                                <Background gap={12} size={1}/>
                            </ReactFlow>
                        </ReactFlowProvider>
                    </Box>
                </Container>
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', width: '100%' }}>
                    <Button onClick={computeJSONRepresentation}></Button>
                </Box>
                <Container maxWidth={false}>
                    <ItemGrid filter={search} orderBy={orderBy} tags={tags} ai={ai}
                              itemFunctions={{addService: addServiceNode}}
                              items={{service: CreatePipelineServiceCard}}
                              handleTags={(event: SelectChangeEvent, newValue: Tag[]) =>
                                  handleTags(event, newValue, setTags, searchParams, history, handleNoFilterWrapper)}

                              handleAIToggle={(event: React.ChangeEvent<HTMLInputElement>) =>
                                  handleAIToggle(event, setAI, searchParams, history, handleNoFilterWrapper)}
                    />
                </Container>
            </Box>
        </Box>
    );
}

export default CreatePipeline;