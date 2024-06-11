import { RunState } from '../utils/reducers/runStateSlice';
import { PipelineExecution } from './PipelineExecution';
import { Service } from './Service';

export class Task {
    id: string;
    status: string;
    data_in: string[];
    data_out: string[];
    service: Service;
    service_id: string;
    pipeline_execution?: PipelineExecution;
    pipeline_execution_id?: string;
    general_status?: RunState;
    created_at: string;
    updated_at: string;
}
