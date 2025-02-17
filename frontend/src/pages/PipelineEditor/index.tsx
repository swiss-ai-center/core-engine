import { ArrowBack, ArrowUpward, DescriptionTwoTone } from "@mui/icons-material";
import {
    Box,
    Button,
    Container,
    Grid,
    Link as URLLink,
    SelectChangeEvent,
    TextField,
    Toolbar,
    Typography
} from "@mui/material";
import BoardEdit from 'components/Board/BoardEdit';
import PipelineEditorServiceCard from "components/Cards/PipelineEditorServiceCard";
import Copyright from 'components/Copyright/Copyright';
import { FilterDrawer } from "components/FilterDrawer/FilterDrawer";
import ItemGrid from "components/ItemGrid/ItemGrid";
import { JsonModal } from 'components/JsonModal/JsonModal';
import { FieldDescription } from "models/ExecutionUnit";
import { Tag } from "models/Tag";
import React from "react";
import { useSelector } from "react-redux";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import ScrollToTop from "react-scroll-to-top";
import { toast } from "react-toastify";
import {
    addEdge,
    Connection,
    Edge,
    getOutgoers,
    Node,
    ReactFlowProvider,
    useEdgesState,
    useNodesState,
} from "reactflow";
import { checkPipelineValidity, createPipeline } from "utils/api";
import { handleAIToggle, handleNoFilter, handleOrder, handleSearch, handleTags, isSmartphone } from "utils/functions";
import { PerPage } from 'utils/reducers/perPageSlice';


const entryNodeMinWidth = 400;
const nodeWidth = 200;
const nodeHeight = 200;
const nodeSpacing = 100;

