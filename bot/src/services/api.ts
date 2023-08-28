import axios, { AxiosError, AxiosRequestConfig } from 'axios';
import fs from 'fs';
import wait from 'node:timers/promises';
import { OpenAPIV3_1 } from 'openapi-types';
import { Readable } from 'stream';
import { v4 as uuidv4 } from 'uuid';
import { API_URL, OUTPUTS_DIR } from '../constants';

const http = axios.create({
    baseURL: API_URL
})

async function getModels(): Promise<string[]> {
    const config: AxiosRequestConfig = {
        timeout: 30 * 1000
    }
    const resp = await http.get<OpenAPIV3_1.Document>('/openapi.json', config)
    const openAPISchema = resp.data
    const schemas = openAPISchema.components?.schemas;
    if (schemas) {
        const models = schemas["Model"]["enum"]
        return models as string[]
    } else {
        throw Error("Unable to get models")
    }
}

export type BaseRequest = {
    model: string,
    prompt: string,
    num_inference_steps?: number

}

export interface TextToImageRequest extends BaseRequest {
    width: number,
    height: number,
}

export interface ImageToImageRequest extends BaseRequest {
    image_url: string
    strength?: number
    guidance_scale?: number
}

async function textToImage(textToImageRequest: TextToImageRequest): Promise<typeof uuidv4> {
    let resp
    try {
        resp = await http.post<typeof uuidv4>('/text-to-image', textToImageRequest)

    } catch (error) {
        if (error instanceof AxiosError && error.response?.status == 422) {
            throw Error(JSON.stringify(error.response.data))
        } else {
            throw error
        }
    }
    const data = resp.data;
    return data
}

async function imageToImage(imageToImageRequest: ImageToImageRequest): Promise<typeof uuidv4> {
    let resp
    try {
        resp = await http.post<typeof uuidv4>('/image-to-image', imageToImageRequest)

    } catch (error) {
        if (error instanceof AxiosError && error.response?.status == 422) {
            throw Error(JSON.stringify(error.response.data))
        } else {
            throw error
        }
    }
    const data = resp.data;
    return data
}


interface TextToImageTask extends TextToImageRequest {
    task_id: string,
}

export enum TaskStage {
    PENDING = "PENDING",
    PROCESSING = "PROCESSING",
    COMPLETE = "COMPLETE",
    NOT_FOUND = "NOT FOUND"
}

export class TaskState {
    task!: TextToImageTask
    stage!: TaskStage
    steps_completed!: number
    position!: number
}


async function result(submissionId: typeof uuidv4, callback?: (state: TaskState) => unknown): Promise<string> {
    const config: AxiosRequestConfig = {
        maxRedirects: 0,
        params: {
            'task_id': submissionId
        }
    }

    // poll for duration of prediction
    // eslint-disable-next-line no-constant-condition
    while (true) {
        await wait.setTimeout(4000);
        try {
            const state = await http.get<TaskState>('/status', config)
            if (callback) callback(state.data)
        } catch (error) {
            if (error instanceof AxiosError && error.response?.status == 303) {
                break
            }
            throw error
        }
    }

    // get result
    const path = `${OUTPUTS_DIR}/${submissionId}.png`;
    config.responseType = 'stream'
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
    imageToImage,
    textToImage,
    result
}

export default API
