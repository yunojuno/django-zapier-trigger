const perform = async (z, bundle) => {
    return [bundle.cleanedRequest];
};

const performSubscribe = async (z, bundle) => {
    const options = {
        url: "{{process.env.BASE_API_URL}}/zapier/hooks/subscribe/",
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            "X-API-TOKEN": bundle.authData.api_key
        },
        params: {},
        body: {
            hookUrl: bundle.targetUrl,
            hookScope: "approved_timesheet"
        }
    };

    return z.request(options).then((response) => {
        response.throwForStatus();
        const results = response.json;

        // You can do any parsing you need for results here before returning them

        return results;
    });
};

module.exports = {
    operation: {
        perform: perform,
        type: "hook",
        performSubscribe: performSubscribe,
        performUnsubscribe: {
            body: { hookUrl: "{{bundle.targetUrl}}" },
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
                "X-API-TOKEN": "{{bundle.authData.api_key}}"
            },
            method: "DELETE",
            url: "{{process.env.BASE_API_URL}}/zapier/hooks/unsubscribe/{{bundle.subscribeData.id}}"
        },
        sample: {
            id: "123456",
            authorName: "Arthur Conan Doyle",
            bookTitle: "Hound of the Baskervilles",
            publishedYear: 1902
        }
    },
    key: "new_book",
    noun: "Book",
    display: {
        label: "Ne Book",
        description: "Triggers when a book is published.",
        hidden: false,
        important: false
    }
};
