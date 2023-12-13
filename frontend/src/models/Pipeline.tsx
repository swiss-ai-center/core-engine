import { ExecutionUnit } from './ExecutionUnit';

export class PipelineStep {
    identifier: string;
    needs: string[];
    condition: string;
    inputs: string[];
    service_id: string;
}

export class Pipeline extends ExecutionUnit {
    steps: PipelineStep[];
}
