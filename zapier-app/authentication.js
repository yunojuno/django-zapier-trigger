// basic Bearer token authentication

module.exports = {
    type: "custom",
    connectionLabel: "{{connectionLabel}}",
    test: {
        headers: {
            "Content-Type": "application/json"
        },
        url: "{{process.env.BASE_API_URL}}/zapier/auth/",
        method: "POST",
        body: {
            api_key: "{{bundle.authData.api_key}}",
            email: "{{bundle.authData.email}}"
        }
    },
    fields: [
        {
            key: "email",
            label: "Email address",
            helpText: "The email address that you use to log in to ACME.",
            required: true
        },
        {
            key: "api_key",
            label: "Personal API key",
            helpText: "Your API key is available from your ACME account.",
            required: true
        }
    ],
    customConfig: {}
};
