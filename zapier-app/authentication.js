// basic Bearer token authentication, mimics Basic auth.
apiKeyAuthentication = {
    type: "custom",
    connectionLabel: "{{connectionLabel}}",
    test: {
        url: "{{process.env.BASE_API_URL}}/zapier/triggers/auth/",
        method: "GET"
    },
    fields: [
        {
            key: "api_key",
            label: "Personal API key",
            helpText: "Your API key is available from your ACME account.",
            required: true
        }
    ]
};

basicAuthentication = {
    type: "Basic",
    connectionLabel: "{{connectionLabel}}",
    test: {
        url: "{{process.env.BASE_API_URL}}/zapier/triggers/auth/",
    }
};

module.exports = {
    apiKeyAuthentication: apiKeyAuthentication,
    basicAuthentication: basicAuthentication
};
