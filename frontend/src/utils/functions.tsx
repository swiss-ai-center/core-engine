import { getResult } from './api';
import { toast } from 'react-toastify';
import { Tag } from "../models/Tag";
import { SelectChangeEvent } from "@mui/material";
import React from "react";

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
    if (handlesLength === 0) return '50%';
    return `${(index / (handlesLength + 1)) * 100}%`;
}


export const handleTags = (
    _: SelectChangeEvent,
    newValue: Tag[],
    setTags: React.Dispatch<React.SetStateAction<Tag[]>>,
    searchParams: URLSearchParams,
    windowHistory: History,
    handleNoFilter: any
) => {
    setTags(newValue);
    if (newValue.length === 0) {
        searchParams.delete('tags');
    } else {
        searchParams.delete('tags');
        newValue.forEach((tag) => {
            searchParams.append('tags', tag.acronym);
        });
    }
    windowHistory.pushState({}, '', `?${searchParams.toString()}`);
    handleNoFilter();
};

export const handleAIToggle = (
    event: React.ChangeEvent<HTMLInputElement>,
    setAI: React.Dispatch<React.SetStateAction<boolean>>,
    searchParams: URLSearchParams,
    windowHistory: History,
    handleNoFilter: any
) => {
    setAI(event.target.checked);
    if (event.target.checked) {
        searchParams.set('ai', 'true');
    } else {
        searchParams.delete('ai');
    }
    windowHistory.pushState({}, '', `?${searchParams.toString()}`);
    handleNoFilter();
};

export const handleSearch = (
    event: React.ChangeEvent<HTMLInputElement>,
    setSearch: React.Dispatch<React.SetStateAction<string>>,
    searchParams: URLSearchParams,
    handleNoFilter: any,
    windowHistory: History) => {
    setSearch(event.target.value);
    if (event.target.value === '') {
        searchParams.delete('filter');
    } else {
        searchParams.set('filter', event.target.value);
    }
    windowHistory.pushState({}, '', `?${searchParams.toString()}`);
    handleNoFilter();
};

const orderByList = [
    {value: 'name-asc', label: 'Name (A-Z)'},
    {value: 'name-desc', label: 'Name (Z-A)'}
]
export const handleOrder = (event: SelectChangeEvent, setOrderBy: any, searchParams: URLSearchParams, windowHistory: History) => {
    setOrderBy(event.target.value as string);
    if (event.target.value === orderByList[0].value) {
        searchParams.delete('orderBy');
    } else {
        searchParams.set('orderBy', event.target.value as string);
    }
    windowHistory.pushState({}, '', `?${searchParams.toString()}`);
    handleNoFilter(searchParams, windowHistory);
}

export const handleNoFilter = (
    searchParams: URLSearchParams,
    windowHistory: History) => {
    if (searchParams.toString() === '') {
        windowHistory.pushState({}, '', window.location.pathname);
    }
}



