const headers = (z, bundle) => {
    return {
        "Content-Type": "application/json",
        Accept: "application/json",
        Authorization: `Bearer ${bundle.authData.api_key}`
    };
};

const doPerform = (event) => {
    const polling = (z, bundle) => {
        const options = {
            url: `${process.env.BASE_API_URL}/zapier/triggers/${event}/`,
            method: "GET",
            headers: headers(z, bundle)
        };
        return z.request(options).then((response) => {
            response.throwForStatus();
            return response.json;
        });
    };
    return polling;
};

module.exports = {
    perform: doPerform
};
