import { RunState } from '../utils/reducers/runStateSlice';
import { Service } from './Service';
import { PipelineExecution } from './PipelineExecution';

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
