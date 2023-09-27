enum MessageType {
    SUCCESS = 'success',
    ERROR = 'error',
    WARNING = 'warning',
    INFO = 'info',
}

export enum MessageSubject {
    CONNECTION = 'connection',
    EXECUTION = 'execution',
}

class MessageData {
    text: string;
    data: object;
}

export class Message {
    message: MessageData;
    type: MessageType;
    subject: MessageSubject;
}
