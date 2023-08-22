import axios, { AxiosRequestConfig } from 'axios';
import { OpenAPIV3_1 } from 'openapi-types'
import { API_URL } from '../constants';
import { v4 as uuidv4 } from 'uuid';

const http = axios.create({
    baseURL: API_URL
})

async function getModels(): Promise<string[]> {
    const resp = await http.get<OpenAPIV3_1.Document>('/openapi.json')
    const openAPISchema = resp.data
    const schemas = openAPISchema.components?.schemas;
    if (schemas) {
        const models = schemas["Model"]["enum"]
        return models as string[]
    } else {
        throw Error("Unable to get models")
    }
}

export class PredictTaskRequest {
    model!: string
    prompt!: string
    width!: number
    height!: number
    num_inference_steps!: number
}

async function predict(predictTaskRequest: PredictTaskRequest): Promise<typeof uuidv4> {
    const resp = await http.post<typeof uuidv4>('/predict', predictTaskRequest)
    const data = resp.data;
    return data
}

export enum PredictTaskStatus {
    PENDING = "PENDING",
    PROCESSING = "PROCESSING",
    COMPLETE = "COMPLETE",
    NOT_FOUND = "NOT FOUND"
}

export type PredictTaskInfo = {
    position: number,
    status: PredictTaskStatus
}

async function status(submissionId: typeof uuidv4): Promise<PredictTaskInfo> {
    const config: AxiosRequestConfig = {
        params: {
            'submission_id': submissionId
        }
    }
    const resp = await http.get<PredictTaskInfo>('/status', config)
    const data = resp.data;
    return data
}

async function result(submissionId: typeof uuidv4): Promise<Blob> {
    const config: AxiosRequestConfig = {
        params: {
            'submission_id': submissionId
        }
    }
    const resp = await http.get<Blob>('/result', config)
    const data = resp.data;
    return data
}

const API = {
    getModels,
    predict,
    result,
    status
}

export default API
