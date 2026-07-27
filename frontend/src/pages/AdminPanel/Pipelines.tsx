import { DeleteOutline, EditOutlined, SaveOutlined } from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Chip,
    CircularProgress,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    Paper,
    Stack,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Typography,
} from '@mui/material';
import React, { FormEvent, useCallback, useEffect, useState } from 'react';
import { ServiceStatus } from 'enums/serviceStatusEnum';
import { Pipeline } from 'models/Pipeline';
import { deletePipeline, getAllPipelines, updatePipelineMetadata } from 'utils/api';
import { getStoredAuthenticationToken } from 'utils/authentication';

const statusColor = (status: ServiceStatus): 'success' | 'error' | 'warning' | 'default' => {
    if (status === ServiceStatus.AVAILABLE) return 'success';
    if (status === ServiceStatus.UNAVAILABLE) return 'error';
    if (status === ServiceStatus.SLEEPING) return 'warning';
    return 'default';
};

const AdminPipelines: React.FC = () => {
    const [pipelines, setPipelines] = useState<Pipeline[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [pipelineToDelete, setPipelineToDelete] = useState<Pipeline | null>(null);
    const [isDeleting, setIsDeleting] = useState(false);
    const [deleteError, setDeleteError] = useState('');
    const [pipelineToEdit, setPipelineToEdit] = useState<Pipeline | null>(null);
    const [pipelineName, setPipelineName] = useState('');
    const [pipelineSummary, setPipelineSummary] = useState('');
    const [pipelineDescription, setPipelineDescription] = useState('');
    const [isSaving, setIsSaving] = useState(false);
    const [editError, setEditError] = useState('');

    const loadPipelines = useCallback(async () => {
        const token = getStoredAuthenticationToken();
        if (!token) {
            setError('Your session is no longer valid.');
            setIsLoading(false);
            return;
        }

        setError('');
        setIsLoading(true);
        try {
            setPipelines(await getAllPipelines(token));
        } catch (loadError) {
            setError(loadError instanceof Error ? loadError.message : 'Unable to load pipelines.');
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        void loadPipelines();
    }, [loadPipelines]);

    const openDeleteDialog = (pipeline: Pipeline) => {
        setDeleteError('');
        setPipelineToDelete(pipeline);
    };

    const openEditDialog = (pipeline: Pipeline) => {
        setPipelineToEdit(pipeline);
        setPipelineName(pipeline.name);
        setPipelineSummary(pipeline.summary);
        setPipelineDescription(pipeline.description ?? '');
        setEditError('');
    };

    const closeEditDialog = () => {
        if (isSaving) return;
        setPipelineToEdit(null);
        setEditError('');
    };

    const savePipeline = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        if (!pipelineToEdit) return;

        const token = getStoredAuthenticationToken();
        if (!token) {
            setEditError('Your session is no longer valid.');
            return;
        }

        setEditError('');
        setIsSaving(true);
        try {
            const updatedPipeline = await updatePipelineMetadata(token, pipelineToEdit.id, {
                name: pipelineName.trim(),
                summary: pipelineSummary.trim(),
                description: pipelineDescription.trim(),
            });
            setPipelines((currentPipelines) => currentPipelines.map(
                (pipeline) => pipeline.id === updatedPipeline.id ? updatedPipeline : pipeline,
            ));
            setPipelineToEdit(null);
        } catch (updateError) {
            setEditError(updateError instanceof Error ? updateError.message : 'Unable to update this pipeline.');
        } finally {
            setIsSaving(false);
        }
    };

    const closeDeleteDialog = () => {
        if (isDeleting) return;
        setPipelineToDelete(null);
        setDeleteError('');
    };

    const confirmDelete = async () => {
        if (!pipelineToDelete) return;
        const token = getStoredAuthenticationToken();
        if (!token) {
            setDeleteError('Your session is no longer valid.');
            return;
        }

        setDeleteError('');
        setIsDeleting(true);
        try {
            await deletePipeline(token, pipelineToDelete.id);
            setPipelines((currentPipelines) => currentPipelines.filter((pipeline) => pipeline.id !== pipelineToDelete.id));
            setPipelineToDelete(null);
        } catch (deletionError) {
            setDeleteError(deletionError instanceof Error ? deletionError.message : 'Unable to delete this pipeline.');
        } finally {
            setIsDeleting(false);
        }
    };

    return (
        <Box sx={{mt: 1}}>
            <Typography color="text.secondary" sx={{mb: 3}}>
                Review and manage every pipeline, regardless of availability.
            </Typography>

            {error && (
                <Alert
                    severity="error"
                    action={<Button color="inherit" size="small" onClick={loadPipelines}>Retry</Button>}
                    sx={{mb: 3}}
                >
                    {error}
                </Alert>
            )}

            {isLoading ? (
                <Box sx={{display: 'flex', alignItems: 'center', gap: 1.5, py: 4}}>
                    <CircularProgress size={24}/>
                    <Typography color="text.secondary">Loading pipelines…</Typography>
                </Box>
            ) : (
                <TableContainer component={Paper} variant="outlined" elevation={0}>
                    <Table aria-label="Pipelines" sx={{minWidth: 760}}>
                        <TableHead>
                            <TableRow>
                                <TableCell>Name</TableCell>
                                <TableCell>Slug</TableCell>
                                <TableCell>Summary</TableCell>
                                <TableCell>Status</TableCell>
                                <TableCell align="right">Actions</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {pipelines.map((pipeline) => (
                                <TableRow key={pipeline.id} hover>
                                    <TableCell>
                                        <Typography fontWeight={600}>{pipeline.name}</Typography>
                                    </TableCell>
                                    <TableCell>{pipeline.slug}</TableCell>
                                    <TableCell sx={{maxWidth: 380}}>{pipeline.summary || '—'}</TableCell>
                                    <TableCell>
                                        <Chip
                                            label={pipeline.status}
                                            size="small"
                                            color={statusColor(pipeline.status)}
                                            variant="outlined"
                                            sx={{textTransform: 'capitalize', fontWeight: 600}}
                                        />
                                    </TableCell>
                                    <TableCell align="right">
                                        <Stack direction="row" spacing={1} justifyContent="flex-end">
                                            <Button
                                                size="small"
                                                variant="outlined"
                                                startIcon={<EditOutlined/>}
                                                onClick={() => openEditDialog(pipeline)}
                                                sx={{textTransform: 'none'}}
                                            >
                                                Edit
                                            </Button>
                                            <Button
                                                color="error"
                                                size="small"
                                                variant="outlined"
                                                startIcon={<DeleteOutline/>}
                                                onClick={() => openDeleteDialog(pipeline)}
                                                sx={{textTransform: 'none'}}
                                            >
                                                Delete
                                            </Button>
                                        </Stack>
                                    </TableCell>
                                </TableRow>
                            ))}
                            {pipelines.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={5} align="center" sx={{py: 5, color: 'text.secondary'}}>
                                        No pipelines found.
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            )}

            <Dialog open={Boolean(pipelineToEdit)} onClose={closeEditDialog} maxWidth="sm" fullWidth>
                <DialogTitle>
                    Edit pipeline
                    <Typography variant="body2" color="text.secondary" sx={{mt: 0.5}}>
                        Slug: {pipelineToEdit?.slug}
                    </Typography>
                </DialogTitle>
                <Box component="form" onSubmit={savePipeline}>
                    <DialogContent sx={{display: 'grid', gap: 2.5}}>
                        {editError && <Alert severity="error">{editError}</Alert>}
                        <TextField
                            autoFocus
                            required
                            fullWidth
                            label="Title"
                            value={pipelineName}
                            onChange={(event) => setPipelineName(event.target.value)}
                            disabled={isSaving}
                        />
                        <TextField
                            fullWidth
                            label="Summary"
                            value={pipelineSummary}
                            onChange={(event) => setPipelineSummary(event.target.value)}
                            disabled={isSaving}
                        />
                        <TextField
                            fullWidth
                            multiline
                            minRows={4}
                            label="Description"
                            value={pipelineDescription}
                            onChange={(event) => setPipelineDescription(event.target.value)}
                            disabled={isSaving}
                        />
                    </DialogContent>
                    <DialogActions sx={{px: 3, pb: 3}}>
                        <Button color="inherit" onClick={closeEditDialog} disabled={isSaving}>Cancel</Button>
                        <Button
                            type="submit"
                            variant="contained"
                            disabled={isSaving || !pipelineName.trim()}
                            startIcon={isSaving ? <CircularProgress size={16} color="inherit"/> : <SaveOutlined/>}
                        >
                            Save
                        </Button>
                    </DialogActions>
                </Box>
            </Dialog>

            <Dialog open={Boolean(pipelineToDelete)} onClose={closeDeleteDialog} maxWidth="xs" fullWidth>
                <DialogTitle>Delete pipeline?</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        This will permanently delete “{pipelineToDelete?.name}”. This action cannot be undone.
                    </DialogContentText>
                    {deleteError && <Alert severity="error" sx={{mt: 2}}>{deleteError}</Alert>}
                </DialogContent>
                <DialogActions sx={{px: 3, pb: 3}}>
                    <Button color="inherit" onClick={closeDeleteDialog} disabled={isDeleting}>Cancel</Button>
                    <Button
                        color="error"
                        variant="contained"
                        onClick={confirmDelete}
                        disabled={isDeleting}
                        startIcon={isDeleting ? <CircularProgress size={16} color="inherit"/> : <DeleteOutline/>}
                    >
                        Delete
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default AdminPipelines;
