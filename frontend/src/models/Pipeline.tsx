import { ExecutionUnit } from 'models/ExecutionUnit';
import { Service } from 'models/Service';

export class PipelineStep {
    id: string;
    identifier: string;
    needs: string[];
    condition: string;
    inputs: string[];
    service_id: string;
    service: Service;
    group_identifier: string | null;
    source_pipeline_slug: string | null;
    source_pipeline: Pipeline | null;
}

export class Pipeline extends ExecutionUnit {
    steps: PipelineStep[];
}
