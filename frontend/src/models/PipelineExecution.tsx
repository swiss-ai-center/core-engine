import { Pipeline } from './Pipeline';
import { Task } from './Task';

export class PipelineExecution {
    id: string;
    status: string;
    tasks: Task[];
    current_pipeline_step_id: string;
    pipeline: Pipeline;
    pipeline_id: string;
    created_at: string;
    updated_at: string;
}
