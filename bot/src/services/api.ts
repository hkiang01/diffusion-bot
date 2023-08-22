import axios from 'axios';
import { OpenAPIV3_1 } from 'openapi-types'
import { API_URL } from '../constants';

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

const API = {
    getModels
}

export default API
