import API from '../../../src/services/api'

describe("API", () => {
    test("It should get API models", async () => {
        const models = await API.getTextToImageModels();
        // expect(models.length).toBeGreaterThan(0);
    })
})
