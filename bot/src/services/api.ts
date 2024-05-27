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

async function getTextToImageModels(): Promise<string[]> {
    return await getModels("TextToImageModel")
}

async function getTextToVideoModels(): Promise<string[]> {
    return await getModels("TextToVideoModel")
}

async function getImageToImageModels(): Promise<string[]> {
    return await getModels("ImageToImageModel")
}


async function getModels(schema: string): Promise<string[]> {
    const config: AxiosRequestConfig = {
        timeout: 30 * 1000
    }
    const resp = await http.get<OpenAPIV3_1.Document>('/openapi.json', config)
    const openAPISchema = resp.data
    const schemas = openAPISchema.components?.schemas;
    if (schemas) {
        const schemaObject = schemas[schema];
        if (!schemaObject) return []
        if (schemaObject.enum && schemaObject.enum.length > 0) return schemaObject.enum
        else if (schemaObject.const) return [schemaObject.const]
        return []
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

export interface TextToVideoRequest extends BaseRequest {

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

async function textToVideo(textToVideoRequest: TextToVideoRequest): Promise<typeof uuidv4> {
    let resp
    try {
        resp = await http.post<typeof uuidv4>('/text-to-video', textToVideoRequest)

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
    steps_completed: number,
    position: number
}

interface TextToVideoTask extends TextToVideoRequest {
    task_id: string,
    steps_completed: number,
    position: number
}

interface ImageToImageTask extends ImageToImageRequest {
    task_id: string,
    steps_completed: number,
    position: number
}

async function result(submissionId: typeof uuidv4, extension: string, callback?: () => unknown): Promise<string> {
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
            const status = await http.get('/status', config)
            if (callback) callback()
        } catch (error) {
            if (error instanceof AxiosError && error.response?.status == 303) {
                break
            }
            throw error
        }
    }

    // get result
    const path = `${OUTPUTS_DIR}/${submissionId}${extension}`;
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
    getImageToImageModels,
    getTextToImageModels,
    getTextToVideoModels,
    imageToImage,
    textToImage,
    textToVideo,
    result
}

export default API
