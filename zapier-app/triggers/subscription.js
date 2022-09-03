// generic functions supporting RestHook operations

const headers = (z, bundle) => {
    return {
        "Content-Type": "application/json",
        Accept: "application/json",
        Authorization: `Bearer ${bundle.authData.api_key}`
    };
};

const doPerform = async (z, bundle) => {
    return [bundle.cleanedRequest];
};

const doSubscribe = (hook) => {
    const subscribeHook = (z, bundle) => {
        const options = {
            url: `${process.env.BASE_API_URL}/zapier/hooks/${hook}/subscribe/`,
            method: "POST",
            headers: headers(z, bundle),
            body: {
                hookUrl: bundle.targetUrl
            }
        };
        return z.request(options).then((response) => {
            response.throwForStatus();
            return response.json;
        });
    };
    return subscribeHook;
};

const doUnsubscribe = (hook) => {
    const unsubscribeHook = (z, bundle) => {
        const options = {
            url: `${process.env.BASE_API_URL}/zapier/hooks/${hook}/unsubscribe/${bundle.subscribeData.id}/`,
            method: "DELETE",
            headers: headers(z, bundle)
        };
        return z.request(options).then((response) => {
            response.throwForStatus();
            return response.json;
        });
    };
    return unsubscribeHook
}

const doList = (hook) => {
    const listHook = (z, bundle) => {
        z.console.log(`Requesting list for hook: ${hook}`);
        const options = {
            url: `${process.env.BASE_API_URL}/zapier/hooks/${hook}/list/`,
            method: "GET",
            headers: headers(z, bundle)
        };
        return z.request(options).then((response) => {
            response.throwForStatus();
            return response.json;
        });
    };
    return listHook;
};

module.exports = {
    perform: doPerform,
    subscribe: doSubscribe,
    unsubscribe: doUnsubscribe,
    list: doList
};
