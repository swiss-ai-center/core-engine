import { getResult } from './api';
import { toast } from 'react-toastify';

export async function download(resultIdList: string[]) {
    for (const id of resultIdList) {
        const file: any = await getResult(id);
        if (file.file) {
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(file.file);
            link.setAttribute('download', 'result.' + id.split('.')[1]);
            document.body.appendChild(link);
            link.click();
        } else {
            toast(`Error downloading file ${id}: ${file.error}`, {type: "error"});
        }
    }
}

export const isSmartphone = (): boolean => {
    return window.innerWidth < 600;
}


export const displayTimer = (timer: number): string => {
    return timer < 300 ? timer.toFixed(1) + "s" : ">300.0s";
}

export const positionHandle = (handlesLength: number, index: number) => {
    return `${(index / (handlesLength + 1)) * 100}%`;
}
