import { ExecutionUnit } from 'models/ExecutionUnit';
import { ServiceAccessLevel } from 'enums/serviceAccessLevelEnum';

export class Service extends ExecutionUnit {
    url: string;
    docs_url: string;
    has_ai: boolean;
    access_level: ServiceAccessLevel;
}
