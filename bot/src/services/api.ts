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
    width?: number | null = 512
    height?: number | null = 512
    num_inference_steps?: number | null = 20
}

async function predict(predictTaskRequest: PredictTaskRequest): Promise<typeof uuidv4> {
    const resp = await http.post<typeof uuidv4>('/predict', predictTaskRequest)
    const data = resp.data;
    return data
}

async function status(submissionId: string): Promise<string> {
    const config: AxiosRequestConfig = {
        params: {
            'submission_id': submissionId
        }
    }
    const resp = await http.get<string>('/status', config)
    const data = resp.data;
    return data
}

async function result(submissionId: string): Promise<Blob> {
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
