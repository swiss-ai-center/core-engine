import ItemGrid from "../../components/ItemGrid/ItemGrid";
import {Box, Button, Container, SelectChangeEvent} from "@mui/material";
import {Tag} from "../../models/Tag";
import React, {useCallback, useEffect} from "react";
import {useSearchParams} from "react-router-dom";
import ReactFlow, {
    addEdge,
    Background,
    Connection,
    Controls,
    Node,
    Edge,
    ReactFlowProvider,
    useEdgesState,
    useNodesState
} from "react-flow-renderer";
import Board from "../../components/Board/Board";
import {useReactFlow} from "reactflow";
import {ArrowUpward} from "@mui/icons-material";
import ScrollToTop from "react-scroll-to-top";
import {useSelector} from "react-redux";
import EntryNode from "../../components/Board/EntryNode";
import ProgressNode from "../../components/Board/ProgressNode";
import ExitNode from "../../components/Board/ExitNode";
import EntryNodeEdit from "../../components/Nodes/EntryNodeEdit";
import {FieldDescription} from "../../models/ExecutionUnit";
import ServiceNode from "../../components/Nodes/ServiceNode";

let id = 0;
const getId = () => `${id++}`;

const CreatePipeline: React.FC<{ mobileOpen: boolean }> = (
    {
        mobileOpen,
    }) => {

    const orderByList = [
        {value: 'name-asc', label: 'Name (A-Z)'},
        {value: 'name-desc', label: 'Name (Z-A)'},
    ];

    const nodeTypes = React.useMemo(() => ({
        entryNodeEdit: EntryNodeEdit, serviceNode: ServiceNode, exitNode: ExitNode
    }), []);
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [search, setSearch] = React.useState('');
    const [orderBy, setOrderBy] = React.useState(orderByList[0].value);
    const [tags, setTags] = React.useState<Tag[]>([]);
    const [ai, setAI] = React.useState(false);
    const [searchParams] = useSearchParams();
    //const { getNodes, getEdges } = useReactFlow();
    const history = window.history;
    const handleNoFilter = () => {
        if (searchParams.toString() === '') {
            history.pushState({}, '', window.location.pathname);
        }
    }
    const handleTags = (event: SelectChangeEvent, newValue: Tag[]) => {
        setTags(newValue);
        if (newValue.length === 0) {
            searchParams.delete('tags');
        } else {
            searchParams.delete('tags');
            newValue.forEach((tag) => {
                searchParams.append('tags', tag.acronym);
            });
        }
        history.pushState({}, '', `?${searchParams.toString()}`);
        handleNoFilter();
    }

    const handleAIToggle = (event: React.ChangeEvent<HTMLInputElement>) => {
        setAI(event.target.checked);
        if (event.target.checked) {
            searchParams.set('ai', 'true');
        } else {
            searchParams.delete('ai');
        }
        history.pushState({}, '', `?${searchParams.toString()}`);
        handleNoFilter();
    }

    const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSearch(event.target.value);
        if (event.target.value === '') {
            searchParams.delete('filter');
        } else {
            searchParams.set('filter', event.target.value);
        }
        history.pushState({}, '', `?${searchParams.toString()}`);
        handleNoFilter();
    };

    const onConnect = useCallback (
        (params: Edge<any> | Connection) => {
            if ('source' in params) {
                const sourceNode = nodes.find((node) => node.id === params.source);
                if (sourceNode && 'data' in sourceNode) {
                    const dataIn = sourceNode.data.dataIn;
                    console.log(dataIn); // Use the dataIn array as needed
                }
            }
            return setEdges((eds) => addEdge(params, eds))
        },
        [nodes,edges],
    );


    React.useEffect(() => {
        // Call the addInitialNodes function here
        setNodes((nodes) => nodes.concat(createEntryNode()));
    }, [setNodes]);

    const createEntryNode = () => {
        return {
            id: "entry",
            type: "entryNodeEdit",
            data: {
                label: "entry",
            },
            position: {x: 0, y: 0},
        }
    }

    const addServiceNode = (serviceName: string) => {
        const id = getId();
        const newNode = {
            id,
            type: "serviceNode",
            position: {
                x: 150,
                y: 150,
            },
            data: {
                label: `${serviceName}`
            },
        };
        setNodes((nodes) => nodes.concat(newNode));
    };


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
                                nodeTypes={nodeTypes}
                                onConnect={onConnect}
                            >
                                <Controls />
                                <Background  gap={12} size={1} />
                            </ReactFlow>
                        </ReactFlowProvider>
                    </Box>
                </Container>
                <Container>
                    <Button onClick={() => addServiceNode("None")}>
                        New node
                    </Button>
                </Container>
                <Container maxWidth={false}>
                    <ItemGrid filter={search} orderBy={orderBy} tags={tags} handleTags={handleTags}
                              ai={ai} handleAIToggle={handleAIToggle} addService={addServiceNode}/>
                </Container>
            </Box>
        </Box>
    );
}

export default CreatePipeline;