import { ExecutionUnit } from 'models/ExecutionUnit';
import { Service } from 'models/Service';

export class PipelineStep {
    identifier: string;
    needs: string[];
    condition: string;
    inputs: string[];
    service_id: string;
    service: Service;
}

export class Pipeline extends ExecutionUnit {
    steps: PipelineStep[];
}