const PipelineEditor: React.FC<{ mobileOpen: boolean, handleOpen: any }> = (
    {mobileOpen, handleOpen}) => {
    const navigate = useNavigate();

    const orderByList = [
        {value: 'name-asc', label: 'Name (A-Z)'},
        {value: 'name-desc', label: 'Name (Z-A)'},
    ];

    const colorMode = useSelector((state: any) => state.colorMode.value);
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [pipeName, setPipeName] = React.useState('')
    const [pipeSlug, setPipeSlug] = React.useState('')
    const [pipeNameSlugLinked, setPipeNameSlugLinked] = React.useState(true);
    const [pipeSummary, setPipeSummary] = React.useState('')
    const [pipeDescription, setPipeDescription] = React.useState('')
    const [search, setSearch] = React.useState('');
    const [orderBy, setOrderBy] = React.useState(orderByList[0].value);
    const [tags, setTags] = React.useState<Tag[]>([]);
    const [ai, setAI] = React.useState(false);
    const [jsonModalOpen, setJsonModalOpen] = React.useState(false);
    const [searchParams] = useSearchParams();
    const history = window.history;

    const nodesRef = React.useRef(nodes)
    const setNodesRef = React.useRef(setNodes)
    const edgesRef = React.useRef(edges)
    const setEdgesRef = React.useRef(setEdges)

    const handleNoFilterWrapper = () => handleNoFilter(searchParams, history)

    const navigateHome = () => {
        navigate("/home");
    }

    const handlePipeSlug = (value: string) => {
        setPipeNameSlugLinked(false);
        setPipeSlug(value);
    }

    const handlePipeName = (value: string) => {
        setPipeName(value);
        // use the pipe name to create a slug in kebab case
        if (pipeNameSlugLinked) setPipeSlug(value.toLowerCase().replace(/\s+/g, '-'));
    }

    const onEdgeDelete = (deletedEdges: Edge[]) => {
        deletedEdges.forEach((edge) => {
            const targetNode = nodesRef.current.find((node) => edge.target === node.id)
            if (targetNode?.type === "exitNodeEdit") {
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
                const selectedDataIn = prevDataIn.filter((input) => {
                    return `${sourceNode.data.identifier}.${edge.sourceHandle}` !== input
                });
                setNodeSelectedDataIn(targetNode, selectedDataIn);

                const needs = [...targetNode.data.needs];
                const newNeeds = needs.filter((need) => {
                    return need !== sourceNode.data.identifier;
                })

                setNodeNeeds(targetNode, newNeeds);
            }

        })
    }

    const onConnect = (params: Edge | Connection) => {
        if (params.target === params.source) return;
        const targetNode = nodesRef.current.find((node) => node.id === params.target);
        const sourceNode = nodesRef.current.find((node) => node.id === params.source);
        if (!(targetNode && sourceNode)) return;
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
            const dataInIndex = targetNode.data.dataIn.findIndex((input: FieldDescription) => input.name === targetHandle)
            const sourceDataIndex = sourceNodeDataOut.findIndex((input: FieldDescription) => input.name === sourceHandle)
            const dataTypes: string [] = sourceNodeDataOut[sourceDataIndex]?.type;

            if (sourceHandle === null || dataTypes.length === 0) {
                toast("The data must be named and have a type to be connected", {type: "warning"});
                return;
            }
            const allowedTypes: string[] = targetNode.data.dataIn[dataInIndex].type;
            let compatible = false;
            // Check if the source data type is compatible with the target data type
            // by checking if the source data type is a subset of the target data type
            // and has not an extra type not present in the target data type
            for (let i = 0; i < dataTypes.length; i++) {
                if (!allowedTypes.includes(dataTypes[i])) {
                    compatible = false;
                    break;
                }
                compatible = true;
            }

            if (!compatible) {
                toast("Incompatible types", {type: "warning"});
                return;
            }

            if (sourceNode.type !== "entryNodeEdit") {
                const needs = [...targetNode.data.needs];
                needs.push(sourceNode.data.identifier)
                setNodeNeeds(targetNode, needs);
            }
            const selectedDataIn = [...targetNode.data.selectedDataIn];
            const dataSource = sourceNode.type === "entryNodeEdit" ? "pipeline" : sourceNode.data.identifier;
            selectedDataIn[dataInIndex] = `${dataSource}.${params.sourceHandle}`;
            setNodeSelectedDataIn(targetNode, selectedDataIn);
        }

        const data = {condition: "", onAddCondition: onAddCondition, onDeleteCondition: onDeleteCondition}
        const edge = {...params, type: 'editEdge', data};
        setEdges((eds) => addEdge(edge, eds));
    }

    const isValidConnection = ((connection: Connection) => {
        const nodes = nodesRef.current;
        const edges = edgesRef.current;
        const target = nodes.find((node) => node.id === connection.target);
        const source = nodes.find((node) => node.id === connection.source);
        if (!(target && source)) return false;
        const hasCycle = (node: Node, visited = new Set()) => {
            if (visited.has(node.id)) return false;

            visited.add(node.id);

            for (const outgoer of getOutgoers(node, nodes, edges)) {
                if (outgoer.id === connection.source) return true;
                if (hasCycle(outgoer, visited)) return true;
            }
        };

        if (target.id === connection.source) return false;
        if (source.type === "entryNodeEdit" && target.type === "exitNodeEdit") return false;
        // make sure the source is not already connected to the exit node
        const exitNode = nodesRef.current.find((node) => node.type === "exitNodeEdit");
        if (edgesRef.current.find((edge) => {
            return edge.source === source.id && edge.target === exitNode?.id
        })) return false;
        return !hasCycle(target);

    });

    const onAddCondition = (id: string, condition: string) => {
        setEdgeCondition(id, condition);
    }

    const onDeleteCondition = (id: string) => {
        const edge = edgesRef.current.find((edge) => edge.id === id)
        if (!edge) return;

        setEdgeCondition(id, "");
    }

    const setEdgeCondition = (edgeId: string, condition: string) => {
        setEdgesRef.current((edges) =>
            edges.map((edge) => {
                if (edge.id !== edgeId) return edge;

                return {
                    ...edge,
                    data: {
                        ...edge.data,
                        condition: condition,
                    },
                };

            })
        )
    }

    const setNodeSelectedDataIn = (affectedNode: Node, selectedDataIn: string[]) => {
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

    const setNodeNeeds = (affectedNode: Node, needs: string[]) => {
        setNodesRef.current((nds) =>
            nds.map((node) => {
                if (node.id !== affectedNode.id) {
                    return node;
                }

                return {
                    ...node,
                    data: {
                        ...node.data,
                        needs: needs,
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

    const createExitNode = () => {
        const dataOut: FieldDescription[] = [];
        return {
            id: `exit`,
            type: "exitNodeEdit",
            deletable: false,
            data: {
                identifier: "exit",
                dataOut: dataOut,
                label: "pipeline-exit",
            },
            position: {x: 2 * nodeSpacing + nodeWidth + entryNodeMinWidth, y: 200},
        }
    }

    const addServiceNode = (serviceId: string, tags: any[], serviceSlug: string, dataIn: FieldDescription[], dataOut: FieldDescription[]) => {
        let counter = 2;
        const selectedDataIn = new Array<string>(dataIn.length);
        let identifier = serviceSlug
        let label = serviceSlug;
        const doesIdentifierExist = (node: Node) => node.data.identifier === identifier;

        while (nodesRef.current.find(doesIdentifierExist)) {
            identifier = label = `${serviceSlug}-${counter}`;
            counter++;
        }

        const newNode = {
            id: identifier,
            type: "serviceNode",

            position: {
                x: nodeSpacing + entryNodeMinWidth,
                y: 200 + (nodesRef.current.length - 2) * (nodeHeight + nodeSpacing),
            },
            data: {
                identifier: identifier,
                selectedDataIn: selectedDataIn,
                dataIn: dataIn,
                dataOut: dataOut,
                service_slug: serviceSlug,
                serviceId: serviceId,
                tags: tags,
                needs: [],
                label: label
            },
        };
        setNodesRef.current((nodes) => nodes.concat(newNode));
        // find the class "react-flow__controls-fitview" and click it
        const elem = document.querySelector('[title="fit view"]') as HTMLElement;
        if (elem) {
            // wait for the next render cycle to click the button
            setTimeout(() => {
                elem.click();
            }, 0);
        }
    };

    const checkInputsAreConnected = (): boolean => {
        const exitNode = nodesRef.current.find((node) => node.type === "exitNodeEdit");
        const lastEdge = edgesRef.current.find((edge) => edge.target === exitNode?.id);
        if (!lastEdge) return false;
        const allNodes = nodesRef.current.filter((node) => node.type !== "entryNodeEdit" && node.type !== "exitNodeEdit");
        let inputConnected = true;
        allNodes.forEach((node) => {
            node.data.dataIn.forEach((input: FieldDescription) => {
                if (!edgesRef.current.find((edge) => edge.targetHandle === input.name)) inputConnected = false;
            })
        })

        return inputConnected;
    }

    const postPipeline = async () => {
        if (!(await checkPipeline())) return;

        const json = getJSONRepresentation();
        createPipeline(json)
            .then((answer) => {
                if (answer?.errorBody) {
                    toast(`Error: ${answer?.errorBody}`, {type: "error"})
                } else {
                    toast("Pipeline created", {type: "success"})
                    navigateHome();
                }
            })
            .catch(error => {
                console.log("Error creating pipeline: ", error);
            })
    }

    const checkPipeline = async (): Promise<boolean> => {

        if (pipeName === '' || pipeSlug === '' || pipeSummary === '' || pipeDescription === '') {
            toast("The pipeline information must be filled", {type: "warning"})
            return false;
        }

        if (!checkInputsAreConnected()) {
            toast("Invalid: Every service input must be connected", {type: "warning"})
            return false;
        }


        try {
            const json = getJSONRepresentation();

            const answer = await checkPipelineValidity(json);

            if (answer && answer?.valid) {
                toast("Pipeline is valid", {type: "success"});
                return true;
            } else {
                toast(`Invalid: ${answer?.errorBody}`, {type: "warning"});
                return false;
            }
        } catch (error) {
            toast("Could not check validity", {type: "error"})
            console.log("Error checking validity: ", error);
            return false;
        }
    }

    const addRequiredNodes = (queue: string[], index: number) => {
        const node = nodesRef.current.find((nd) => nd.id === queue[index]);
        node?.data.needs.forEach((nodeId: string) => {
            queue.push(nodeId);
        });
    }

    const getJSONRepresentation = (): string => {
        const entryNode = nodesRef.current.find((node) => node.type === "entryNodeEdit");
        const exitNode = nodesRef.current.find((node) => node.type === "exitNodeEdit");
        const lastEdge = edgesRef.current.find((edge) => edge.target === exitNode?.id);

        if (!(entryNode && exitNode && lastEdge)) return "{}";

        const data_in_fields = entryNode?.data.dataIn;
        const data_out_fields = exitNode?.data.dataOut;
        const queue: string[] = [lastEdge!.source];
        let index = 0;

        // Add all nodes in the queue in reverse order of their appearance in the pipeline (allowing duplicates)
        while (index < queue.length) {
            addRequiredNodes(queue, index);
            index++;
        }

        // Sort the node list and reverse their order
        const visited: string [] = [];
        const nodesInStepOrder = queue.reverse().filter((nodeId) => {
            if (visited.includes(nodeId)) return false;
            visited.push(nodeId)
            return true;
        })

        const steps: any[] = []
        const tags: any[] = []
        nodesInStepOrder.forEach((nodeId) => {
            const incomingEdges = edgesRef.current.filter((edge) => edge.target === nodeId)
            let condition: string = "";
            incomingEdges.forEach((edge, _) => {
                if (edge.data.condition !== "")
                    condition = condition === "" ? condition.concat(`(${edge.data.condition})`) : condition.concat(` and  (${edge.data.condition})`)
            })
            const node = nodesRef.current.find((nd) => nd.id === nodeId)
            node?.data.tags.forEach((tag: any) => {
                if (tags.filter((existingTag) => existingTag.acronym === tag.acronym).length === 0) {
                    tags.push(tag);
                }
            })
            condition === "" ?
                steps.push({
                    identifier: node?.data.identifier,
                    needs: node?.data.needs,
                    inputs: node?.data.selectedDataIn,
                    service_slug: node?.data.service_slug
                })
                : steps.push({
                    identifier: node?.data.identifier,
                    needs: node?.data.needs,
                    condition: condition,
                    inputs: node?.data.selectedDataIn,
                    service_slug: node?.data.service_slug
                })

        })

        return JSON.stringify({
            name: pipeName,
            slug: pipeSlug,
            summary: pipeSummary,
            description: pipeDescription,
            data_in_fields: data_in_fields,
            data_out_fields: data_out_fields,
            tags: tags,
            steps: steps
        })
    }

    const itemGrid = () => {
        return (
            <ItemGrid filter={search} orderBy={orderBy} tags={tags} ai={ai}
                      itemFunctions={{addService: addServiceNode}}
                      items={{service: PipelineEditorServiceCard}}
                      handleTags={(event: SelectChangeEvent, newValue: Tag[]) =>
                          handleTags(event, newValue, setTags, searchParams, history, handleNoFilterWrapper)}

                      handleAIToggle={(event: React.ChangeEvent<HTMLInputElement>) =>
                          handleAIToggle(event, setAI, searchParams, history, handleNoFilterWrapper)}
                      paginationPositions={["top"]} paginationOptions={[PerPage['4'], PerPage['12']]}
                      displayedPage={"pipeline-editor"}
            />);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    const MemoizedItemGrid = React.useMemo(() => itemGrid(), [search, orderBy, tags, ai]);

    React.useEffect(() => {
        const onAddEntryInput = (defaultName: string) => {
            const entryNode = nodesRef.current.find((node) => node.type === "entryNodeEdit")
            if (!entryNode) return;
            const dataIn = [...entryNode.data.dataIn];
            const inputField = new FieldDescription();
            inputField.type = [];
            inputField.name = defaultName;
            dataIn.push(inputField);
            setNodeDataIn(entryNode, dataIn);
        }

        const onDeleteEntryInput = (index: number) => {
            const entryNode = nodesRef.current.find((node) => node.type === "entryNodeEdit")
            if (!entryNode) return;
            const dataIn = [...entryNode.data.dataIn];
            dataIn.splice(index, 1)
            setNodeDataIn(entryNode, dataIn)
        }

        const onSelectEntryInput = (inputIndex: number, type: string[]) => {
            const entryNode = nodesRef.current.find((node) => node.type === "entryNodeEdit")
            if (entryNode === undefined) return;

            // remove edges that are connected to the input
            const inputName = entryNode.data.dataIn[inputIndex].name;
            const edgesToRemove = edgesRef.current.filter((edge) => edge.sourceHandle === inputName)
            onEdgeDelete(edgesToRemove);

            // update edges refs to remove the edges
            setEdgesRef.current((edges) => edges.filter((edge) => !edgesToRemove.includes(edge)))

            const dataIn = [...entryNode.data.dataIn];
            dataIn[inputIndex].type = type;
            setNodeDataIn(entryNode, dataIn);
        }
        const updateSelectedInputOption = (affectedNode: Node, newName: string, previousName: string) => {
            const selectedDataIn = affectedNode.data.selectedDataIn.map((option: string) => {
                if (option === previousName) return newName;
                return option;
            })
            setNodeSelectedDataIn(affectedNode, selectedDataIn);
        }
        const onSelectEntryInputName = (inputIndex: number, newName: string, previousName: string) => {
            const entryNode = nodesRef.current.find((node) => node.type === "entryNodeEdit")
            if (entryNode === undefined) return;
            const dataIn = [...entryNode.data.dataIn];
            dataIn[inputIndex].name = newName;
            setNodeDataIn(entryNode, dataIn);

            const initialEdge = edgesRef.current.find((edge) => edge.source === entryNode.id)
            if (initialEdge) {
                // Propagate the name change of the selected input data in the other nodes
                const affectedNodes = edgesRef.current
                    .map((edge) => edge.sourceHandle === previousName ? edge.target : null)
                    .filter((target) => target !== null);


                affectedNodes.forEach((nodeId) => {
                    const affectedNode = nodesRef.current.find((node) => node.id === nodeId)
                    if (affectedNode && affectedNode.type !== "exitNodeEdit")
                        updateSelectedInputOption(affectedNode, `${entryNode.data.identifier}.${newName}`, `${entryNode.data.identifier}.${previousName}`);
                })
            }
            return;
        }

        const createEntryNode = () => {
            const dataIn: FieldDescription[] = [];
            return {
                id: `entry`,
                type: "entryNodeEdit",
                deletable: false,
                data: {
                    onAddEntryInput: onAddEntryInput,
                    onSelectEntryInput: onSelectEntryInput,
                    onSelectEntryInputName: onSelectEntryInputName,
                    onDeleteEntryInput: onDeleteEntryInput,
                    identifier: "entry",
                    dataIn: dataIn,
                    label: "pipeline-entry",
                    minWidth: entryNodeMinWidth,
                },
                position: {x: 50, y: 200},
            }
        }

        const initialNodes: Node[] = []
        initialNodes.push(createEntryNode())
        initialNodes.push(createExitNode())
        setNodes(() => initialNodes);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [setNodes]);

    React.useMemo(() => {
        nodesRef.current = nodes;
        setNodesRef.current = setNodes
        edgesRef.current = edges
        setEdgesRef.current = setEdges
    }, [edges, nodes, setNodes, setEdges])


    return (
        <Box sx={{display: 'flex'}}>
            <ScrollToTop smooth component={<ArrowUpward style={{color: (colorMode === 'light' ? 'white' : 'black')}}
                                                        sx={{paddingTop: '2px'}}/>}/>
            <FilterDrawer
                mobileOpen={mobileOpen} handleOpen={handleOpen}
                orderBy={orderBy} handleOrder={(event: SelectChangeEvent) => {
                handleOrder(event, setOrderBy, searchParams, history)
            }}
                orderByList={orderByList}
                search={search}
                handleSearch={(event: React.ChangeEvent<HTMLInputElement>) => {
                    handleSearch(event, setSearch, searchParams, handleNoFilterWrapper, history)
                }}
                tags={tags}
                handleTags={(event: SelectChangeEvent, newValue: Tag[]) =>
                    handleTags(event, newValue, setTags, searchParams, history, handleNoFilterWrapper)}
                ai={ai}
                handleAIToggle={(event: React.ChangeEvent<HTMLInputElement>) =>
                    handleAIToggle(event, setAI, searchParams, history, handleNoFilterWrapper)}
            />
            <Box component={"main"} sx={{flexGrow: 1, mb: 0}}>
                <Toolbar/>
                <Container sx={{my: 2}} maxWidth={false}>
                    <Grid container spacing={2} justifyContent={"space-between"}
                          sx={{py: isSmartphone() ? 0 : 1}}>
                        <Grid item>
                            <Link to={"/home"} style={{textDecoration: "none"}}>
                                <Button variant={"outlined"} color={"secondary"} startIcon={<ArrowBack/>}>
                                    Back
                                </Button>
                            </Link>
                        </Grid>
                        <Grid item>
                            <URLLink
                                href={"https://docs.swiss-ai-center.ch/tutorials/create-a-pipeline-that-blurs-faces-in-an-image/#create-the-pipeline"}
                                target={"_blank"}>
                                <Button color={"secondary"} variant={"outlined"}
                                        startIcon={<DescriptionTwoTone/>}>
                                    Docs
                                </Button>
                            </URLLink>
                        </Grid>
                    </Grid>
                </Container>
                <Container maxWidth={false} sx={{mb: 3}}>
                    {}
                    {MemoizedItemGrid}
                </Container>
                <Container maxWidth={false}>
                    <Box sx={{
                        height: 500,
                        width: "100%",
                        border: 2,
                        borderRadius: "5px",
                        borderColor: "primary.main"
                    }}
                         mt={1}
                    >
                        <ReactFlowProvider>
                            <BoardEdit
                                nodes={nodes}
                                edges={edges}
                                onConnect={onConnect}
                                onEdgeDelete={onEdgeDelete}
                                isValidConnection={isValidConnection}
                                onNodesChange={onNodesChange}
                                onEdgesChange={onEdgesChange}
                            />
                        </ReactFlowProvider>
                    </Box>
                </Container>
                <Container maxWidth={false}>
                    <Typography variant={"h4"} component={"h2"} my={4}>
                        Pipeline Information
                    </Typography>
                    <Grid container spacing={2} justifyContent={"flex-start"} sx={{height: "100%"}}
                          alignItems={"stretch"}>
                        <Grid container item xs={12} md={6} justifyContent={"flex-start"} spacing={2}
                              alignItems={"stretch"}>
                            <Grid container item spacing={2} justifyContent={"space-between"}>
                                <Grid item xs={12} md={6}>
                                    <TextField variant={"outlined"} sx={{width: "100%"}}
                                               placeholder={"Pipeline Name"} label={"Pipeline Name"}
                                               onChange={(event) => handlePipeName(event.target.value)}>
                                    </TextField>
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <TextField variant={"outlined"} sx={{width: "100%"}}
                                               placeholder={"in kebab case (e.g. pipeline-slug)"}
                                               label={"Pipeline Slug"}
                                               value={pipeSlug}
                                               onChange={(event) => handlePipeSlug(event.target.value)}
                                    >
                                    </TextField>
                                </Grid>
                            </Grid>
                            <Grid xs={12} item alignContent={"flex-end"} flexDirection={"column"}>
                                <TextField sx={{width: "100%"}} variant={"outlined"} multiline rows={2}
                                           placeholder={"Phrase defining the pipeline"} label={"Summary"}
                                           onChange={(event) => setPipeSummary(event.target.value)}>
                                </TextField>
                            </Grid>
                        </Grid>
                        <Grid xs={12} md={6} pl={2} pt={2} container item alignItems={"stretch"}>
                            <Grid item sx={{width: "100%"}} alignItems={"stretch"}>
                                <TextField variant={"outlined"} multiline rows={6} sx={{width: "100%"}}
                                           placeholder={"Full pipeline description (markdown compatible)"}
                                           label={"Description"}
                                           onChange={(event) => setPipeDescription(event.target.value)}>
                                </TextField>
                            </Grid>
                        </Grid>
                    </Grid>
                    <Box sx={{display: 'flex', justifyContent: 'flex-end', width: '100%'}} my={2}>
                        <Button sx={{mr: 2}} color={"secondary"} variant={"contained"}
                                onClick={() => setJsonModalOpen(true)} disableElevation={true}>
                            Show JSON
                        </Button>
                        <Button sx={{mr: 2}} color={"secondary"} variant={"contained"} onClick={checkPipeline}
                                disableElevation={true}>
                            Check Validity
                        </Button>
                        <Button variant={"contained"} onClick={postPipeline} disableElevation={true}>
                            Submit
                        </Button>
                    </Box>
                </Container>
                <Container>
                    <Copyright/>
                </Container>
            </Box>
            <JsonModal trigger={jsonModalOpen} onClose={() => setJsonModalOpen(false)} json={getJSONRepresentation()}/>
        </Box>
    );
}

export default PipelineEditor;
