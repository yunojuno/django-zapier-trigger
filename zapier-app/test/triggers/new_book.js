require("should");

const zapier = require("zapier-platform-core");

const App = require("../../index");
const appTester = zapier.createAppTester(App);

describe("Trigger - new_book", () => {
    zapier.tools.env.inject();

    it("should get an array", async () => {
        const bundle = {
            authData: {
                api_key: process.env.API_KEY
            },

            inputData: {}
        };

        const results = await appTester(App.triggers["new_book"].operation.perform, bundle);
        results.should.be.an.Array();
    });
});
