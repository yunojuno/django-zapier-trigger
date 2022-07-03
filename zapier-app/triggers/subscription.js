// generic functions supporting RestHook operations

// Run when the hook triggers - by default this is a noop, but it could
// be used to filter / inspect the payload. It's a closure just to keep
// it consistent with all of the other functions - it's not required.
const doPerform = (hook) => {
    const performHook = async (z, bundle) => {
        return [bundle.cleanedRequest];
    };
    return performHook;
};

// Run when the user creates a new Zap that subscribes to the hook
// event. The hook name is passed in from the trigger configuration, and
// passed through on the subsbscribe URL.
const doSubscribe = (hook) => {
    const subscribeHook = (z, bundle) => {
        const options = {
            url: `${process.env.BASE_API_URL}/zapier/hooks/${hook}/subscribe/`,
            method: "POST",
            body: {
                // targetUrl is the Zapier URL to which event payloads
                // will be posted. It is stored along with the
                // subscription.
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
        };
        return z.request(options).then((response) => {
            response.throwForStatus();
            return response.json;
        });
    };
    return unsubscribeHook;
};

const doList = (hook) => {
    const listHook = (z, bundle) => {
        z.console.log(`Requesting list for hook: ${hook}`);
        const options = {
            url: `${process.env.BASE_API_URL}/zapier/hooks/${hook}/list/`,
            method: "GET",
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
