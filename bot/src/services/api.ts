import axios, { AxiosRequestConfig } from 'axios';
import { Readable } from 'stream'
import fs from 'fs'
import { OpenAPIV3_1 } from 'openapi-types';
import { v4 as uuidv4 } from 'uuid';
import { API_URL, OUTPUTS_DIR } from '../constants';
import { BufferResolvable } from 'discord.js';
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

async function result(submissionId: typeof uuidv4): Promise<BufferResolvable> {
    const path = `${OUTPUTS_DIR}/${submissionId}.png`;

    const config: AxiosRequestConfig = {
        params: {
            'submission_id': submissionId
        },
        responseType: 'stream'
    }
    const { data } = await http.get<Readable>('/result', config)
    const writeStream = fs.createWriteStream(path)
    const stream = data.pipe(writeStream)
    await new Promise(resolve => stream.on('finish', resolve))
    return path
}

const API = {
    getModels,
    predict,
    result,
    status
}

export default API
