// Core functions for supporting triggers.

// Run when the hook triggers - by default this is a noop, but it could
// be used to filter / inspect the payload. It's a closure just to keep
// it consistent with all of the other functions - it's not required.
const doPerform = (trigger) => {
    const performHook = async (z, bundle) => {
        z.console.log(`Processing inbound request for trigger '${trigger}'.`);
        return [bundle.cleanedRequest];
    };
    return performHook;
};

// Run when the user creates a new Zap that subscribes to the hook
// event. The hook name is passed in from the trigger configuration, and
// passed through on the subsbscribe URL.
const doSubscribe = (trigger) => {
    const subscribeHook = (z, bundle) => {
        z.console.log(
            `Creating webhook subscription for trigger '${trigger}'.`
        );
        const options = {
            url: `${process.env.BASE_API_URL}/zapier/triggers/${trigger}/subscriptions/`,
            method: "POST",
            body: {
                // targetUrl is the Zapier URL to which event payloads
                // will be posted. It is stored along with the
                // subscription.
                hookUrl: bundle.targetUrl,
                zapId: bundle.meta.zap.id
            }
        };
        return z.request(options).then((response) => {
            response.throwForStatus();
            return response.json;
        });
    };
    return subscribeHook;
};

const doUnsubscribe = (trigger) => {
    const unsubscribeHook = (z, bundle) => {
        z.console.log(`Deleting subscription for trigger '${trigger}'.`);
        const options = {
            url: `${process.env.BASE_API_URL}/zapier/triggers/${trigger}/subscriptions/${bundle.subscribeData.id}/`,
            method: "DELETE"
        };
        return z.request(options).then((response) => {
            response.throwForStatus();
            return response.json;
        });
    };
    return unsubscribeHook;
};

const doList = (trigger) => {
    const listHook = (z, bundle) => {
        z.console.log(`Requesting data for trigger '${trigger}'.`);
        const options = {
            url: `${process.env.BASE_API_URL}/zapier/triggers/${trigger}/`,
            method: "GET",
            params: {sample: bundle.meta.isLoadingSample}
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
    poll: doList,
    sample: doList
};
