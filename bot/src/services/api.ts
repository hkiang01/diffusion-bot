import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';
import { Readable } from 'stream'
import fs from 'fs'
import { OpenAPIV3_1 } from 'openapi-types';
import { v4 as uuidv4 } from 'uuid';
import { API_URL, OUTPUTS_DIR } from '../constants';
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

export type PredictTaskRequest = {
    model: string,
    prompt: string,
    width: number,
    height: number,
    num_inference_steps: number
}

async function predict(predictTaskRequest: PredictTaskRequest): Promise<typeof uuidv4> {
    const resp = await http.post<typeof uuidv4>('/predict', predictTaskRequest)
    const data = resp.data;
    return data
}


interface PredictTask extends PredictTaskRequest {
    task_id: string,
}

export enum PredictTaskStage {
    PENDING = "PENDING",
    PROCESSING = "PROCESSING",
    COMPLETE = "COMPLETE",
    NOT_FOUND = "NOT FOUND"
}

export class PredictTaskState {
    predict_task!: PredictTask
    stage!: PredictTaskStage
    percent_complete!: number
    position!: number
}

async function status(submissionId: typeof uuidv4): Promise<AxiosResponse<PredictTaskState | string>> {
    const config: AxiosRequestConfig = {
        maxRedirects: 0,
        params: {
            'task_id': submissionId
        }
    }
    return await http.get<PredictTaskState | string>('/status', config)
}

async function result(submissionId: typeof uuidv4): Promise<string> {
    const path = `${OUTPUTS_DIR}/${submissionId}.png`;

    const config: AxiosRequestConfig = {
        params: {
            'task_id': submissionId
        },
        responseType: 'stream'
    }
    const { data } = await http.get<Readable>('/result', config)
    const writeStream = fs.createWriteStream(path)
    const stream = data.pipe(writeStream)
    await new Promise(resolve => stream.on('finish', resolve))
    return path
}

async function deleteResult(submissionId: typeof uuidv4): Promise<void> {
    const config: AxiosRequestConfig = {
        params: {
            'task_id': submissionId
        },
        responseType: 'stream'
    }
    await http.delete<Readable>('/result', config)
}

const API = {
    deleteResult,
    getModels,
    predict,
    result,
    status
}

export default API
