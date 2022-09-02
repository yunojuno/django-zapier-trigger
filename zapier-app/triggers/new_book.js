const perform = async (z, bundle) => {
    return [bundle.cleanedRequest];
};

const performSubscribe = async (z, bundle) => {
    const options = {
        url: "{{process.env.BASE_API_URL}}/zapier/hooks/subscribe/",
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer {{bundle.authData.api_key}}"
        },
        body: {
            hookUrl: bundle.targetUrl,
            hookScope: "new_book"
        }
    };
    return z.request(options).then((response) => {
        response.throwForStatus();
        return response.json;
    });
};

const performUnsubscribe = async (z, bundle) => {
    const options = {
        url: "{{process.env.BASE_API_URL}}/zapier/hooks/unsubscribe/",
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer {{bundle.authData.api_key}}"
        }
    };
    return z.request(options).then((response) => {
        response.throwForStatus();
        return response.json;
    });
};

module.exports = {
    operation: {
        perform: perform,
        type: "hook",
        performSubscribe: performSubscribe,
        performUnsubscribe: performUnsubscribe,
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
        label: "New Book",
        description: "Triggers when a book is published.",
        hidden: false,
        important: false
    }
};
